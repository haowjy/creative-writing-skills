/**
 * The viewer's colours, read from the project's design token files (the config's `tokens.files`)
 * each time they are asked for: the custom property declarations of the blocks the config names,
 * as one stylesheet, then `--map-<role>: var(<token>)` for each of the config's `tokens.roles`
 * (the names `styles/page.css` paints with). A Tailwind `@theme` block, which a browser ignores,
 * becomes `:root`.
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { DEFAULT_DARK } from "./js/pages.js";

const ENGINE = dirname(fileURLToPath(import.meta.url));
const ROLES = ["background", "foreground", "card", "quiet", "border", "border-subtle", "focus", "link", "danger", "danger-tint", "warning", "sans"];

/**
 * The token files a config's colours come from, and the directory they are relative to: the
 * project's `tokens`, or the engine's neutral `default-tokens.css` when the config names none.
 */
export function tokenSource(config, repo) {
  if (config.tokens) return { root: repo, tokens: config.tokens };
  return {
    root: ENGINE,
    tokens: {
      files: [{ file: "default-tokens.css", blocks: [":root", `[${DEFAULT_DARK.attribute}="${DEFAULT_DARK.value}"]`] }],
      dark: DEFAULT_DARK,
      roles: Object.fromEntries(ROLES.map((role) => [role, `--${role}`])),
    },
  };
}

/** The top-level blocks of a stylesheet, comments removed: [{ selector, body }]. */
function topLevelBlocks(css) {
  const text = css.replace(/\/\*[\s\S]*?\*\//g, "");
  const blocks = [];
  let depth = 0;
  let start = 0;
  let selector = "";
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === "{") {
      if (depth++ === 0) {
        selector = text.slice(start, i).replace(/\s+/g, " ").trim();
        start = i + 1;
      }
    } else if (c === "}") {
      if (--depth === 0) {
        blocks.push({ selector, body: text.slice(start, i) });
        start = i + 1;
      }
    } else if (c === ";" && depth === 0) start = i + 1;
  }
  return blocks;
}

/**
 * The token stylesheet for `tokens` ({ files: [{ file, blocks }], roles: { role: "--token" } }), read from the repo at `root`.
 * A block is taken when one of the selectors in its list is in `blocks` (`@theme` names the Tailwind block).
 * Returns { css, names: the property names without `--`, missing: "file: selector" for each listed block that isn't there,
 * blocks: [{ selector, declarations: [[name, value]] }] the blocks taken, in file order }.
 */
export function readTokens(root, tokens) {
  const taken = [];
  const names = new Set();
  const missing = [];
  for (const { file, blocks: wanted } of tokens.files) {
    const found = new Set();
    for (const { selector, body } of topLevelBlocks(readFileSync(join(root, file), "utf8"))) {
      const hit = wanted.find((w) => selector.split(",").some((s) => s.trim() === w));
      if (!hit) continue;
      found.add(hit);
      const declarations = [
        ...body.replace(/\{[^{}]*\}/g, "").matchAll(/(--[\w-]+)\s*:\s*([^;{}]+);/g),
      ];
      for (const [, name] of declarations) names.add(name.slice(2));
      const taking = hit === "@theme" ? ":root" : selector;
      taken.push({
        selector: taking,
        declarations: declarations.map(([, name, value]) => [
          name,
          value.replace(/\s+/g, " ").trim(),
        ]),
      });
    }
    for (const w of wanted) if (!found.has(w)) missing.push(`${file}: ${w}`);
  }
  const rules = taken.map(
    ({ selector, declarations }) =>
      `${selector} {\n${declarations.map(([name, value]) => `  ${name}: ${value};`).join("\n")}\n}`,
  );
  const roles = Object.entries(tokens.roles ?? {});
  if (roles.length)
    rules.push(
      `:root {\n${roles.map(([role, token]) => `  --map-${role}: var(${token});`).join("\n")}\n}`,
    );
  return {
    css: `/* Built from ${tokens.files.map((f) => f.file).join(", ")}. */\n${rules.join("\n\n")}\n`,
    names,
    missing,
    blocks: taken,
  };
}
