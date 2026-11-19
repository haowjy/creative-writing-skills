/**
 * The real import graph of the source under the paths the map names, for check.mjs. Reads
 * source text, not types: it sees `import`/`export ... from`/dynamic `import()`/`require()` and a stylesheet's `@import`,
 * resolves relative paths, the configured aliases and workspace package names (`name[/sub]` through the
 * package's `exports`, else `main`, to the file it names), and follows re-exports (`export * from`,
 * `export { x } from`) to the files an import really reaches. Test files are
 * left out (with `test-support` directories and files): the map describes what the code does, not what its tests reach into.
 */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, posix } from "node:path";

const SOURCE = /\.(?:[cm]?[jt]s|tsx|jsx|css)$/;
const TEST =
  /\.(?:test|spec)\.[cm]?[jt]sx?$|\.d\.ts$|(?:^|\/)(?:__tests__|tests?|e2e|fixtures|test-support)\/|[^/]*test-support[^/]*$/;
const SKIP_DIRS = new Set(["node_modules", ".git", "dist", ".output", ".nitro", ".tanstack"]);
const EXTENSIONS = [
  "",
  ".ts",
  ".tsx",
  ".js",
  ".mjs",
  ".mts",
  ".cjs",
  ".jsx",
  "/index.ts",
  "/index.tsx",
  "/index.js",
];

const STATEMENTS = [
  // import a, { b } from "x" / import type ... from "x" / export ... from "x"
  /\b(import|export)\s+(type\s+)?([\w$*{},\s]*?)\s*\bfrom\s*["']([^"']+)["']/g,
  // import "x"
  /\bimport\s*["']([^"']+)["']/g,
  // import("x"), require("x")
  /\b(?:import|require)\s*\(\s*["'`]([^"'`]+)["'`]\s*\)/g,
];
// @import "x" in a stylesheet
const CSS_IMPORT = /@import\s+["']([^"']+)["']/g;

/** The text with comments blanked, so a commented-out import doesn't count. */
function withoutComments(source, isCss) {
  const noBlocks = source.replace(/\/\*[\s\S]*?\*\//g, "");
  return isCss ? noBlocks : noBlocks.replace(/(^|[^:"'`\w])\/\/.*$/gm, "$1");
}

/** `{ a, type B, c as d }` → [{ name: "a", as: "a", type: false }, { name: "B", ..., type: true }, ...]. */
function nameList(list) {
  return list
    .slice(1, list.lastIndexOf("}"))
    .split(",")
    .map((n) => n.trim())
    .filter(Boolean)
    .map((n) => {
      const type = /^type\s/.test(n);
      const [name, as = name] = n.replace(/^type\s+/, "").split(/\s+as\s+/);
      return { name, as, type };
    });
}

/**
 * The module specifiers a file imports: [{ spec, typeOnly, reexport, names, ns }]. `reexport` is an
 * `export ... from`; `names` the braced names it takes ([{ name, as, type }]), or null for all of the
 * module (a default, a namespace, `export *`, a side-effect or dynamic import); `ns` the name an
 * `export * as ns from` gives it.
 */
function specifiersIn(source, isCss) {
  const text = withoutComments(source, isCss);
  if (isCss)
    return [...text.matchAll(CSS_IMPORT)].map((m) => ({
      spec: m[1],
      typeOnly: false,
      reexport: false,
      names: null,
    }));
  const found = [];
  for (const m of text.matchAll(STATEMENTS[0])) {
    const list = m[3].trim();
    // `D`, `D, { x }`: a default import takes the name `default`. `* as ns` (alone or after a default) takes all of it.
    const [, defaultName, rest = ""] = /^([\w$]+)\s*(?:,\s*([\s\S]*))?$/.exec(list) ?? [];
    const names = list.startsWith("{")
      ? nameList(list)
      : defaultName && defaultName !== "type" && !rest.startsWith("*")
        ? [{ name: "default", as: defaultName, type: false }, ...(rest ? nameList(rest) : [])]
        : null;
    const typeOnly = Boolean(m[2]) || (names?.length > 0 && names.every((n) => n.type));
    const ns = /^\*\s+as\s+([\w$]+)$/.exec(list)?.[1];
    found.push({ spec: m[4], typeOnly, reexport: m[1] === "export", names, ns });
  }
  for (const pattern of STATEMENTS.slice(1))
    for (const m of text.matchAll(pattern))
      found.push({ spec: m[1], typeOnly: false, reexport: false, names: null });
  return found;
}

const DECLARATION =
  /\bexport\s+(?:declare\s+)?(?:default\s+)?(?:abstract\s+)?(?:async\s+)?(?:function\s*\*?|class|const|let|var|type|interface|enum|namespace)\s+([\w$]+)/g;
