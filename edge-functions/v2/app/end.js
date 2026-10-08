import {
  handlePost,
  jsonResponse,
  requestBiliAPI,
  requireStringField,
} from "../../shared/common.js";

export async function onRequest(context) {
  return handlePost(context, "/v2/app/end", async ({ config, body }) => {
    const game_id = requireStringField(body, "game_id");
    const data = await requestBiliAPI(config, "/v2/app/end", {
      game_id,
      app_id: config.APP_ID,
    });
    console.log(`[/v2/app/end] ${game_id} -> code=${data.code} msg=${data.message}`);
    return jsonResponse(data, 200);
  });
}
