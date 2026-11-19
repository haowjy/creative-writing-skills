# atlas

A viewer and a check for an atlas: Markdown pages with one Mermaid diagram each, so they read on
GitHub and in an editor as they do in the viewer. The viewer draws each page as a clickable map
you drill down through, renders Markdown, journeys and state machine pages, and opens every file
in the repo inside itself. The check fails when the pages break: a link or a box's page that is
gone, a box with no section. For a codebase, config keys turn on checks against the code: a
path that is gone, a service with no page, a directory no box covers, an arrow with no import
behind it, a dependency break nobody wrote down.

[example/](example/) is a working toy: a config, two level pages, a journey and a fake source
tree. Read it first.

```sh
node tools/atlas/check.mjs tools/atlas/example/atlas.config.mjs
node tools/atlas/serve.mjs tools/atlas/example/atlas.config.mjs   # http://localhost:4848/atlas/
```

## Adopting it

1. Copy this directory into the project (`tools/atlas/`), unchanged. Its source is the `/creative-writing-skills:atlas`
   skill: a change to the engine goes there, and the project copies it again.
2. Write `atlas.config.mjs` and the pages beside each other, in the directory the config's
   `pagesDir` names. Start from `example/`: `example/architecture/` shows each kind of page, and "The pages"
   below gives the format in brief.
3. Serve it. With Vite, in `vite.config.ts`: `plugins: [atlasPlugin("<path to atlas.config.mjs>")]`,
   imported from `tools/atlas/vite-plugin.mjs` (dev only; a build never includes it). Without Vite,
   `node tools/atlas/serve.mjs <config> [port]`. The viewer is at `/atlas/`.
4. Add a check script: `"check:atlas": "node tools/atlas/check.mjs <path to atlas.config.mjs>"`, and put it in
   the project's gate.

## The pages

`README.md` in the pages directory lists the top-level pages under `## The pages` as
`- [Label](page.md)`; the first is the home page. Any level page a box's `Opens` names is a child, drilled into from
that box, with a breadcrumb. Besides level pages the directory may hold:

- `journeys/index.md` and one page per journey (`nav.journeys`), `flows/index.md` and one sequence diagram per
  flow, each linked from a journey step's `Map` line;
- `dependencies.md` (`nav.dependencies`): the rules, and a table `| from | to | rule | example file |` of
  the places the code breaks them, one row per break; with a file rule, a second table
  `| file | imports |`, one row per importing file and module (the rule is named in the section heading;
  with several file rules a third column `rule` says which).

