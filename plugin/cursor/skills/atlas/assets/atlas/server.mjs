/**
 * The viewer's server side, for any dev server: what a request path under `/atlas/` gets.
 *   /atlas/                  index.html
 *   /atlas/<engine file>     js/, styles/page.css, vendor/ of this directory
 *   /atlas/atlas.config.mjs    the project's config file, whatever it is called on disk
 *   /atlas/tokens.css        the project's colours, built from its token files (tokens.mjs)
 *   /atlas/repo/<path>       a repo file as text (or an image), or a directory as JSON
 * Repo paths are served only if git tracks them (or, for the pages directory, lists them as
 * new and not ignored), so `.env`, ignored files and `node_modules` are never served; a symlink
 * is followed only if its target would be served too. Read-only, GET and HEAD.
 */
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { globRegExp } from "./js/pages.js";
import { readTokens, tokenSource } from "./tokens.mjs";

export const ENTRY = "/atlas/";
const ENGINE_DIR = path.dirname(fileURLToPath(import.meta.url));

const ENGINE_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
};
const TEXT_TYPES = { ".md": "text/markdown; charset=utf-8", ".css": "text/css; charset=utf-8" };
const IMAGE_TYPES = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
};
/** Engine files the browser may load; the example, check and server code stay out. */
const ENGINE_FILES = /^\/(?:index\.html|js\/[\w.-]+\.js|styles\/page\.css|vendor\/[\w.-]+\.css)$/;
const REFRESH_MS = 2000;

/**
 * Loads the config at `configFile` and returns `handle(rawPath) → Response`, a plain
 * { status, headers, file?, body? } the caller writes. `rawPath` is the request path without its query.
 */
export async function createAtlasServer(configFile) {
  const config = (
    await import(
      /* @vite-ignore */ `${pathToFileURL(path.resolve(configFile)).href}?t=${Date.now()}`
    )
  ).default;
  const root = fs.realpathSync(path.resolve(path.dirname(configFile), config.root ?? "."));
  const docs = (config.docs ?? []).map(globRegExp);
  const pagesDir = config.pagesDir;

  let listed = { at: 0, files: new Set(), dirs: new Map() };
  /** Tracked files, plus untracked unignored ones under the pages directory so a new page opens before it is added. */
  function tracked() {
    if (Date.now() - listed.at < REFRESH_MS) return listed;
    const git = (...args) =>
      execFileSync("git", args, { cwd: root, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 })
        .split("\0")
        .filter(Boolean);
    const files = new Set([
      ...git("ls-files", "-z"),
      ...git("ls-files", "-z", "--others", "--exclude-standard", "--", pagesDir),
    ]);
    const dirs = new Map();
    for (const file of files) {
      const parts = file.split("/");
      for (let i = 1; i < parts.length; i++) {
        const dir = parts.slice(0, i).join("/");
        if (!dirs.has(dir)) dirs.set(dir, new Map());
        dirs.get(dir).set(parts[i], i + 1 < parts.length);
      }
    }
    listed = { at: Date.now(), files, dirs };
    return listed;
  }

  const showable = (repoPath) =>
    config.serveSource !== false ||
    repoPath.startsWith(`${pagesDir}/`) ||
    docs.some((re) => re.test(repoPath));
  const reject = {
    status: 403,
    headers: { "content-type": "text/plain; charset=utf-8" },
    body: "Not served",
  };
  const missing = {
    status: 404,
    headers: { "content-type": "text/plain; charset=utf-8" },
    body: "Not found",
  };
  const hardened = { "cache-control": "no-cache", "x-content-type-options": "nosniff" };

  function repoResponse(repoPath) {
    const { files, dirs } = tracked();
    if (!showable(repoPath) && !dirs.has(repoPath)) return missing;
    if (dirs.has(repoPath) && !files.has(repoPath)) {
      const entries = [...dirs.get(repoPath)]
        .filter(([name, dir]) =>
          dir
            ? config.serveSource !== false ||
              [...files].some((f) => f.startsWith(`${repoPath}/${name}/`) && showable(f))
            : showable(`${repoPath}/${name}`),
        )
        .map(([name, dir]) => ({ name, dir }))
        .sort((a, b) => Number(b.dir) - Number(a.dir) || a.name.localeCompare(b.name));
      if (!showable(repoPath) && !entries.length) return missing;
      return {
        status: 200,
        headers: { ...hardened, "content-type": "application/json; charset=utf-8" },
        body: JSON.stringify(entries),
      };
    }
    if (!files.has(repoPath)) return missing;
    // A symlink must not lead out of the repo or to a file that isn't served.
    let real;
    try {
      real = fs.realpathSync(path.join(root, repoPath));
    } catch {
      return missing;
    }
    const realPath = path.relative(root, real).split(path.sep).join("/");
    if (
      real !== root &&
      (/^\.\.(\/|$)/.test(realPath) || !files.has(realPath) || !showable(realPath))
    )
      return reject;
    if (!fs.statSync(real).isFile()) return missing;
    const image = IMAGE_TYPES[path.extname(repoPath).toLowerCase()];
    // Text is served as plain text (Markdown as Markdown, CSS for the viewer's stylesheet link), never as HTML or SVG, and sandboxed.
    const type = image ?? TEXT_TYPES[path.extname(repoPath)] ?? "text/plain; charset=utf-8";
    if (!image && isBinary(real))
      return {
        status: 415,
        headers: { "content-type": "text/plain; charset=utf-8" },
        body: "Not a text file",
      };
    return {
      status: 200,
      headers: { ...hardened, "content-type": type, "content-security-policy": "sandbox" },
      file: real,
    };
  }

  function tokenSheet() {
    let css;
    try {
      const source = tokenSource(config, root);
      ({ css } = readTokens(source.root, source.tokens));
    } catch (error) {
      return {
        status: 500,
        headers: { "content-type": "text/plain; charset=utf-8" },
        body: `The token files didn't read: ${error.message}`,
      };
    }
    return {
      status: 200,
      headers: { ...hardened, "content-type": ENGINE_TYPES[".css"] },
      body: css,
    };
  }

  return function handle(rawPath) {
    let pathname;
    try {
      pathname = decodeURIComponent(rawPath);
    } catch {
      return reject;
    }
    if (pathname === ENTRY.slice(0, -1)) return { status: 302, headers: { location: ENTRY } };
    if (!pathname.startsWith(ENTRY)) return null;
    // A path that climbs, or hides a separator, is refused whatever it names.
    if (/(^|\/)\.\.?(\/|$)|\\|\0/.test(pathname)) return reject;
    const rest = pathname.slice(ENTRY.length - 1);
    if (rest === "/") return engineFile("/index.html");
    if (rest === "/atlas.config.mjs")
      return {
        status: 200,
        headers: { ...hardened, "content-type": ENGINE_TYPES[".mjs"] },
        file: path.resolve(configFile),
      };
    if (rest === "/tokens.css") return tokenSheet();
    if (rest.startsWith("/repo/")) {
      const repoPath = rest.slice("/repo/".length).replace(/\/$/, "");
      return repoPath ? repoResponse(repoPath) : missing;
    }
    return ENGINE_FILES.test(rest) ? engineFile(rest) : missing;
  };
}

