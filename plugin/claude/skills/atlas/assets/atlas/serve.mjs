#!/usr/bin/env node
/**
 * Serves the atlas without a dev server of your own: `node tools/atlas/serve.mjs <config> [port]`,
 * then open http://localhost:<port>/atlas/. Same server code as the Vite plugin.
 */
import { createServer } from "node:http";
import { createAtlasServer, ENTRY, send } from "./server.mjs";

const [configFile, port = "4848"] = process.argv.slice(2);
if (!configFile) {
  console.error("usage: serve.mjs <path to atlas.config.mjs> [port]");
  process.exit(1);
}
const handle = await createAtlasServer(configFile);
// A page on another origin can point its own name at 127.0.0.1 and read what this serves, so only our own host names get an answer.
const hosts = new Set([`localhost:${port}`, `127.0.0.1:${port}`]);
createServer((req, res) => {
  if (!hosts.has(req.headers.host)) {
    res.statusCode = 403;
    res.end("Unknown host");
    return;
  }
  const result =
    req.method === "GET" || req.method === "HEAD" ? handle(req.url.split(/[?#]/)[0]) : null;
  if (result) send(req, res, result);
  else {
    res.statusCode = 404;
    res.end("Not found");
  }
}).listen(Number(port), "127.0.0.1", () => console.log(`http://localhost:${port}${ENTRY}`));
