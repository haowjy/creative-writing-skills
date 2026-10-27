# drive-sync

CLI for the Google Drive destination. JSON on stdout. Preview, then apply
the digest you reviewed. `--apply` without `--plan-digest` is an error.

Install from the skill folder into its own environment:

```sh
UV_PROJECT_ENVIRONMENT=/external/drive-sync-venv uv sync --locked --no-editable --project /path/to/writing-sync
/external/drive-sync-venv/bin/drive-sync --help
```

Details: [installation](../resources/installation.md). Indexes, sources,
tokens, and state stay outside this tree. Don't print client or token JSON.

```sh
drive-sync --index /external/drive.yaml ...
```

`--config-home` if the OAuth profile isn't under `~/.config/drive-sync`.
`--state-home` if bindings shouldn't use the default state directory. Keep
those flags the same for every command on an index.

## Auth

Desktop OAuth, `drive.file` only. [Google setup](../resources/google-auth-setup.md).

```sh
drive-sync auth login --profile personal --client /external/client.json
# prints {"event":"open_browser","url":"..."} then waits for the callback

drive-sync auth pick-folder --profile personal --client /external/client.json
# JSON includes folder_id — set that as destination_parent on a root

drive-sync auth status --profile personal
drive-sync auth logout --profile personal
```

Over SSH, forward the callback port first (`--port`, default 8765).

## Index

```sh
drive-sync --index /external/drive.yaml index create
drive-sync --index /external/drive.yaml index show
drive-sync --index /external/drive.yaml index preview
drive-sync --index /external/drive.yaml index edit --expected-digest DIGEST --save --edits '[
  {"operation":"set","path":["roots","notes"],"value":{"path":"/external/notes","destination_name":"Notes"}},
  {"operation":"append","path":["selection","include"],"value":{"root":"notes","path":".","glob":"**/*.md"}}
]'
```

`show` returns the digest `edit` needs. `--save` writes configuration only.

## Sync

[First sync](../resources/first-sync.md): conversion check, initialize empty
Docs, populate, then expect no-ops.

```sh
drive-sync conversion capabilities
drive-sync --index /external/drive.yaml conversion check

drive-sync --index /external/drive.yaml sync --initialize
drive-sync --index /external/drive.yaml sync --initialize --apply --plan-digest DIGEST

drive-sync --index /external/drive.yaml sync
drive-sync --index /external/drive.yaml sync --apply --plan-digest DIGEST

drive-sync --index /external/drive.yaml sync --source SOURCE_UUID
drive-sync --index /external/drive.yaml sync --folders-only
```

`--source` limits writes to that item and its parent folders. Repeat the flag
for several UUIDs. A pending file is not permission to initialize again.

## Conflicts and recovery

```sh
drive-sync --index /external/drive.yaml conflict inspect --source SOURCE_UUID
drive-sync --index /external/drive.yaml conflict resolve --source SOURCE_UUID --choice keep-local
drive-sync --index /external/drive.yaml conflict resolve --source SOURCE_UUID --choice keep-local --apply --plan-digest DIGEST
```

`--choice` is `keep-local`, `accept-remote`, `restore-layout`, or
`replace-storage`.

```sh
drive-sync --index /external/drive.yaml state recover
drive-sync --index /external/drive.yaml source rebind --source SOURCE_UUID --root notes --path moved.md
drive-sync --index /external/drive.yaml source preview-return --source SOURCE_UUID
```

The rest of the repair commands (`resume-batches`, `repair-created-layout`,
…) are in [recovery](../resources/recovery.md).

## Code

`cli.py` prints JSON. Sync/auth/conversion/recovery are importable functions
(`application.py`, `auth.py`, …). Google I/O is `google.py`. Bindings and
journals are `state.py`, on disk next to the user's state home, not in this
repo.

Tests: `../tests`. Fake Drive unless you opt into a live runner.
