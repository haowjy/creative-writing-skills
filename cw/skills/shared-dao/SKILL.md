---
name: shared-dao
description: >
  Shared vocabulary for creative writing projects. Load when establishing
  canonical story terms, resolving ambiguous names, checking term consistency,
  or deciding where vocabulary belongs in kb/.
---

# Shared Dao

Shared vocabulary is the contract between the author's intent and agent action.
Ambiguous, overloaded, drifting, or misleading terms corrupt drafts early:
magic systems get renamed, factions blur together, genre terms mean different
things in different prompts, and characters speak with vocabulary the author
never intended.

Treat vocabulary problems as story-structure problems. Resolve terminology
while the meaning is still easy to sharpen.

## Core Discipline

Scrutinize important terms aggressively. Reuse existing names when they already
fit the concept. Converge on one name per concept and one concept per name as
quickly as the evidence allows.

Resolve terminology early:

- rename when the clearer term is available
- define when the concept is real but still blurry
- flag when the author's judgment is required

## Where Vocab Lives

Place terms at the lowest common scope where they are shared:

- **Project vocab** (`kb/vocab.md`): terms used across the whole story
- **Domain vocab** (`kb/<domain>/vocab.md`): terms specific to one domain,
  such as worldbuilding, characters, factions, or timeline eras
- **Work notes** (`work/...`): provisional vocabulary during brainstorming or
  drafting, promoted to `kb/` once settled

Each entry includes:

- **Canonical name**: the form agents should use
- **Definition**: one to three sentences. Include boundaries that prevent
  likely confusion.
- **Aliases**: names the author, characters, drafts, or older kb pages
  actually use
- **Source**: where the usage was established or decided

## Discovery

Before defining new terms, check what already exists:

1. Read relevant vocab files.
2. Search `CLAUDE.md`, kb pages, outlines, drafts, and work notes.
3. Spawn focused subagents when the search is broad enough to crowd your context.
4. Check how the author uses the term in conversation and prose.

Mint new terms when they mark a real new concept. Let new vocabulary reflect
clear distinctions rather than uncertainty, local convenience, or unexamined
drift.

## Disambiguation

Ambiguity is the root failure mode. Resolve it before carrying the term
forward:

- **Same term, different meanings:** pick one meaning for the canonical
  definition, and give the other meaning its own name.
- **Different terms, same meaning:** pick one as canonical, record the others
  as aliases.
- **Unclear meaning:** ask the author: "When you say X, what specifically do
  you mean? Where are the edges of that meaning?"

When terminology conflicts with existing kb or draft usage, resolve the drift
when the evidence is clear. When author judgment is needed, flag the conflict
explicitly in your report so competing names stay visible.

## Creative Writing Terms to Watch

- Magic, technology, powers, abilities, rituals
- Factions, institutions, places, cultures, eras
- Titles, ranks, honorifics, forms of address
- Relationship labels and social categories
- Character-specific vocabulary, catchphrases, verbal tics
- Genre terms the author uses with a project-specific meaning
- Chapter, arc, POV, and timeline labels

Shared vocabulary is the contract between author intent and agent action.
Ambiguity you leave in vocab propagates into drafts, critique, continuity, and
KB updates.
