# Atlas engine

A viewer and a check for a project's atlas pages. The pages and the config are the
project's; this directory holds no content and names no project. [README.md](README.md) says how
to adopt it and lists the config; [example/](example/) is a working toy.

- This directory's source is the `/creative-writing-skills:atlas` skill in meridian-base: a project copies it unchanged,
  and the check fails when an installed skill's copy differs. Fix the engine there.
- Keep it free of project names: nothing here outside comments may name the project it is used in,
  its directories or its packages (the project's own paths belong in its `atlas.config.mjs`).
- `pages.js` parses a page and has no DOM and no Node APIs, so `check.mjs` and the viewer read
  pages the same way. Change the page format there, in `check.mjs` and in the README together.
- `index.html` and `styles/page.css` hold no content and no colours: `page.css` paints with `--map-*`
  roles only, which the config's `tokens.roles` maps to the project's tokens (a few are mixed from
  those in `page.css`). Where the page needs a colour no role gives, add a role to the README's list and
  to every config (`example/` too); `check.mjs` fails a raw colour here and an unmapped role.
- Read colours from `<html>`, not an element lower down, so the `--map-*` roles have resolved in
  the current theme.
- A repo path from the address bar goes through `fetchRepoEntry`, which checks the URL the browser
  will request. The server serves only what git tracks, as `text/plain` with `nosniff` and a
  `sandbox` CSP, never as HTML or SVG; don't widen that.
- Third-party scripts are pinned with integrity hashes. To bump one, fetch the new file and
  recompute its `sha384`. React stays on 18 (19 has no UMD build).

How the viewer, routes, Map layout and server work: [`.context/CONTEXT.md`](.context/CONTEXT.md).
