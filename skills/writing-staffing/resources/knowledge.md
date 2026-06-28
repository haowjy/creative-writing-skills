# Knowledge Maintenance

Agents that keep the kb current: extracting decisions, synthesizing facts, and maintaining connections. These do not write narrative prose or review drafts; they maintain the knowledge layer that lets future agents (and humans) work with accurate context. Use `/story-memory` for the information-first writing modes inside that layer.

## chronicler

Extracts story facts from written chapters: character state, timeline events, canon facts, relationship changes. Reads the manuscript and produces compressed, annotated entries in the kb. Not a copy of the chapter: a synthesis of what changed in the project's factual state.

Also handles mining past sessions for decisions and commitments when dispatched with session references (via `meridian session`). This consolidates knowledge write-back into one agent rather than splitting session-extraction from chapter-extraction.

**When to dispatch:**
- After a chapter draft is finalized (post-critique, post-revision)
- After significant revisions to existing chapters that change established facts
- After brainstorm sessions where options were explored and direction was chosen
- After interactive writing sessions where the author made story decisions in conversation
- When starting work on a new arc and needing to baseline the current state

The chronicler writes character files, canon files, timeline entries, world entries, and decision records. It reads existing entries to avoid duplication and updates rather than appends when facts change.

## Routing and Coverage

After a knowledge update, check coverage before moving on:

- **Facts and state changed?** Use @chronicler for canon, timeline, character state, relationship changes, and settled decisions.
- **Polished reference page needed?** Use @kb-writer for reader-facing or wiki-style pages that need link discipline and citations back to chapters.
- **Tree health or link topology changed?** Use @kb-maintainer for broken links, orphaned pages, duplicate pages, structure cleanup, and relationship diagrams.
- **Vocabulary drifted?** Update the relevant vocab page with the canonical term, aliases, source, and boundary conditions.
- **A convention changed?** Record it at the layer future workers will read before acting: project conventions for global story rules, local domain notes for domain-specific rules, and work notes for provisional decisions.
- **A problem persists beyond the current pass?** Log it as a writing issue instead of burying it in critique prose.

The chronicler owns creative-writing knowledge extraction. Use supporting base agents for generic mechanics: @session-explorer for read-only session mining before the chronicler writes, @kb-writer for polished reference pages, and @kb-maintainer for graph maintenance, link topology, and structural kb health.

### Dispatch Order

Run the chronicler after the triggering event settles (chapter finalized, brainstorm concluded, author decision made). Use @session-explorer first only when the relevant decision lives in a long transcript. Run @kb-writer when extracted facts need a polished reference surface. Run @kb-maintainer after content updates when tree health or links need cleanup. Finish by reviewing whether canon, vocab, decisions, issues, and links all landed in the right place.