const LOCAL_EXPORT = /\bexport\s+(?:type\s+)?(\{[^}]*\})(?!\s*from)/g;

/** The names a file declares itself: `export const x`, `export { a as b }` (no `from`). */
function declaredIn(source) {
  const text = withoutComments(source, false);
  const names = new Set([...text.matchAll(DECLARATION)].map((m) => m[1]));
  for (const m of text.matchAll(LOCAL_EXPORT)) for (const n of nameList(m[1])) names.add(n.as);
  if (/\bexport\s+default\b/.test(text)) names.add("default");
  return names;
}

/** Source files under a repo-relative directory or file, tests excluded. */
function sourceFiles(repo, path, out) {
  const full = join(repo, path);
  if (!existsSync(full)) return;
  if (statSync(full).isFile()) {
    if (SOURCE.test(path) && !TEST.test(path)) out.add(path);
    return;
  }
  for (const entry of readdirSync(full, { withFileTypes: true })) {
    if (SKIP_DIRS.has(entry.name)) continue;
    const child = posix.join(path, entry.name);
    if (entry.isDirectory()) sourceFiles(repo, child, out);
    else if (SOURCE.test(entry.name) && !TEST.test(child)) out.add(child);
  }
}

/** The source files (tests excluded) under the repo-relative `roots`. */
export function sourceFilesUnder(repo, roots) {
  const files = new Set();
  for (const root of roots) sourceFiles(repo, root, files);
  return files;
}

/** Package name → { dir, exports, main }, for the workspace directories that hold a package.json. */
function packageInfo(repo, workspaceDirs) {
  return new Map(
    workspaceDirs.map((dir) => {
      const pkg = JSON.parse(readFileSync(join(repo, dir, "package.json"), "utf8"));
      return [pkg.name, { dir, exports: pkg.exports, main: pkg.module ?? pkg.main }];
    }),
  );
}

/** Package name → directory, for the workspace directories that hold a package.json. */
export function workspacePackages(repo, workspaceDirs) {
  return new Map([...packageInfo(repo, workspaceDirs)].map(([name, { dir }]) => [name, dir]));
}

/** The file an `exports` value names: a string, else the first usable condition (`import`, `default`, `types`). */
function exportTarget(value) {
  if (typeof value === "string") return value;
  if (!value || typeof value !== "object") return null;
  for (const condition of ["import", "default", "types"]) {
    const found = exportTarget(value[condition]);
    if (found) return found;
  }
  return null;
}

/** The path inside a package that `sub` ("." or "./x") names through its `exports` (wildcards included), else its `main`. */
function packageEntry({ exports, main }, sub) {
  if (exports === undefined) return sub === "." && main ? main : null;
  const map =
    typeof exports === "string" || !Object.keys(exports).some((k) => k.startsWith("."))
      ? { ".": exports }
      : exports;
  if (map[sub] !== undefined) return exportTarget(map[sub]);
  for (const [key, value] of Object.entries(map)) {
    const [head, tail] = key.split("*");
    if (tail === undefined || !sub.startsWith(head) || !sub.endsWith(tail)) continue;
    const target = exportTarget(value);
    if (target) return target.replace("*", sub.slice(head.length, sub.length - tail.length));
  }
  return null;
}

/**
 * Imports out of the source under `roots` (repo-relative paths):
 * [{ from, to, typeOnly, spec, reached }], `spec` the module specifier as written,
 * `to` a repo-relative file when the import resolves to one, else the path it points at: a
 * workspace package import resolves through the package's `exports` to a file, and to the package
 * directory when that names none. `reached` is every file the import gives its importer, as
 * [{ to, typeOnly }]: `to` itself and what its `export ... from` lines pass on, transitively (a name
 * imported through a barrel is the file that defines it). External packages are left out.
 * `workspaceDirs` are the directories of the workspace packages; `aliases` are
 * [{ prefix, within, to }]: a `prefix` import from a file under `within` reads from `to`.
 */
