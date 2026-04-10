# Knowledge Maintenance

Agents that keep `$MERIDIAN_FS_DIR/` current — extracting decisions, synthesizing facts, and maintaining connections. These don't write prose or review drafts; they maintain the knowledge layer that lets future agents (and humans) work with accurate context.

## session-miner

Extracts decisions, facts, and commitments from conversations and brainstorm sessions. Mines past sessions via `meridian session` for story direction choices, character decisions, rejected alternatives, worldbuilding commitments, and open questions.

Writes findings inline to `$MERIDIAN_FS_DIR/` with decision annotations (see the story-decisions skill for annotation format). The session-miner's value is recovering reasoning that would otherwise be lost to compaction.

**When to dispatch:**
- After brainstorm sessions where options were explored and direction was chosen
- After interactive writing sessions where the author made story decisions in conversation
- After critique synthesis where the orchestrator overrode or accepted reviewer findings
- Retroactively, when a writer or critic encounters a fact with no recorded reasoning

**Timing matters.** Dispatch the session-miner promptly after the triggering event — the session context is richest immediately after, before compaction thins it out.

## chronicler

Extracts story facts from written chapters — character state, timeline events, canon facts, relationship changes. Reads the manuscript and produces compressed, annotated entries in `$MERIDIAN_FS_DIR/`. Not a copy of the chapter — a synthesis of what changed in the project's factual state.

**When to dispatch:**
- After a chapter draft is finalized (post-critique, post-revision)
- After significant revisions to existing chapters that change established facts
- When starting work on a new arc and needing to baseline the current state

The chronicler writes to `$MERIDIAN_FS_DIR/characters/`, `$MERIDIAN_FS_DIR/canon/`, `$MERIDIAN_FS_DIR/timeline/`, and `$MERIDIAN_FS_DIR/world/`. It reads existing entries to avoid duplication and updates rather than appends when facts change.

## graph-maintainer

Keeps relationship maps and cross-links current across all `$MERIDIAN_FS_DIR/` content. Rebuilds connection maps, flags orphaned documents and missing back-links, updates mermaid relationship diagrams in `$MERIDIAN_FS_DIR/graphs/`.

**When to dispatch:**
- After the chronicler or session-miner has written new entries to `$MERIDIAN_FS_DIR/`
- After wiki-editor updates that introduce new entities or relationships
- Periodically as a health check when `$MERIDIAN_FS_DIR/` has grown significantly
- When an orchestrator notices cross-reference failures or stale links

The graph-maintainer is the last agent in the knowledge update chain — it depends on the chronicler and session-miner having finished their work. Fan out chronicler and session-miner in parallel, then run graph-maintainer after both complete.
