export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === "/api/data") {
      return new Response(JSON.stringify({
        data: [
          { id: 1, name: "Sample Item 1", value: 100 },
          { id: 2, name: "Sample Item 2", value: 200 },
          { id: 3, name: "Sample Item 3", value: 300 },
        ],
        total: 3,
        timestamp: new Date().toISOString(),
      }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    const asset = await env.ASSETS.fetch(request);
    return new Response(asset.body, {
      headers: asset.headers,
    });
  }
};
