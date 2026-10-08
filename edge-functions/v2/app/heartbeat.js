import {
  handlePost,
  requestBiliAPI,
  requireStringField,
} from "../../shared/common.js";

export async function onRequest(context) {
  return handlePost(context, "/v2/app/heartbeat", async ({ config, body }) => {
    const game_id = requireStringField(body, "game_id");
    const data = await requestBiliAPI(config, "/v2/app/heartbeat", { game_id });
    console.log(`[/v2/app/heartbeat] ${game_id} -> code=${data.code} msg=${data.message}`);
    return Response.json(data, { status: 200 });
  });
}
