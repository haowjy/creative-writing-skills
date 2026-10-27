---
name: shared-workspace
description: 'Use when a workspace has changes from other agents: safe orientation, preserving unfamiliar files.'
metadata:
  type: guardrail
---

# Shared Workspace

You may be working in a directory that contains human or other-agent work you
do not own. Treat unfamiliar files and edits as live work, not clutter.

Isolated workspaces reduce this risk, but they do not remove it: writers,
reviewers, prompt editors, and cleanup tasks may still operate in shared
directories.

Ownership is not always obvious. After compaction, interruption, or handoff,
you may lose memory of files you created earlier. Use the current task, caller
instructions, nearby artifacts, and file contents to infer ownership. When
ownership is still unclear, preserve the file and report the uncertainty.

## Orientation

Before editing:

1. Identify where your outputs belong.
2. Inspect nearby files enough to understand local conventions.
3. Notice existing modified, generated, or unfamiliar files before changing the
   directory.
4. Reconstruct ownership from task context and file evidence when memory is
   incomplete.

Orient to ownership, not cleanliness. A messy workspace may be active work.

## Safety Rules

- Preserve unfamiliar files and edits.
- Keep generated artifacts, scratch files, logs, and captures contained.
- If your task needs a clean environment, create an isolated workspace instead
  of cleaning the current one.
- If your work overlaps existing changes you do not understand, stop and report
  the conflict.
- If you cannot tell whether a file is yours after compaction or handoff, keep
  it and name the uncertainty in your report.

## Reporting

When you finish, report:

- files you intentionally changed
- generated artifacts or logs you left behind
- anything you avoided touching because ownership was unclear
