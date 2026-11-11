---
name: qi-layer
description: 'Use when writing or maintaining AGENTS.md or .context/CONTEXT.md: AGENTS.md loads automatically, so it keeps only what matters most.'
metadata:
  type: reference
---

# qi-layer

How to write the colocated pair, `AGENTS.md` and `.context/CONTEXT.md`, in
any tree agents work in: code, a KB, docs, a work directory.
`/creative-writing-skills:knowledge-layers` says what belongs in which place; `/creative-writing-skills:qi-maintenance` keeps
the pair true as the tree changes.

## Writing AGENTS.md

`AGENTS.md` is loaded automatically: the root one into every session, a
nested one when an agent works in its directory, on harnesses that load
nested files. Codex loads only the files from the root down to where it
started, so the root tells agents to read an area's `AGENTS.md` before
changing that area. Write instructions there, not in a `CLAUDE.md`: Claude reads
`AGENTS.md` only when no `CLAUDE.md` sits in the directory or above it. Every line costs every
agent that works there, every time, so it holds only the most important
information: what must an agent understand before working here? Write it
like a prompt, as short as the directory allows, rarely past 200 lines.
Write a nested file as the local additions an agent needs on entry.

Put in only what an agent can't work out by reading the code: what the area
is for and, at the root, who its users are and what they rely on; the
commands that check work here; places where the code misleads (a live
directory that looks dead, a pattern new code must not copy); choices that
aren't visible in the code; mistakes agents have made here more than once;
and links to `.context/` and related areas. An agent that reads only
`AGENTS.md` should work correctly here; one that also reads `.context/`
should change things safely.

The tree compresses as it climbs. A leaf summarizes its directory, a parent
its children, and shared knowledge appears once, at the shallowest directory
covering every place it applies. Agents accumulate the tree as they descend,
so a child never repeats its parent.

## Writing .context/

`.context/CONTEXT.md` holds the depth an agent looks up before editing:
contracts and what breaks if they're violated, architecture and dependency
direction, rationale, concrete pitfalls. Add files beside it for specialized
concerns.

## What Doesn't Belong in AGENTS.md

Test each line: would removing it cause a wrong decision here? Text an agent
would only have to look up goes in `.context/`; text that changes nothing
gets deleted. Detail that matters in one domain goes in that domain's
directory, not the root.

- **Session bleed:** working notes that calcified into instructions: status
  words ("shipped", "deferred"), history, decision IDs, implementation terms
  with no framing.
- **Overviews:** architecture, file layout, tables of modules or fields,
  full vocabularies. The agent reads the repo itself; depth it has to look
  up goes in `.context/` or the code's own docs.
- **Procedures some runs need:** releasing, migrations, a review checklist.
  They go in a doc or skill the file links to.
- **Rules that can't have exceptions:** make them a hook, deny rule or CI
  check. A prose rule is followed almost always, not always, and emphasis
  (ALL CAPS, IMPORTANT) makes the model over-apply it.
- **Guards a check already enforces:** the test, type or lint is the guard;
  prose beside it rots.
- **Copies** of what a skill, another `.context/`, or a KB page says. Link
  to it.

## Structure

- Relative links, to files rather than headings.
- `AGENTS.md` and `.context/` sit side by side in the same directory.
- Link across `.context/` directories that share a contract.
