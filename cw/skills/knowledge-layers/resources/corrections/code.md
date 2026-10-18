# Corrections in a Codebase

In a code project, record **Enforced by** with one of these kinds, strongest
first, and name the artifact so a reader can find it:

| Kind | What it means |
|---|---|
| `architecture: <what changed>` | The wrong way no longer exists: one owner per piece of state, one supported way per task, internals hidden so the wrong import fails, the old way deleted |
| `type: <type>` | The bad state can't be written |
| `lint: <rule>` or `ci: <check>` | A check fails, and its error names the file, type, or function to use instead |
| `test: <path>` | A test fails when the behavior breaks |
| `permission: <agent> <rule>` | A tool rule in the agent profile blocks the action |
| `doc: <file>` | A written rule in `AGENTS.md`, a skill, or an agent prompt |
| `none` | Nothing |

Record a check as enforcement only after it has failed on a real past
mistake, replayed. A test that still passes when its behavior breaks
enforces nothing; record the class as `doc` or `none` until it's fixed.

A row with `architecture` or `type` usually means the mistake can no longer
happen. Delete it once nothing can reintroduce the old way.
