addEventListener("fetch", event => {
  const url = new URL(event.request.url);

  if (url.pathname === "/api/data") {
    const data = {
      data: [
        { id: 1, name: "Sample Item 1", value: 100 },
        { id: 2, name: "Sample Item 2", value: 200 },
        { id: 3, name: "Sample Item 3", value: 300 },
      ],
      total: 3,
      timestamp: new Date().toISOString(),
    };
    return event.respondWith(
      new Response(JSON.stringify(data), {
        headers: { "Content-Type": "application/json" },
      })
    );
  }

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Customer Hub</title>
</head>
<body>
  <h1>Customer Hub</h1>
  <p>API: <a href="/api/data">/api/data</a></p>
</body>
</html>`;

  return event.respondWith(
    new Response(html, {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    })
  );
});
