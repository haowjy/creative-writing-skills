---
name: knowledge-layers
description: 'Use when deciding where knowledge goes or reading/writing durable docs: AGENTS.md, .context/, KB, docs/, and work directories.'
metadata:
  type: reference
---

# Knowledge Layers

Load `/creative-writing-skills:qi-layer` when writing or editing AGENTS.md or .context/ files: it
owns the craft (four principles, contents guidelines, what doesn't belong).
Load `/creative-writing-skills:information-hierarchy` if not already loaded for disclosure tiers.
Load `/creative-writing-skills:llm-writing` if not already loaded.

## The Five Layers

| Layer | What it holds | When to use it |
|---|---|---|
| `AGENTS.md` | Intent and mental model for a directory | First thing agents read on entry; what to understand *before* working here |
| `.context/` | Contracts, architecture, rationale (`CONTEXT.md`); deferred work (`TODO`, `FUTURE`) | Reference depth and tracked deferrals, co-located with the material they describe |
| KB | Cross-cutting decisions, domain concepts, patterns | Spans directories; outlives sessions; no single directory owns it |
| `docs/` | User-facing documentation | Different audience, different update cadence |
| Work directory | Temporary design decisions and scratch | Not colocated with durable content; scoped to an active work item |

## Placement Rules

If it's intent/mental-model for a directory → `AGENTS.md`.
If it's directory-scoped depth an agent looks up → `.context/`.
If it's deferred work scoped to this directory → `.context/TODO` (must-do)
or `.context/FUTURE` (nice-to-have). Flat markdown lists — each entry names
the affected path and concrete follow-up. Cross-cutting items or items needing
external visibility get filed in the project's issue tracker instead.
If it's big picture — cross-cutting decisions, domain concepts,
higher-level system architecture → KB.
If it's for end users → `docs/`.
If it's the human correcting an agent → the KB corrections register
(`resources/corrections/register.md`; `code.md` beside it for code projects).
`/correct` fixes the classes that repeat.
If it's a temporary work artifact → work directory.

When in doubt, colocate. Knowledge that depends on one subsystem belongs
in that subsystem's AGENTS.md or .context/ even when it reads like a
concept; the KB stays independent of any one implementation, holding what
survives a change to it. Knowledge that lives far from what it describes
rots faster: changes to the thing don't trigger awareness that a distant doc
needs updating.

**The KB links to the work's own docs.** Before writing to the KB about
some work, read the docs, `AGENTS.md`, `.context/`, and comments the work
updated. Link to what they describe, and write only what they don't say:
the settled intent, the reason, the rejected alternatives, how it relates
to the rest of the project. When they say all of it, the KB gets a link or
nothing. Cut a KB section that restates them down to the link and the
parts they don't say; the copy drifts the next time they change.

## Current Truth Over History

Every durable layer — AGENTS.md, `.context/`, KB, `docs/` — holds the best
current understanding; work directories may keep intermediate reasoning
while their work item is active. When durable content is
superseded, delete it or (for KB pages) move it to `archive/`
(`.kgignore`'d, excluded from the knowledge graph). Live content never
references archived content. Pages read as current truth, never narrate
their own evolution.

**Deletion needs no replacement.** A page whose subject is gone, or that
describes behavior the system no longer has, gets deleted on sight — even
with nothing new to write in its place. Stale knowledge is worse than a
gap: agents load it and reason from it. Deletion is the content-truth
owner's call; structural roles flag instead.

**History is the archive.** In a version-controlled tree, commit untracked
files before deleting them so the removal lands in history, and say what was
removed and why in the commit message. Elsewhere, preserve what still matters
in the project's archive before deleting. Deletion is cheap because nothing
preserved is truly lost.

**Truth is anchored per layer.** AGENTS.md and `.context/` describe the
tree that contains them: update them in the same change as what they
describe. The KB records the current settled intent — what the project
*should be* — and an invariant is KB truth the moment the human settles it,
done or not. Unsettled intent isn't KB material; it stays in the work directory.
`docs/` describes what has shipped to its readers. In a code project, load
`resources/code.md` for how this maps to branches, merges, and shipped code.

Decision records are the exception: preserve superseded decisions in place
when they explain why the system changed. Mark the old decision as
superseded and link to the replacement.

## Invariants and Current Choices

Record each settled point as one of two kinds. An **invariant** must hold
however the work is done. A **current choice** is what the project is doing
or trying for now. The test: if an agent found a better way that broke it,
should it stop and ask the human who owns the project first? If yes, it's an
invariant; if no, the agent changes it and updates the doc.

Default to current choice. The human's hedges ("for now", "let's try", "i
think", "whatever is less work") mark a trial, and so does the human agreeing
to something an agent proposed. An agent's own call stays a current choice
until the human makes it an invariant. Quote the human with their hedges
kept, and never record a trial as their ruling.

Write invariants as rules, in decision records or `AGENTS.md`. Write current
choices as how things stand now, beside the work they describe. Measurements
and the story of what went wrong go beside what they measure or explain, not
inside a rule. A status line says only whether the thing is done, partly
done, not done, or superseded; how it got there belongs in version control
or the archive.

## KB Conventions

### Structure

The KB is a directory tree like any other: it carries its own AGENTS.md
and `.context/` pair, written per `/creative-writing-skills:qi-layer` — intent in AGENTS.md,
governance depth (writing conventions, structure, validation) in
`.context/`. Read the KB's own `AGENTS.md` before writing. Treat this
skill as the cross-project default; the local KB guide wins for that KB.
See `resources/bootstrap.md` for a suggested starting layout.

### Wiki Page Conventions

Follow `/creative-writing-skills:information-hierarchy`. One concept per document; name files by
what they describe (`token-validation.md`), not when (`auth-redesign-notes.md`).
Cross-reference instead of re-explaining. Load `/creative-writing-skills:shared-dao` for vocabulary
methodology. Use mermaid for anything spatial; capture what the files
themselves can't easily tell you.

## Operations

**Ingest**: new information enters the KB. Read the source, extract key
knowledge, write or update wiki pages, and update indexes/cross-links touched
by the change.

**Maintain**: keep the wiki current per Current Truth Over History above.

**Lint**: health-check the wiki. Look for contradictions, stale claims,
orphan pages, missing cross-references. Use `/creative-writing-skills:md-validation` for link
checking and diagram validation.

Flag content needing human attention with `> [!FLAG] **Needs human review**`.
