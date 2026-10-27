# Recovery and conflicts

`--index` required. `--state-home` and `--config-home` as used for sync.
Back up the state directory; tokens cannot restore baselines. Never delete
state, journals, or attempt markers to retry a write.

## `state recover`

After a pending or uncertain result. Reads remote state; never repeats a
write. One matching object plus the intended verified content advances a
baseline. Zero/multiple matches, mixed content, unreadable state, or missing
preparation stay pending.

Ctrl-C during apply: exit 130. Check top-level `cancelled` and per-file
statuses. A forced kill cannot clean up; recover after restart.

## Conflicts

`conflict inspect --source UUID` stages private local/base/remote review
files. Prints paths and hashes, not source text. For Docs, `remote.txt` is
semantic evidence, not a file you paste over Markdown or EPUB.

`conflict resolve --source UUID --choice keep-local` (or `accept-remote`)
previews a two-sided content plan. Apply with `--apply --plan-digest DIGEST`.
Cannot bypass missing state, moved objects, annotations, or conversion
findings. Does not rewrite a baseline to hide a conflict.

Native `accept-remote` uses the last verified source, not the conflicting
local prose. Local bytes stay as backup. Changed comments, frontmatter, or
protected structure block; reconcile those by hand.

Remote move/rename: `--choice restore-layout` restores local-authoritative
name and parent without replacing content. Local source moves use rebind,
not this.

## Rebind

After a local move, update selection if needed, then:

```sh
drive-sync --index /external/drive.yaml source rebind --source UUID --root ROOT --path NEW_RELATIVE_PATH
```

New path must be selected; parent folder already bound. Missing parents:
reviewed `sync --folders-only` first. Old path must be absent on preview and
apply. An existing file, directory, or dangling symlink blocks; a copy is
not a relocation. If the old path reappears, preview again. Do not delete
either copy to bypass.

Rebind updates local bindings only. Then a separately reviewed
`restore-layout` applies the new remote name/parent.

`wrong_account` / `unverified_account`: use the original profile. Do not
overwrite `account.json` or switch profiles.

## Missing source

Missing old path plus a new selected path blocks create until resolved.
Move → rebind. Intentional removal of an unrelated new file:

```sh
drive-sync --index /external/drive.yaml state acknowledge-missing --source UUID
```

Records acknowledged absence. Remote object and baselines stay. The
configured root must still be available. Cannot hide pending writes or a
path that still exists (including a dangling symlink).
`source_presence_unreadable` is not "missing."

## Storage replacement

After an index storage-mode change:

```sh
drive-sync --index /external/drive.yaml conflict resolve --source UUID --choice replace-storage
```

Creates a new representation. Keeps the old remote object and binding
history. Later sync uses the new binding. Pending migration → recover, not
another create.

## Rebaseline

Missing baseline, identities intact, local and remote already agree:

```sh
drive-sync --index /external/drive.yaml state rebaseline --source UUID
```

Repairs local baseline records. Does not write Google or source content.
Divergent versions are a conflict, not a baseline repair. A lost identity
map needs a backup, not title matching.

## Inventory and read-back errors

- `invalid_inventory`: listing cannot establish what exists. Restore API
  access and preview again. Not an empty folder. Do not reset identities or
  create again.
- `invalid_metadata` / `invalid_document`: bound-object read failed. Retry
  the read. Do not recreate the object.
- `creation_not_found` / `ambiguous_identity`: operation-marked candidate
  missing or duplicated.
- `remote_layout_mismatch`: object exists, title/parent differs. Keep the
  journal; use layout repair. Content mismatch → content repair.

## Repair commands

Journal UUID from the pending result's `operation_id`. Preview, then
`--apply --plan-digest DIGEST`. `repair_already_attempted`: recover, do not
delete the attempt record.

Already-created Doc, content verified, wrong title/parent:

```sh
drive-sync --index /external/drive.yaml state repair-created-layout --operation JOURNAL_UUID
```

Already-created pending Doc, wrong content:

```sh
drive-sync --index /external/drive.yaml state repair-created-content --operation JOURNAL_UUID
```

Review the proposed replacement. Not a merge. Does not create a new Doc.

Native push that is actually unchanged vs the pre-write snapshot:

```sh
drive-sync --index /external/drive.yaml state close-unchanged --operation JOURNAL_UUID
```

Does not change content or baselines. Preview ordinary sync before a new
attempt.

Partial large native push:

```sh
drive-sync --index /external/drive.yaml state resume-batches --operation JOURNAL_UUID
```

Keep source and index unchanged. Lost write response, remote still matches
the pre-write snapshot: the plan may include `close_unchanged_attempt`.
Authorize that digest; do not invent a receipt.

Partial document that matches neither checkpoint nor intended final:

```sh
drive-sync --index /external/drive.yaml state repair-batches --operation JOURNAL_UUID
```

Replaces observed text with the staged source rendering. **Not a merge.**
Review `before_text`, `desired_text`, and `observation`. Interrupted repair:
`state recover` first, then a **new** repair-batches preview. Old digest is
invalid.

## Other blocks

- `unsupported_source_permissions`: setuid/setgid/sticky. Inspect; do not
  clear them to force a sync. A mode change between snapshot and replace
  also blocks.
- `corrupt_state` / `invalid_state`: restore the record from backup. Do not
  pick a duplicate key or regenerate identities. Path is named; contents
  are not echoed.
- `invalid_etag`: get a fresh metadata guard. Never `*` and never edit the
  journal.
- `invalid_annotations`: comments response unusable. Fresh preview later.
  Not an empty comment list. Do not discard comments.

Per-file results: `source_id`, `source`, `destination`, `operation`,
`status`, `reason`, `detail`, `action`, `operation_id`. Process exit is not
enough. `pending` means follow `action`.
