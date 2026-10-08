import {
  handlePost,
  requestBiliAPI,
  requireStringField,
} from "../../shared/common.js";

export async function onRequest(context) {
  return handlePost(context, "/v2/app/start", async ({ config, clientIP, body }) => {
    const code = requireStringField(body, "code");
    const data = await requestBiliAPI(config, "/v2/app/start", {
      code,
      app_id: config.APP_ID,
    });

    // EdgeOne does not support WebSocket yet, so wss_link is left as returned by Bilibili
    // (same behaviour as open-server with WEBSOCKET_ENABLE=false).

    if (data?.data?.game_info !== undefined) {
      console.log(
        `[/v2/app/start] ${code} -> code=${data.code} uid=${data.data.anchor_info.uid} rid=${data.data.anchor_info.room_id} gid=${data.data.game_info.game_id}`,
      );
    } else {
      console.log(`[/v2/app/start] ${code} -> code=${data.code} msg=${data.message}`);
    }

    return Response.json(data, { status: 200 });
  });
}
