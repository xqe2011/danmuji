import { z, type ZodSchema } from "zod";
import { Logger } from "tslog";
import crypto from "crypto";

const StartSchema = z.object({
  code: z.string(),
});

const GameIdSchema = z.object({
  game_id: z.string(),
});

const WebsocketUrlSchema = z.object({
  game_id: z.string(),
  url: z.string(),
  signature: z.string(),
});

const StartSuccessDataSchema = z.object({
  game_info: z.object({
    game_id: z.string(),
  }),
  websocket_info: z.object({
    auth_body: z.string(),
    wss_link: z.array(z.string()),
  }),
  anchor_info: z.object({
    room_id: z.number().int(),
    uname: z.string(),
    uface: z.string(),
    uid: z.number().int(),
    open_id: z.string(),
    union_id: z.string(),
  }),
});

const DefaultResponseSchema = z.object({
  code: z.number().int(),
  message: z.string(),
  data: z.unknown(),
});

const StartResponseSchema = DefaultResponseSchema.extend({
  data: z.union([StartSuccessDataSchema, z.object({}).strict()]),
});

const ConfigSchema = z.object({
  ACCESS_KEY_ID: z.string(),
  ACCESS_KEY_SECRET: z.string(),
  APP_ID: z.coerce.number(),
  WEBSOCKET_URL: z.string(),
});

const config = ConfigSchema.parse(process.env);
const logger = new Logger({ hideLogPositionForProduction: true });

async function hmac(data: string) {
  return crypto.createHmac("sha256", config.ACCESS_KEY_SECRET).update(data).digest("hex");
}

async function requestBiliAPI<T>(responseSchema: ZodSchema<T>, path: string, body: unknown) {
  const bodyStr = JSON.stringify(body);
  const contentMd5 = crypto.createHash("md5").update(bodyStr).digest("hex");
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const nonce = crypto.randomUUID();

  const authHeaders = {
    "x-bili-accesskeyid": config.ACCESS_KEY_ID,
    "x-bili-content-md5": contentMd5,
    "x-bili-signature-method": "HMAC-SHA256",
    "x-bili-signature-nonce": nonce,
    "x-bili-signature-version": "1.0",
    "x-bili-timestamp": timestamp
  };

  const response = await fetch("https://live-open.biliapi.com" + path, {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": await hmac(Object.entries(authHeaders).map(([key, value]) => `${key}:${value}`).join("\n")),
      ...authHeaders,
    },
    body: bodyStr,
  });
  if (response.status !== 200) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return responseSchema.parse(await response.json());
}

const routes: Record<string, (clientIP: string, body: unknown, query?: Record<string, unknown>, request?: Request, server?: Bun.Server<unknown>) => Promise<Response | undefined>> = {
  "/v2/app/start": async (clientIP, body, query, request, server) => {
    const req = StartSchema.parse(body);
    const data = await requestBiliAPI(StartResponseSchema, "/v2/app/start", { code: req.code, app_id: config.APP_ID });
    data.data.websocket_info.wss_link = await Promise.all(data.data.websocket_info.wss_link.map(async (url) => {
      return config.WEBSOCKET_URL +
        "?game_id=" + data.data.game_info.game_id +
        "&url=" + encodeURIComponent(url) +
        "&signature=" + await hmac(";,'\"[!]" + `${url}, ${data.data.game_info.game_id}, ${clientIP}`);
    }));
    if (data.data.game_info !== undefined) {
      logger.info(`[/v2/app/start] ${req.code} -> code=${data.code} uid=${data.data.anchor_info.uid} rid=${data.data.anchor_info.room_id} gid=${data.data.game_info.game_id}`);
    } else {
      logger.info(`[/v2/app/start] ${req.code} -> code=${data.code} msg=${data.message}`);
    }
    return Response.json(data, { status: 200 });
  },

  "/v2/app/end": async (clientIP, body, query, request, server) => {
    const req = GameIdSchema.parse(body);
    const data = await requestBiliAPI(DefaultResponseSchema, "/v2/app/end", { game_id: req.game_id, app_id: config.APP_ID });
    logger.info(`[/v2/app/end] ${req.game_id} -> code=${data.code} msg=${data.message}`);
    return Response.json(data, { status: 200 });
  },

  "/v2/app/heartbeat": async (clientIP, body, query, request, server) => {
    const req = GameIdSchema.parse(body);
    const data = await requestBiliAPI(DefaultResponseSchema, "/v2/app/heartbeat", { game_id: req.game_id });
    logger.info(`[/v2/app/heartbeat] ${req.game_id} -> code=${data.code} msg=${data.message}`);
    return Response.json(data, { status: 200 });
  },
  "/sub": async (clientIP, body, query, request, server) => {
    const req = WebsocketUrlSchema.parse(query);
    if (await hmac(";,'\"[!]" + `${req.url}, ${req.game_id}, ${clientIP}`) !== req.signature) {
      logger.warn(`[/sub] ${clientIP} -> status=403, msg=Invalid URL Signature`);
      return Response.json({ error: "Invalid URL Signature" }, { status: 403 });
    }
    
    logger.info(`[/sub] ${req.game_id} -> Connecting to ${req.url}`);
    /* 打开连接 */
    const client = new WebSocket(req.url);
    await new Promise((resolve) => {
      client!.onopen = () => {
        resolve(0);
      };
    });
    if (server!.upgrade(request!, {data: { gameID: req.game_id, client }})) {
      return;
    }
    return Response.json({ error: "Internal Server Error" }, { status: 500 });
  },
};

