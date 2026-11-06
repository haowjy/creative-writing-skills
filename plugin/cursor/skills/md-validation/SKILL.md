---
name: md-validation
description: 'Load after writing, moving, or linking markdown pages or Mermaid diagrams, before committing them: validates links, the KB link graph, and diagram syntax.'
metadata:
  type: reference
alwaysApply: false
---

# Markdown Validation

Validate links before committing documentation changes, and read the link graph
before and after restructuring a tree. Validate Mermaid syntax and style after
diagram edits. Fix every reported issue and repeat the validation until it is clean.

Use the validators your project or runtime provides. Their commands, warning
categories, suppression comments, and ignore files belong to that tool: when
the runtime offers Markdown-validation guidance, read it before running them.
Report any check you could not run.

When a warning marks a construct you meant, suppress only that category, as
narrowly as the validator allows, with the reason beside the diagram. Exclude
generated or vendored material from validation; never exclude a broken page
that belongs to the tree.

See `resources/mermaid-authoring.md` for diagram authoring rules.