export function readImports(repo, roots, { workspaceDirs, aliases }) {
  const files = sourceFilesUnder(repo, roots);
  const packages = packageInfo(repo, workspaceDirs);
  const isFile = (path) => {
    try {
      return statSync(join(repo, path)).isFile();
    } catch {
      return false;
    }
  };
  const settle = (path) => {
    // TypeScript sources import each other as "./x.js".
    const stem = path.replace(/\.[cm]?js$/, "");
    for (const candidate of stem === path ? [path] : [path, stem]) {
      for (const extension of EXTENSIONS)
        if (isFile(candidate + extension)) return candidate + extension;
    }
    return path;
  };
  const resolve = (from, spec) => {
    if (spec.startsWith("."))
      return { to: settle(posix.normalize(posix.join(posix.dirname(from), spec))) };
    const alias = aliases.find((a) => spec.startsWith(a.prefix) && from.startsWith(a.within));
    if (alias) return { to: settle(alias.to + spec.slice(alias.prefix.length)) };
    const parts = spec.split("/");
    const name = spec.startsWith("@") ? parts.slice(0, 2).join("/") : parts[0];
    const pkg = packages.get(name);
    if (!pkg) return null;
    const entry = packageEntry(pkg, `.${spec.slice(name.length)}`);
    const to = entry && settle(posix.join(pkg.dir, entry));
    return { to: to && isFile(to) ? to : pkg.dir };
  };

  const parsed = new Map();
  /** A file's specifiers and the names it declares, read once. */
  const parse = (file) => {
    if (!parsed.has(file)) {
      const source = readFileSync(join(repo, file), "utf8");
      parsed.set(file, {
        specifiers: specifiersIn(source, file.endsWith(".css")),
        declared: file.endsWith(".css") ? new Set() : declaredIn(source),
      });
    }
    return parsed.get(file);
  };
  const readable = (path) => isFile(path) && SOURCE.test(path);
  /**
   * The files that declare `name` for an importer of `file`, found through its `export ... from`
   * lines; an empty set when it comes from outside the repo, null when `file` neither declares nor
   * re-exports it. `seen` ends a cycle of `export *` lines.
   */
  const declaring = (file, name, seen) => {
    const key = `${file}|${name}`;
    if (seen.has(key)) return null;
    seen.add(key);
    if (!readable(file)) return new Set([file]);
    const { specifiers, declared } = parse(file);
    if (declared.has(name)) return new Set([file]);
    const follow = (r, wanted) => {
      const target = resolve(file, r.spec);
      if (!target) return new Set();
      // The line says the name comes from there, so a target this reader can't see into still defines it.
      return declaring(target.to, wanted, seen) ?? new Set([target.to]);
    };
    const named = specifiers.find((r) => r.reexport && r.names?.some((n) => n.as === name));
    if (named) return follow(named, named.names.find((n) => n.as === name).name);
    const namespace = specifiers.find((r) => r.reexport && r.ns === name);
    if (namespace) {
      const target = resolve(file, namespace.spec);
      return target ? whole(target.to) : new Set();
    }
    // `export *` passes a name on only from a module that has it.
    let found = null;
    for (const r of specifiers.filter((r) => r.reexport && !r.names && !r.ns)) {
      const target = resolve(file, r.spec);
      const hit = target && declaring(target.to, name, seen);
      if (hit) found = new Set([...(found ?? []), ...hit]);
    }
    return found;
  };
  /** `file` and every file its `export ... from` lines pass on, transitively: what a namespace import is given. */
  const whole = (file, out = new Set()) => {
    if (out.has(file)) return out;
    out.add(file);
    if (!readable(file)) return out;
    for (const r of parse(file).specifiers) {
      const target = r.reexport && resolve(file, r.spec);
      if (target) whole(target.to, out);
    }
    return out;
  };
  /**
   * The files that give `names` (null: everything) to an importer of `file`. A name the walk can't
   * find stays with `file`, the module imported: that fails safe, since only a box holding `file`
   * (or the whole package) then passes.
   */
  const definers = (file, names) => {
    if (names === null) return whole(file);
    const out = new Set();
    for (const name of names)
      for (const f of declaring(file, name, new Set()) ?? [file]) out.add(f);
    return out;
  };
  /** The files an import gives its importer, [{ to, typeOnly }]: `to` itself, and what defines the names it takes. */
  const reach = (to, { names, typeOnly }) => {
    const found = new Map([[to, typeOnly]]);
    const add = (files, type) => {
      for (const f of files) found.set(f, type && (found.get(f) ?? true));
    };
    if (names === null) add(definers(to, null), typeOnly);
    else {
      add(
        definers(to, new Set(names.filter((n) => !n.type && !typeOnly).map((n) => n.name))),
        false,
      );
      add(definers(to, new Set(names.filter((n) => n.type || typeOnly).map((n) => n.name))), true);
    }
    return [...found].map(([file, type]) => ({ to: file, typeOnly: type }));
  };

  const imports = [];
  for (const from of files) {
    for (const { spec, typeOnly, names } of parse(from).specifiers) {
      const target = resolve(from, spec);
      if (target && target.to !== from)
        imports.push({
          from,
          typeOnly,
          spec,
          ...target,
          reached: reach(target.to, { names, typeOnly }),
        });
    }
  }
  return imports;
}

/** Whether `path` is `root` or lies under it. */
export const under = (path, root) => path === root || path.startsWith(`${root}/`);