Bun.serve({
  port: 3000,
  async fetch(req, server) {
    const clientIP = req.headers.get("X-Forwarded-For") ?? req.headers.get("X-Real-IP") ?? req.headers.get("CF-Connecting-IP") ?? req.headers.get("Remote-Addr") ?? req.headers.get("Host") ?? "unknown";
    const url = new URL(req.url);
    const handler = routes[url.pathname];

    if (!handler) return new Response("Not Found", { status: 404 });
    let body: unknown;
    if (url.pathname !== "/sub") {
      if (req.method !== "POST") {
        logger.warn(`[${url.pathname}] ${clientIP} -> status=405, msg=Method Not Allowed`);
        return new Response("Method Not Allowed", { status: 405 });
      }
  
      try {
        body = await req.json();
      } catch {
        logger.warn(`[${url.pathname}] ${clientIP} -> status=400, msg=Invalid JSON`);
        return Response.json({ error: "Invalid JSON" }, { status: 400 });
      }
    }

    try {
      const response = await handler(clientIP, body, url.searchParams.toJSON(), req, server);
      return response;
    } catch (err) {
      if (err instanceof z.ZodError) {
        logger.warn(`[${url.pathname}] ${clientIP} -> status=400, msg=Schema Validation Error`);
        return Response.json({ error: z.treeifyError(err) }, { status: 400 });
      }
      logger.error(`[${url.pathname}] ${clientIP} -> status=500, msg=Internal Server Error`);
      logger.trace(err);
      return Response.json({ error: "Internal Server Error" }, { status: 500 });
    }
  },
  websocket: {
    idleTimeout: 40,
    data: {} as {client?: WebSocket, gameID?: string, url: string},
    async open(ws) {
      ws.data.client!.onmessage = (message) => {
        if (ws.readyState !== WebSocket.OPEN) return;
        ws.send(message.data);
        logger.info(`[WebSocket] ${ws.data.gameID} -> Forwarded message to client`);
      };
      ws.data.client!.onclose = () => {
        logger.info(`[WebSocket] ${ws.data.gameID} -> Upstream closed`);
        ws.close(1000);
      };
      logger.info(`[WebSocket] ${ws.data.gameID} -> Opened`);
    },
    message(ws, message) {
      /* 只允许透过AUTH包和心跳包 */
      if (typeof message === "string" || message.length < 16 || (message.at(11) !== 0x02 && message.at(11) !== 0x07)) {
        logger.warn(`[WebSocket] ${ws.data.gameID} -> Invalid message`);
        return;
      }
      ws.data.client?.send(message);
      logger.info(`[WebSocket] ${ws.data.gameID} -> Forwarded message to upstream`);
    },
    close(ws, code, reason) {
      logger.info(`[WebSocket] ${ws.data.gameID} -> Connection lost`);
      routes["/v2/app/end"]!("localhost", { game_id: ws.data.gameID! }).then(() => {
        logger.info(`[WebSocket] ${ws.data.gameID} -> Game closed`);
      }).catch((err) => {
        logger.error(`[WebSocket] ${ws.data.gameID} -> Error closing game: ${err}`);
      });
    },
  }
});

logger.info("Server running on http://localhost:3000");
