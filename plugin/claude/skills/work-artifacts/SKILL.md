---
name: work-artifacts
description: 'Load when work must survive compaction or crashes or be shared with other agents: findings, decisions, and artifacts go in the work directory, not in context.'
metadata:
  type: principle
---

# Work Artifacts

The work directory is the shared state between you, the user, and other
agents; what isn't on disk doesn't survive a crash or compaction. Write
findings and decisions there as you make them, with the alternatives you
rejected, and commit where it is version-controlled. Source edits go in the
source checkout, not the work directory.

This work item's artifacts go in the work directory; project-wide reference
goes in the knowledge base. Keep raw files (traces, HARs, dumps, build output)
out of the work directory, which syncs through git: record the excerpt that
carries the finding.

The agent that started a work item owns its state; leave it alone unless
your brief says otherwise.

## Maintain the Work Directory

Its `AGENTS.md` orients a delegated agent arriving cold: the goal, the artifact
layout, and what is settled versus still moving. Keep it current as the work
shifts, following `/creative-writing-skills:qi-layer`.

Decisions scoped to one change go with it, in its commit message or a note
beside what they explain; structural decisions go in the work directory. When
the plan shifts during execution, log the shift in `DIVERGENCE/`. Reviewers
check alignment against it, and knowledge capture mines it.
