import { z, type ZodSchema } from "zod";
import { Logger } from "tslog";
import crypto from "crypto";

const StartSchema = z.object({
  code: z.string(),
});

const GameIdSchema = z.object({
  game_id: z.string(),
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
  APP_ID: z.coerce.number()
});

const config = ConfigSchema.parse(process.env);
const logger = new Logger({ hideLogPositionForProduction: true });

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

  const authStr = Object.entries(authHeaders).map(([key, value]) => `${key}:${value}`).join("\n");
  const signature = crypto.createHmac("sha256", config.ACCESS_KEY_SECRET).update(authStr).digest("hex");

  const response = await fetch("https://live-open.biliapi.com" + path, {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": signature,
      ...authHeaders,
    },
    body: bodyStr,
  });
  if (response.status !== 200) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return responseSchema.parse(await response.json());
}

const routes: Record<string, (body: unknown) => Response | Promise<Response>> = {
  "/v2/app/start": async (body) => {
    const req = StartSchema.parse(body);
    const data = await requestBiliAPI(StartResponseSchema, "/v2/app/start", { code: req.code, app_id: config.APP_ID });
    if (data.data.game_info !== undefined) {
      logger.info(`[/v2/app/start] ${req.code} -> code=${data.code} uid=${data.data.anchor_info.uid} rid=${data.data.anchor_info.room_id} gid=${data.data.game_info.game_id}`);
    } else {
      logger.info(`[/v2/app/start] ${req.code} -> code=${data.code} msg=${data.message}`);
    }
    return Response.json(data, { status: 200 });
  },

  "/v2/app/end": async (body) => {
    const req = GameIdSchema.parse(body);
    const data = await requestBiliAPI(DefaultResponseSchema, "/v2/app/end", { game_id: req.game_id, app_id: config.APP_ID });
    logger.info(`[/v2/app/end] ${req.game_id} -> code=${data.code} msg=${data.message}`);
    return Response.json(data, { status: 200 });
  },

  "/v2/app/heartbeat": async (body) => {
    const req = GameIdSchema.parse(body);
    const data = await requestBiliAPI(DefaultResponseSchema, "/v2/app/heartbeat", { game_id: req.game_id });
    logger.info(`[/v2/app/heartbeat] ${req.game_id} -> code=${data.code} msg=${data.message}`);
    return Response.json(data, { status: 200 });
  },
};

Bun.serve({
  port: 3000,
  async fetch(req) {
    const clientIP = req.headers.get("X-Forwarded-For") ?? req.headers.get("X-Real-IP") ?? req.headers.get("CF-Connecting-IP") ?? req.headers.get("Remote-Addr") ?? req.headers.get("Host") ?? "unknown";
    const url = new URL(req.url);
    const handler = routes[url.pathname];

    if (!handler) return new Response("Not Found", { status: 404 });
    if (req.method !== "POST") {
      logger.warn(`[${url.pathname}] ${clientIP} -> status=405, msg=Method Not Allowed`);
      return new Response("Method Not Allowed", { status: 405 });
    }

    let body: unknown;
    try {
      body = await req.json();
    } catch {
      logger.warn(`[${url.pathname}] ${clientIP} -> status=400, msg=Invalid JSON`);
      return Response.json({ error: "Invalid JSON" }, { status: 400 });
    }

    try {
      const response = await handler(body);
      return response;
    } catch (err) {
      if (err instanceof z.ZodError) {
        logger.warn(`[${url.pathname}] ${clientIP} -> status=400, msg=Schema Validation Error`);
        return Response.json({ error: z.treeifyError(err) }, { status: 400 });
      }
      logger.error(`[${url.pathname}] ${clientIP} -> status=500, msg=Internal Server Error`);
      return Response.json({ error: "Internal Server Error" }, { status: 500 });
    }
  },
});

logger.info("Server running on http://localhost:3000");