A level page is a `flowchart`; each box is
`id["name<br/><small>role</small>"]:::kind` with a `## id` section giving a one-line sub, `Kind`, `Paths`
(backticked repo paths), `Docs`, `Machines`, `Opens`, `Breaks`, `Drift`, `See`, `Keys` (the credentials the box
holds: env vars, secrets, tokens, as free text) or `Shot` (`- Shot: <shot>` or `- Shot: <shot>/<region>`, a
screenshot from the config's `screens` manifest, cropped to the region when one is named) items. Kinds: `person`,
`client`, `service`, `store`, `external`, `files`, `domain`, `feature`, `module`, `package`, `context`,
`group`, `note`. Arrows are `a -->|"1. sends it"| b` (`<-->` for both ways); numbered ones are the main path. A dotted arrow,
`a -.->|"is handed the store"| b`, is a dependency handed in (a port, a callback), drawn dashed in the Map. With
`arrows.imports`, a solid arrow between two code boxes (`domain`, `feature`, `module`, `package`) needs an import
behind it: a value import, not a type-only one. A dependency with no value import behind it is drawn dotted:
a port or callback handed in, or a relation through types alone (`a -.->|"takes the Row type of"| b`); the
label says which. The check lists the rest.

A journey step's `Shot` item fills the step card with the screenshot.

## The config

`atlas.config.mjs` default-exports a plain object. The browser imports it too, so it holds data only: no
functions, no imports. Paths are repo-relative; a glob's `*` is one path segment and `**` any depth (`docs` globs only: `coverage`, `services`, `imports.workspaces` and dependency rules take `*` alone, and the check fails on a `**` there).

| key | meaning |
|---|---|
| `title` | the viewer's title |
| `root` | the repository root, relative to the config file |
| `repo`, `branch` | "on GitHub" links: `https://github.com/<repo>/blob/<branch>/<path>` |
| `pagesDir` | the directory with README.md, the level pages, `journeys/`, `flows/` and the dependencies page |
| `tokens` | optional: the colours, from the project's own design tokens; without it the viewer uses the engine's neutral `default-tokens.css`. `files: [{ file, blocks }]`: the custom properties of each listed block (a block is taken when one selector in its list is in `blocks`; `@theme` takes a Tailwind `@theme` block, served as `:root`). `dark: { attribute, value }`: what the viewer sets on `<html>` for the dark theme, which a dark block's selector must match. `roles: { <role>: "--token" }`: `styles/page.css` paints with `--map-<role>` only, and each role is served as `--map-<role>: var(--token)`. The roles are `background`, `foreground`, `card`, `quiet` (secondary text), `border`, `border-subtle`, `focus`, `link`, `danger`, `danger-tint`, `warning` and `sans` (the font); the check fails a role the page uses and the config doesn't map, a role the page doesn't use, and a token the files don't define |
| `screens` | optional: the repo path of a JSON manifest of screenshots, `{ "<shot>": { image, width, height, title, regions: [{ id, label, x, y, w, h, map?, code? }] } }`. `image` is relative to the manifest, the bounds are pixels of the image, `map` is a viewer route `<page>/<box>` (the page's file name without `.md`, a box id) and `code` a repo path. A `Shot` item needs it. With `serveSource: false`, `docs` must match the manifest and the images |
| `arrows` | optional: `{ imports: true }` holds each solid arrow between two code boxes to a value import: some file under the from box's source imports, by value, a file under the to box's source (either way for `<-->`; type-only imports and tests don't count). A box's source is its Paths, a reference box that `Opens` another page included (give it the Paths of what it stands for). A solid arrow whose code end has no source files fails: give that box Paths, or draw the arrow dotted. An import reaches the files that define what it names: a workspace package (`imports.workspaces`) specifier resolves through its `package.json` `exports` (else `main`), and `export * from` / `export { x } from` lines are followed by name, so a box holding one file of a package passes only when the importer names something that file defines. A default import is the name `default`; a namespace import (`* as ns`) is given every file the module re-exports; a name the reader can't trace stays with the module imported, so only a box holding that file passes. A box holding the whole package passes for any value import of it. The `exports` reader takes a string, else the first of the conditions `import`, `default`, `types`; a target it can't find leaves the import at the package directory, which also fails safe |
| `services` | optional: `{ glob, page }`. Each directory matching `glob` needs a box on `page` whose Paths are inside it and whose Opens is the page named after the directory |
| `coverage` | `[{ glob, needs? }]`: each directory matching `glob` (that holds `needs`, if given) must lie under some box's Paths |
| `imports` | `{ workspaces, aliases }`: `workspaces` are globs of package directories, resolved by their `package.json` name; `aliases` are `{ prefix, within, to }` |
| `dependencies` | `{ page, rules }`, read when `nav.dependencies` is set. A rule is `{ rule, cycle: glob }` (units that import each other in a loop) or `{ rule, from: glob, to: glob }` (a unit of `from` importing under another unit of `to`; only value imports count). A unit is a directory matching the glob, named by its last segment; the `rule` text is the row's third cell. A **file rule** is `{ rule, files: dir, to: [module, …] }`: any source file under the directory `files` importing a listed module, one row per file and module, so a new file breaks the rule even when a sibling already does. Rows name the file relative to `files` and a repo path by its last segment. A module is a workspace package (`@scope/name`, with its subpaths, and a relative path into its directory), a package subpath (`@scope/name/sub`, with what lies under it) or a tracked repo path (a directory or file; matched on where the import resolves to); a module that is none of these fails the check. The `files` directory is read apart from the boxes' Paths, so it may lie outside them without feeding the unit rules. Type-only imports count. Test files don't (`*.test.*`/`*.spec.*`, `.d.ts`, and directories or files named `__tests__`, `test`, `tests`, `e2e`, `fixtures`, `*test-support*`) |
| `stateMachines` | optional: `{ index, pages }`: the index page the viewer opens, and a git pathspec for every state machine page the index must list |
| `nav` | `{ journeys, machines, dependencies }`: the label of each optional section; leave one out and it is off |
| `serveSource` | default `true`: the dev server shows any tracked file. `false`: only the pages directory and `docs`. Use `false` only when the viewer's server is the sole thing that would show source: a dev server that serves the workspace itself (Vite's `/@fs/`) shows it anyway |
| `docs` | globs of files shown even when `serveSource` is `false` |

## What the viewer serves

Under `/atlas/`: the engine's own files, the config, `tokens.css` (the `tokens` blocks and the `--map-*` roles, read from
disk on each request), and `repo/<path>`: any file git tracks, as text
(images as images), or a directory as the tracked entries under it. It reads the working-tree copy, so
uncommitted edits show; untracked files are refused except new unignored ones under `pagesDir`. Ignored
files (`.env`, `node_modules`), anything with `..` in it, and binary files are refused. `index.html` is sent
with a Content-Security-Policy (scripts only from the server and the pinned CDN), so a script inside a
rendered Markdown file does not run; `serve.mjs` also answers only to `localhost` and `127.0.0.1` on its port. `pnpm dev:funnel`-style tunnels that
publish the dev server also publish what it serves; on a private repository whose dev server serves nothing else, set `serveSource: false`.

## What the check catches

It needs the project to be a git repository: it lists files with `git ls-files`.

Grammar (a Mermaid line the format doesn't allow, a box without its section, numbered arrows out of order,
a note linked to nothing); every path, link and `#id` resolving; every `coverage` directory under some box;
every service with its page; every journey step's map link and flow reached; flow participants being box ids;
state machine pages indexed and on a box; dependency rows matching the breaks computed from value imports
(a break with no row, a row with no break, a wrong example file), and file-rule rows matching each file's
imports, types included; every `tokens` block present, and the
viewer's stylesheet free of raw colours and of variables that aren't mapped `--map-*` roles; with `arrows.imports`,
each solid arrow between code boxes backed by a value import; with `screens`, the manifest's images, bounds, `map` boxes and
`code` paths, and each `Shot` naming a shot and region the manifest has. It doesn't catch whether a box's words or an arrow is still true.
