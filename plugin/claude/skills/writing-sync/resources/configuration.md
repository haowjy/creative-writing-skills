# Configuration commands

```sh
drive-sync --index /external/drive.yaml index create
drive-sync --index /external/drive.yaml index show
drive-sync --index /external/drive.yaml index preview
```

`create` refuses to replace an existing index. `validate` checks schema;
`preview` also resolves sources. JSON on stdout.

`index edit --expected-digest DIGEST --edits JSON` previews compound changes.
`--save` commits configuration, not sync. DIGEST comes from `show`.

```json
[
  {"operation":"set","path":["roots","notes"],"value":{"path":"/external/notes","destination_name":"Notes","destination_parent":"GRANTED_FOLDER_ID"}},
  {"operation":"append","path":["selection","include"],"value":{"root":"notes","path":".","glob":"**/*"}}
]
```

Operations: `set`/`remove` on mapping keys, `append` on lists. Replace a whole
list with `set`. Each edit is `{operation, path}` with a nonempty string-key
`path`; `set`/`append` need `value`, `remove` omits it. Validation is on the
compound result. Concurrent saves fail rather than overwrite.

Fields: [schema](schema.md). Existing Drive folder:
[destination parent](destination-parent.md).

Relative roots resolve from the index directory, not the working directory.
Exclusions win over selections. Overrides change storage only; they do not
select files. Conflicting storage overrides fail. Selected unsupported files
need exclusion or explicit original storage. Symlinks and overlapping roots
are rejected.

Command errors: JSON on stderr with `code`, `reason`, and `action`. Usage
errors (missing `--plan-digest`) fail before authentication.
