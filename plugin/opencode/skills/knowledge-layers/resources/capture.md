# Capturing a Settled Change

The Ingest operation for a change or phase that has settled: what it
taught the project goes into the durable layers, routed per the Five
Layers table, and nothing is written that the work's own docs already say.

1. **Orient.** Skim the existing docs to know where updates land: the
   knowledge base, plus `.context/` and `docs/` in the project tree. While
   reading, note what is stale, bloated, or misplaced.

   Then start from your brief: the work and session refs, the changed
   files, the docs the work already updated, and the human's decisions it
   quotes. Read those docs, then the work directory's decision records and
   its `DIVERGENCE/` log. Undocumented
   decisions hide in deltas: between plan and result, between what was
   discussed and what was written down. Mine the sessions behind the work
   only for what the brief and logs don't account for: a decision without
   its reason or the alternatives it rejected, the human's corrections of
   agents, a delta no log records.

   Search the KB for the names and terms the work touched. Each page that
   contradicts the work or restates its docs is part of this capture.

   Map every changed path to its nearest `AGENTS.md` and current-truth
   `.context/` documents, compare them to the resulting checkout, and apply
   `/creative-writing-skills:qi-maintenance`'s gap test. Repair the gaps even when the
   implementation agent did not.

2. **Investigate, in parallel,** what the brief and the logs leave open.
   Tight scope produces sharp reports; broad scope dilutes attention.
   - `@explorer` per area of the project (one subsystem or concern each)
   - `@session-miner` per prior conversation worth mining for decisions,
     rejected alternatives, rationale, and the human's corrections of agents

   Spawn a follow-up wave only for areas that could change a concrete doc
   target, up to three waves in all. At that limit, capture what you have
   and report the uncovered gaps.

3. **Write, routed by layer.** Reconcile the reports into one picture of
   current truth: what each layer should say, and where existing docs
   contradict it. Record the human's words as said, per Invariants and
   Current Choices. Reconcile colocated gaps before writing cross-cutting
   KB updates. Delete or move stale and misplaced content; queue
   within-tree splits and renames for step 4. When the work's own docs
   already say everything it settled, add nothing for it and spend the run
   on what step 1 found. Record each correction of an agent by the human as
   `resources/corrections/register.md` instructs.

4. **Hand structure to `@kb-maintainer`.** One per tree with structural
   work queued from step 3; it takes one tree per spawn. It owns
   structure; you own content. When it flags a contradiction, you resolve
   it.

5. **Check what you wrote.** Run `/creative-writing-skills:llm-writing` on each page you changed,
   for that page's reader (the Reader column of the Five Layers table).
   Then commission a cold read per `/creative-writing-skills:llm-writing` `resources/cold-read.md`,
   one `@cold-reader` per tree where you wrote new or rewritten prose, and
   act on its findings as that resource says. One exception: the
   corrections register's Occurrences column cites sessions and quotes by
   design, so leave it as it is.

   Last, verify every tree you touched with `/creative-writing-skills:md-validation` (links, KB
   graph, diagrams).

6. **Commit.** The KB is often a separate repo from the project tree.
   Commit each version-controlled tree you touched.
