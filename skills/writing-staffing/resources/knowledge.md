# Knowledge Maintenance

Agents that keep the kb current — extracting decisions, synthesizing facts, and maintaining connections. These don't write prose or review drafts; they maintain the knowledge layer that lets future agents (and humans) work with accurate context.

## chronicler

Extracts story facts from written chapters — character state, timeline events, canon facts, relationship changes. Reads the manuscript and produces compressed, annotated entries in the kb. Not a copy of the chapter — a synthesis of what changed in the project's factual state.

Also handles mining past sessions for decisions and commitments when dispatched with session references (via `meridian session`). This consolidates knowledge write-back into one agent rather than splitting session-extraction from chapter-extraction.

**When to dispatch:**
- After a chapter draft is finalized (post-critique, post-revision)
- After significant revisions to existing chapters that change established facts
- After brainstorm sessions where options were explored and direction was chosen
- After interactive writing sessions where the author made story decisions in conversation
- When starting work on a new arc and needing to baseline the current state

The chronicler writes character files, canon files, timeline entries, world entries, and decision records. It reads existing entries to avoid duplication and updates rather than appends when facts change.

## Base Agents for Knowledge Work

For graph maintenance, link topology checks, and structural kb health, use the base @kb-maintainer. For session transcript mining (read-only exploration before the chronicler writes), use the base @session-explorer. For wiki/reference page writing, use the base @kb-writer.

The base agents handle the generic mechanics; the chronicler handles CW-specific knowledge extraction that requires understanding story structure, character state, and narrative canon.

### Dispatch Order

Fan out the chronicler and base @session-explorer in parallel after the triggering event (chapter finalized, brainstorm concluded). Run base @kb-maintainer after both complete — it depends on the chronicler having finished writing entries.
