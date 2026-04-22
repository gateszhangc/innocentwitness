const http = require("http");
const fs = require("fs");
const path = require("path");

const host = process.env.HOSTNAME || "0.0.0.0";
const port = Number(process.env.PORT || 3000);
const root = __dirname;

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".jpg": "image/jpeg",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".txt": "text/plain; charset=utf-8",
  ".ttf": "font/ttf",
  ".webmanifest": "application/manifest+json; charset=utf-8",
  ".webp": "image/webp",
  ".xml": "application/xml; charset=utf-8"
};

const send = (response, statusCode, headers, body) => {
  response.writeHead(statusCode, headers);
  response.end(body);
};

const serveFile = (requestPath, response) => {
  const safePath = path.normalize(requestPath).replace(/^(\.\.[/\\])+/, "");
  const resolvedPath = path.join(root, safePath);

  if (!resolvedPath.startsWith(root)) {
    send(response, 403, { "Content-Type": "text/plain; charset=utf-8" }, "Forbidden");
    return;
  }

  fs.readFile(resolvedPath, (error, body) => {
    if (error) {
      if (error.code === "ENOENT") {
        send(response, 404, { "Content-Type": "text/plain; charset=utf-8" }, "Not Found");
        return;
      }

      send(response, 500, { "Content-Type": "text/plain; charset=utf-8" }, "Internal Server Error");
      return;
    }

    const ext = path.extname(resolvedPath).toLowerCase();
    const cacheControl = ext === ".html" ? "no-cache" : "public, max-age=31536000, immutable";

    send(
      response,
      200,
      {
        "Cache-Control": cacheControl,
        "Content-Type": contentTypes[ext] || "application/octet-stream",
        "X-Content-Type-Options": "nosniff"
      },
      body
    );
  });
};

const server = http.createServer((request, response) => {
  const url = new URL(request.url || "/", `http://${request.headers.host || "localhost"}`);
  let pathname = decodeURIComponent(url.pathname);

  if (pathname === "/healthz") {
    send(response, 200, { "Content-Type": "application/json; charset=utf-8" }, JSON.stringify({ ok: true }));
    return;
  }

  if (pathname === "/") {
    pathname = "/index.html";
  }

  serveFile(pathname, response);
});

server.listen(port, host, () => {
  console.log(`Static site listening on http://${host}:${port}`);
});
