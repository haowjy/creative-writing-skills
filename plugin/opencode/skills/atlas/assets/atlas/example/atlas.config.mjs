/*
 * A toy project for the atlas engine: two level pages, one journey, a fake source tree.
 * Check it:  node tools/atlas/check.mjs tools/atlas/example/atlas.config.mjs
 * View it:   node tools/atlas/serve.mjs tools/atlas/example/atlas.config.mjs
 * The README next to the engine explains every key.
 */
export default {
  title: "Example architecture",
  root: ".", // this directory
  repo: "example/toy", // "on GitHub" links point at a repository that doesn't exist
  branch: "main",
  pagesDir: "architecture",
  tokens: {
    files: [{ file: "tokens.css", blocks: [":root", '[data-theme="dark"]'] }],
    dark: { attribute: "data-theme", value: "dark" },
    // Each colour role the viewer paints with, mapped to a token the files above define.
    roles: {
      background: "--color-background",
      foreground: "--color-foreground",
      card: "--color-card",
      quiet: "--color-muted-foreground",
      border: "--color-border",
      "border-subtle": "--color-border-subtle",
      focus: "--color-primary",
      link: "--color-jade-text",
      danger: "--color-destructive",
      "danger-tint": "--color-destructive-tint",
      warning: "--color-syntax-string",
      sans: "--font-sans",
    },
  },
  services: { glob: "services/*", page: "system.md" },
  coverage: [{ glob: "services/*" }, { glob: "services/api/src/*" }],
  imports: { workspaces: ["services/*"], aliases: [] },
  // Screenshots a box or journey step shows (`- Shot: publish/post-form`); see screens/screens.json.
  screens: "screens/screens.json",
  // A solid arrow between two code boxes needs a value import behind it; a dotted one doesn't.
  arrows: { imports: true },
  dependencies: {
    page: "dependencies.md",
    rules: [{ rule: "modules are acyclic", cycle: "services/api/src/*" }],
  },
  nav: { journeys: "Journeys", dependencies: "Dependencies" },
};
