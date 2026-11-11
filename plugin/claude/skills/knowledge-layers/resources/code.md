# Knowledge Layers in a Code Project

How the layers' truth maps onto branches, merges, and shipped code.

- **A rule local to one module is a contract,** not an invariant: it changes
  with the design and lives in that module's `AGENTS.md` or `.context/`.
- **Colocated docs follow their branch.** `AGENTS.md` and `.context/`
  describe the checkout that contains them. Update them in the same branch as
  the code change and let the merge carry both; with parallel PRs in flight,
  each branch documents itself.
- **The KB doesn't wait for code.** What the human chose is KB truth the
  moment they choose it, merged or not. Where the code hasn't converged on it yet,
  colocated docs describe current behavior and flag the divergence; never
  describe the intended system as if it were built.
- **Code is ground truth for what's built.** When code and a doc disagree
  about what the code does, the doc is stale: say so, and fix or flag it.
- **Deferred work** in `.context/TODO` and `FUTURE` names the affected path
  and the concrete follow-up; a TODO comment in code needs a matching entry
  or an issue.
- **Current choices live beside the code.** Error codes, names, timers,
  sizes, ordering, and how a PR builds a feature are current choices. They go
  in `.context/` or an architecture page as the current implementation, not
  as a KB rule or in an `AGENTS.md`. PR numbers and branch names stay out
  of status lines.
