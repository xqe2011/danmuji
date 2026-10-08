/**
 * Shared helpers for open-server-compatible EdgeOne Edge Functions.
 * Env (Makers): ACCESS_KEY_ID, ACCESS_KEY_SECRET, APP_ID
 * WEBSOCKET_* is intentionally omitted — EdgeOne does not support WebSocket yet.
 */

function uint8ArrayToHex(arr) {
  return Array.prototype.map
    .call(arr, (x) => (`0${x.toString(16)}`).slice(-2))
    .join("");
}

export function getConfig(env) {
  const ACCESS_KEY_ID = env?.ACCESS_KEY_ID;
  const ACCESS_KEY_SECRET = env?.ACCESS_KEY_SECRET;
  const APP_ID_RAW = env?.APP_ID;

  if (!ACCESS_KEY_ID || !ACCESS_KEY_SECRET || APP_ID_RAW === undefined || APP_ID_RAW === "") {
    throw new ConfigError("Missing required env: ACCESS_KEY_ID, ACCESS_KEY_SECRET, APP_ID");
  }

  const APP_ID = Number(APP_ID_RAW);
  if (!Number.isFinite(APP_ID)) {
    throw new ConfigError("APP_ID must be a number");
  }

  return { ACCESS_KEY_ID, ACCESS_KEY_SECRET, APP_ID };
}

export class ConfigError extends Error {
  constructor(message) {
    super(message);
    this.name = "ConfigError";
  }
}

export class ValidationError extends Error {
  constructor(error) {
    super("Schema Validation Error");
    this.name = "ValidationError";
    this.error = error;
  }
}

export function getClientIP(request) {
  return (
    request?.eo?.clientIp ||
    request.headers.get("X-Forwarded-For")?.split(",")[0]?.trim() ||
    request.headers.get("X-Real-IP") ||
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("Remote-Addr") ||
    request.headers.get("Host") ||
    "unknown"
  );
}

export async function hmacSha256Hex(secret, data) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(data));
  return uint8ArrayToHex(new Uint8Array(signature));
}

export async function md5Hex(data) {
  const buffer = await crypto.subtle.digest(
    { name: "MD5" },
    new TextEncoder().encode(data),
  );
  return uint8ArrayToHex(new Uint8Array(buffer));
}

export async function requestBiliAPI(config, path, body) {
  const bodyStr = JSON.stringify(body);
  const contentMd5 = await md5Hex(bodyStr);
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const nonce = crypto.randomUUID();

  const authHeaders = {
    "x-bili-accesskeyid": config.ACCESS_KEY_ID,
    "x-bili-content-md5": contentMd5,
    "x-bili-signature-method": "HMAC-SHA256",
    "x-bili-signature-nonce": nonce,
    "x-bili-signature-version": "1.0",
    "x-bili-timestamp": timestamp,
  };

  const authorization = await hmacSha256Hex(
    config.ACCESS_KEY_SECRET,
    Object.entries(authHeaders)
      .map(([key, value]) => `${key}:${value}`)
      .join("\n"),
  );

  const response = await fetch(`https://live-open.biliapi.com${path}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      Authorization: authorization,
      ...authHeaders,
    },
    body: bodyStr,
  });

  if (response.status !== 200) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}

export async function parseJsonBody(request) {
  try {
    return await request.json();
  } catch {
    return null;
  }
}

export function requireStringField(body, field) {
  if (body === null || typeof body !== "object" || Array.isArray(body)) {
    throw new ValidationError({ error: "Invalid JSON body" });
  }
  const value = body[field];
  if (typeof value !== "string" || value.length === 0) {
    throw new ValidationError({ [field]: "Required string" });
  }
  return value;
}

export async function handlePost(context, pathname, handler) {
  const { request, env } = context;
  const clientIP = getClientIP(request);

  if (request.method !== "POST") {
    console.warn(`[${pathname}] ${clientIP} -> status=405, msg=Method Not Allowed`);
    return new Response("Method Not Allowed", { status: 405 });
  }

  const body = await parseJsonBody(request);
  if (body === null) {
    console.warn(`[${pathname}] ${clientIP} -> status=400, msg=Invalid JSON`);
    return Response.json({ error: "Invalid JSON" }, { status: 400 });
  }

  try {
    const config = getConfig(env);
    return await handler({ request, env, config, clientIP, body });
  } catch (err) {
    if (err instanceof ValidationError) {
      console.warn(`[${pathname}] ${clientIP} -> status=400, msg=Schema Validation Error`);
      return Response.json({ error: err.error }, { status: 400 });
    }
    if (err instanceof ConfigError) {
      console.error(`[${pathname}] ${clientIP} -> status=500, msg=${err.message}`);
      return Response.json({ error: "Internal Server Error" }, { status: 500 });
    }
    console.error(`[${pathname}] ${clientIP} -> status=500, msg=Internal Server Error`);
    console.error(err);
    return Response.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
