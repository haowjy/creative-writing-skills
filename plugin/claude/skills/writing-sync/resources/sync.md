# Sync commands

`sync` reads Google and prints a folder/file plan plus digest. No Google
writes. `sync --apply --plan-digest DIGEST` authorizes that exact plan. A
changed plan fails. Both take `--state-home`; `--config-home` selects the
auth directory.

Review every operation. `pending` → [recovery](recovery.md).

## Scope

`sync --source SOURCE_UUID` (repeat `--source`) limits writes to those items.
UUIDs come from the full preview. The scoped plan includes each item and its
ancestor folders. Review that plan, then the same `--source` list with
`--apply --plan-digest DIGEST`.

A folder UUID is that folder and its ancestors, not descendants. Use file
UUIDs for content. Omit `--source` for the whole index.

Works with `--initialize` and `--folders-only`; selected UUIDs must exist in
that mode's plan. Unknown UUIDs and empty scope fail; they do not fall back
to everything. Scope limits writes, not reads: index-wide ownership and
inventory checks still run. Uninitialized link targets are not added to the
write scope.

## Initialize then populate

New converted set: [first sync](first-sync.md).
`sync --initialize` creates empty Doc identities and folders. Ordinary `sync`
populates them. Two digests.

`sync --folders-only` creates missing parent folders without source Docs.
Use when a later rebind needs parents bound first.

## Results

Per-file: `source_id`, `source`, `destination`, `operation`, `status`,
`reason`, `detail`, `action`, and `operation_id` when journaled. Destination
is a remote ID, or parent/name for an unconfirmed create. Process exit is not
a substitute for checking each status. Steady state: `verified`, then `noop`.
