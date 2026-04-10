---
name: knowledge-graph
description: Project document navigation. Use when you need to understand how documents connect, find related content, identify orphaned pages, or orient on a project's structure before doing other work.
---

# Knowledge Graph — Document Relationship Mapping

Parse markdown files to build a map of how a project's documents connect. Useful for orientation (what exists, how it's organized), finding related content before writing or reviewing, and maintenance (orphans, broken links, missing back-links).

## What It Parses

The bundled `resources/graph.sh` script extracts relationships from these patterns:

- **Markdown links** — `[text](path)` explicit references between documents
- **Wikilinks** — `[[entity-name]]` shorthand references common in knowledge bases
- **Mermaid relationship blocks** — `graph`, `flowchart`, and relationship lines in fenced mermaid blocks
- **YAML front matter references** — fields like `arc`, `chapter`, `characters`, `location` that connect documents by metadata
- **Entity mentions** — names and terms that appear across documents without explicit links

## What It Outputs

- **Connectivity graph** — file → list of outbound links and the files that link back to it
- **Orphaned files** — documents nothing links to (potential dead content or missing integration)
- **Broken links** — references to files or paths that don't exist
- **Missing back-links** — A references B, but B doesn't reference A (useful for wiki and knowledge base maintenance)
- **Clusters** — groups of tightly connected documents (helps identify topic areas)
- **Entity mention map** — which documents mention which entities, even without explicit links

## Running the Script

```bash
bash resources/graph.sh [root_directory]
```

If no directory is specified, it searches from the current working directory. The script uses only standard unix tools (grep, awk, sed, find, sort) — no Python or other runtime dependencies.

The output is plain text, structured with clear section headers. Pipe it, redirect it to a file, or read it directly.

## When to Read the Script Source

Read `resources/graph.sh` if you need to understand exactly what patterns it matches, extend it for a project with custom link conventions, or debug unexpected output. For normal use, just run it and read the report.

## Interpreting Results

Orphaned files aren't automatically problems — some documents are entry points (READMEs, indexes) that are linked *to* but not *from*. Missing back-links matter most in wikis and knowledge bases where bidirectional navigation is expected. Broken links are almost always worth fixing.

The graph is a starting point for investigation, not a verdict. An orphaned file might be intentionally standalone. A cluster of tightly linked files might be a well-maintained topic area or might indicate circular references with no external connections.
