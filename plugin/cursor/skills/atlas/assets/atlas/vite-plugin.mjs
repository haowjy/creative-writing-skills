/**
 * Dev only: the atlas, served at /atlas/ by the dev server. The production
 * build never includes it (`apply: "serve"`). `configFile` is the project's atlas.config.mjs.
 */
import { createAtlasServer, send } from "./server.mjs";

/** @param {string} configFile @returns {import("vite").Plugin} */
export function atlasPlugin(configFile) {
  return {
    name: "atlas",
    apply: "serve",
    async configureServer(server) {
      const handle = await createAtlasServer(configFile);
      server.middlewares.use((req, res, next) => {
        const result =
          req.url && (req.method === "GET" || req.method === "HEAD")
            ? handle(req.url.split(/[?#]/)[0])
            : null;
        if (result) send(req, res, result);
        else next();
      });
    },
  };
}
