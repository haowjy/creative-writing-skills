---
name: qi-layer
description: 'Use when writing or maintaining AGENTS.md, .context/CONTEXT.md, or a Claude-specific CLAUDE.md: keep intent docs minimal and load-bearing.'
metadata:
  type: reference
---

# qi-layer

`/qi-maintenance` owns when colocated knowledge must move with the changes it describes.
This skill owns how to write and structure that knowledge.

Load `/creative-writing-skills:knowledge-layers` for where each layer lives and what it holds.
Load `/creative-writing-skills:llm-writing` if it isn't already loaded.

This skill is about **how to write and maintain** the directory-local pair:
AGENTS.md and `.context/CONTEXT.md`. The pair governs any tree agents work
in — code, the KB, docs, work directories. AGENTS.md loads into an agent's
bounded context as standing instructions: write it like a prompt, minimal,
every line load-bearing.

## The Four Principles

1. **Fractal Compression**: leaf AGENTS.md summarizes its directory's
   content; parent AGENTS.md summarizes its children. Each level is a
   compression of the level below.
2. **Hierarchical Summarization**: root provides broad architectural
   frame. Leaves provide local working knowledge. Agents accumulate
   understanding as they descend.
3. **LCA Deduplication**: shared knowledge appears once at the shallowest
   node covering all relevant paths.
4. **Progressive Disclosure**: give just enough to work correctly at this
   level. Link to `.context/CONTEXT.md` for depth.

## Writing AGENTS.md

Agents read AGENTS.md before opening anything else in the tree — write for
that moment. Ask: **what must someone understand before working here?**
That's what AGENTS.md captures.

Keep AGENTS.md as short as the directory allows, rarely past 200 lines.
Include only what has substance:

- **Purpose**: what this area IS and what it ISN'T (1–3 sentences)
- **Mental model**: how to think about this area, key abstractions
- **Key rules**: constraints, what breaks if you get it wrong
- **Anti-patterns**: what NOT to do here
- **Downlinks**: to `.context/` for depth, to related areas

An agent that only reads AGENTS.md should be able to work correctly here.
An agent that also reads .context/ should be able to change things safely.

## Writing .context/CONTEXT.md

Reference depth, co-located with what it describes. Where an agent
goes when it needs contracts, architecture, or rationale in detail.

Sections (use only those with substance):

- **Contracts**: interfaces, invariants, what breaks if violated
- **Architecture**: component relationships, data flow, dependency direction
- **Rationale**: why X over Y, rejected alternatives
- **Patterns**: how to work here, concrete pitfalls

The `.context/` directory is extensible: additional files alongside
CONTEXT.md for specialized concerns.

## What Does NOT Belong in AGENTS.md

Apply the **every-session test**: root AGENTS.md loads on every session.
If knowledge is only relevant when working in a specific domain, it belongs
in that domain's AGENTS.md or .context/, not root.

Apply the **think-vs-lookup test**: text whose removal would cause a
*wrong decision* belongs in AGENTS.md. Text an agent would merely have to
*look up* belongs in .context/. Text that changes no behavior gets
deleted — agents already know their craft and common conventions.

Specific failure modes:

- **Session bleed**: LLM working notes that calcified into the instruction
  file. Tells: status-update language ("**deleted**", "shipped", "deferred"),
  implementation terms packed without framing, history narration.
- **Reference material posing as intent**: tables, command blocks, full
  scheme vocabularies, implementation specifics.
- **Redundant guards**: prose warnings for invariants already enforced by
  a check (tests, types, validators). The check is the real guard; prose
  rots faster.
- **Duplicated knowledge**: restating what lives in a skill, a domain
  .context/, or a KB page. Link to where it lives.
- **Domain-specific detail at root**: URI scheme tables, gateway pricing
  internals, auth implementation details. These belong in their domain's
  AGENTS.md, not root.

## Structural Rules

- Relative paths for all links
- AGENTS.md and .context/ at the same directory level (siblings)
- Link to files, not headings (headings change more often)
- Lateral links between `.context/` directories with contracts between them
- LCA deduplication: if two siblings share context, put it in the parent

## CLAUDE.md

Claude Code reads AGENTS.md when a directory has no CLAUDE.md, so most
directories need only AGENTS.md. Add a CLAUDE.md only for Claude-specific
instructions, and make `@AGENTS.md` its first line: when CLAUDE.md exists,
Claude reads it instead of AGENTS.md. Never write shared instructions into
CLAUDE.md.

Loading differs by level. At the root, every harness loads AGENTS.md each
session. In subdirectories, Claude loads a nested AGENTS.md when it touches
files there; other agents see nested AGENTS.md only by reading it on entry. Write each nested
AGENTS.md for that reader: the local additions an agent needs on entry, with
everything else inherited from ancestors.
