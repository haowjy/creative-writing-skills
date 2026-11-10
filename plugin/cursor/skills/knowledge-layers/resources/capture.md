# Capturing a Settled Change

What a settled change taught the project goes where `/creative-writing-skills:knowledge-layers`
places it, and nothing is written that the work's own docs already say.

1. **Read what you were given:** the brief's work and session refs, the
   changed files, the docs the work already updated, and the work
   directory's decision records and `DIVERGENCE/` log. Map each changed path
   to its nearest `AGENTS.md` and `.context/` and apply `/creative-writing-skills:qi-maintenance`'s
   gap test; repair the gaps even when the implementation agent did not.

2. **Find what the change made stale.** Search the KB for the names and
   terms the work touched, including the old names of anything it renamed or
   removed. Check each page you find against the code and docs as they are
   now: a page that describes behavior they contradict, restates them, or
   describes something that no longer exists is part of this capture. A
   direction the human chose that the code hasn't reached yet stays, marked
   as not built yet (`resources/code.md`). Where a choice is missing its reason, or you
   need the human's corrections of agents, have `@session-miner` find the passages
   and read them yourself. Spawn an `@explorer` for an area too large to
   read yourself.

3. **Delete, then write.** Delete each stale page or passage step 2 found,
   or rewrite it to current truth, and fix the links to it. Then write each
   behavior with its reason, and only what the human chose
   or the work established (`/creative-writing-skills:knowledge-layers` The KB Records Why). When
   the work's own docs already say everything it settled, add nothing for
   it. Move misplaced content to its place. Record each
   correction of an agent by the human as `resources/corrections/register.md`
   instructs.

4. **Reorganize what you touched.** Merge pages that cover one topic,
   split a page that covers several, and rename or move a page whose name
   or place no longer fits what it holds. Fix every link to what moved.

5. **Check, then commit.** Run `/creative-writing-skills:llm-writing` on each page you changed, for
   its reader in the Three Places table. Commission a cold read per
   `/creative-writing-skills:llm-writing` `resources/cold-read.md`, one `@cold-reader` for the pages
   where you wrote new prose, and act on its findings. Leave the corrections
   register's Occurrences column as it is: it cites sessions by design.
   Verify each tree with `/creative-writing-skills:md-validation`, then commit each
   version-controlled tree you touched. The capture is done when no page
   you found in step 2 still describes behavior the code or the docs
   contradict.
