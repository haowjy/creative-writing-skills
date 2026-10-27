# Correcting in a Code Project

Code adds three levels. The order, strongest first:

1. **Architecture.** One owner per piece of state, one supported way per
   task. Hide internals so the wrong import fails. Replace hand-synced lists
   with one source of truth. Delete the old way and the dead code an agent
   would copy.
2. **Types**, so the bad state can't be written.
3. **A lint or CI check** whose error names the file, type, or function to
   use instead. Run it the same way locally and in CI.
4. **A test of the behavior.** Fix or delete any test that still passes when
   that behavior breaks, or fails when only internals change.
5. **A tool permission**, then **a written rule**, as in the skill.

Also look for classes in recent reverts, review comments, and comments that
explain a workaround.

An exception to a new check is a suppression on the offending line, with a
reason and the human's approval.

Record enforcement with the kinds in `/creative-writing-skills:knowledge-layers`
`resources/corrections/code.md`.
