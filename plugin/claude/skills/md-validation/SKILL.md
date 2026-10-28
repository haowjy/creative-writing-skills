---
name: md-validation
description: 'Load after writing, moving, or linking markdown pages or Mermaid diagrams, before committing them: validates links, the KB link graph, and diagram syntax.'
metadata:
  type: reference
---

# Markdown Validation

Validate broken links before committing documentation changes. Inspect the
link graph when you need to understand document topology or find orphan,
hub, and disconnected pages.

Validate Mermaid syntax and style after diagram edits. Fix every reported
issue and repeat the validation until it is clean.

See `resources/mermaid-authoring.md` for diagram authoring rules, validator
warning categories, and inline suppressions. See
`resources/validation-inputs.md` for context path names and persistent ignore
files.