/**
 * The page's scripts come from itself and the pinned CDN, so a script or handler inside rendered Markdown
 * (`<img onerror>`) never runs. Inline styles stay allowed: Mermaid and React Flow set them.
 */
const PAGE_CSP = [
  "default-src 'none'",
  "script-src 'self' https://cdn.jsdelivr.net",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  "connect-src 'self'",
  "base-uri 'none'",
  "form-action 'none'",
  "frame-ancestors 'none'",
].join("; ");

function engineFile(rest) {
  const headers = {
    "cache-control": "no-cache",
    "x-content-type-options": "nosniff",
    "content-type": ENGINE_TYPES[path.extname(rest)] ?? "text/plain",
  };
  if (rest === "/index.html") headers["content-security-policy"] = PAGE_CSP;
  return { status: 200, headers, file: path.join(ENGINE_DIR, rest) };
}

/** A NUL byte in the first 8 KB: the file is not text. */
function isBinary(file) {
  const fd = fs.openSync(file, "r");
  try {
    const buffer = Buffer.alloc(8192);
    return buffer.subarray(0, fs.readSync(fd, buffer, 0, buffer.length, 0)).includes(0);
  } finally {
    fs.closeSync(fd);
  }
}

/** Writes a handle() response to a Node response. */
export function send(req, res, result) {
  res.statusCode = result.status;
  for (const [name, value] of Object.entries(result.headers)) res.setHeader(name, value);
  if (result.file && req.method !== "HEAD") {
    const stream = fs.createReadStream(result.file);
    // The file can vanish between the check and the read.
    stream.on("error", () => res.destroy());
    stream.pipe(res);
  } else res.end(req.method === "HEAD" ? undefined : result.body);
}
