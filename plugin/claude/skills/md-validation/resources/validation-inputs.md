# Validation Inputs

## Context Paths

When the validator supports context names, `kb`, `strategy`, and `work` resolve
to the configured knowledge-base, strategy, and work directories. Use the
context name instead of copying an absolute path that changes between machines.

## Persistent Exclusions

Place `.kgignore` at the root of a link scan and `.mermaidignore` at the root
of a diagram scan. Both use gitignore-style patterns. Exclude generated,
vendored, or deliberately unsupported material; do not use an ignore file to
hide a broken document that belongs to the validated tree.
