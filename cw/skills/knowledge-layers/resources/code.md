# Knowledge Layers in a Code Project

How the layers' truth maps onto branches, merges, and shipped code.

- **Colocated docs follow their branch.** `AGENTS.md` and `.context/`
  describe the checkout that contains them. Update them in the same branch as
  the code change and let the merge carry both; with parallel PRs in flight,
  each branch documents itself.
- **The KB doesn't wait for code.** A settled decision is KB truth the moment
  it's made, merged or not. Where the code hasn't converged on it yet,
  colocated docs describe current behavior and flag the divergence; never
  describe the intended system as if it were built.
- **`docs/` describes shipped behavior**, updated when the change ships to
  users.
- **Code is ground truth for what's built.** When code and a doc disagree
  about what the code does, the doc is stale: say so, and fix or flag it.
- **Deferred work** in `.context/TODO` and `FUTURE` names the affected path
  and the concrete follow-up; a TODO comment in code needs a matching entry
  or an issue.
