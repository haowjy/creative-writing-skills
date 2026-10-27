# First sync

CLI installed, profile authorized, index selection saved. Existing Drive
folder first: [destination parent](destination-parent.md).

Keep `--index`, `--state-home`, and `--config-home` the same for every command.
`--state-home` optional if the default is fine. `--config-home` required if the
profile is not under the default config directory.

1. `conversion check` (offline). `supported: true` is a local rendering gate,
   not Google fidelity. Read [conversion limits](conversion-limits.md) before
   converted storage.
2. Preview `sync --initialize`. Apply with
   `sync --initialize --apply --plan-digest DIGEST`. Empty Docs and folders,
   not reading copies. If someone edits an incomplete Doc, the tool blocks
   instead of overwriting it.
3. Preview ordinary `sync`. Apply that second digest. Review every operation.
4. Inspect every file result. `pending` → [recovery](recovery.md). Do not
   repeat initialize or create.
5. Preview `sync` again. Success is all `noop`.

A changed plan fails authorization. Preview again; do not reuse a stale digest.
