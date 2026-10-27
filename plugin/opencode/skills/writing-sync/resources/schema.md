# Index schema (version 1)

User configuration, not credentials or bindings. Prefer CLI edits. Hand-edited
YAML gets the same validation. Unknown fields, duplicate keys, unsafe YAML,
and other versions fail.

```yaml
version: 1
kind: drive-sync
id: 590b7d30-bc08-45e3-aee3-f6bbfdac6342
auth: personal
roots:
  notes:
    path: /external/notes
    destination_name: Notes
    destination_parent: 1F3D4GWjbWumHn3HdECIHBVW0b2aBzIzL
selection:
  include:
    - root: notes
      path: .
      glob: "**/*"
  files: []
  exclude:
    - root: notes
      glob: "private/**"
policy:
  default_storage: google-doc
  formats: [markdown, text, html, epub]
  overrides:
    - root: notes
      glob: "originals/**"
      storage: original
```

## Fields

- `version`: integer `1`.
- `kind`: exactly `drive-sync`.
- `id`: UUID from `index create`. Keep it. Changing it does not migrate remote
  ownership.
- `auth`: profile name (letters, digits, hyphen, underscore).
- `roots`: simple names → `destination_name` and exactly one of `path` or
  `env` (`env` is an environment variable holding the path). Optional
  `destination_parent`: Drive folder id from `auth pick-folder`; without it,
  the root is created in My Drive. See
  [destination parent](destination-parent.md). Relative `path` is from the
  index directory. Destination names must be unique in the index.
- `selection.include`: `{root, path, glob}`. `path` is a directory; `glob` is
  relative to it.
- `selection.files`: exact `{root, path}` files.
- `selection.exclude`: `{root, glob}` on root-relative paths. Exclusions win
  over individually selected files.
- `policy.default_storage`: `google-doc` or `original`.
- `policy.formats`: `markdown`, `text`, `html`, `epub`. Does not exclude
  unmatched types; use original storage or `exclude`.
- `policy.overrides`: `{root, glob, storage}` on root-relative paths. Storage
  only, not selection. Conflicting values fail; no last-match-wins.

All shown top-level keys are required. Empty mappings/lists are valid.
Selectors: relative POSIX paths, no `..`. `*` one segment, `**` zero or more.
Symlinks, nonregular files, overlapping roots: rejected.
`source_scan_failed` names an unreadable directory and stops; a partial scan
is not an empty tree.

Only ancestors of selected files become folders. Remote names keep source
extensions. Local layout wins; a remote move is a conflict. Removed
selections keep their remote copies. No deletion either side.

Storage-mode change after first sync is a conflict:
`conflict resolve --choice replace-storage`. Relocation:
[recovery](recovery.md). Do not change UUIDs or edit bindings.
