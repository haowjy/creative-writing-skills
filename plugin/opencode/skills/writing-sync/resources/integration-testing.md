# Disposable integration testing

Maintainer test, not user sync. Explicit permission before any Google stage.
Never point this at real writing or the human-annotated research Doc.

`tests/live_integration.py` uses production services and a synthetic index.
`--research-token` is a separate probe token; do not copy it onto a production
profile or print it. Users: [Google setup](google-auth-setup.md).

```sh
python /path/to/skills/writing-sync/tests/live_integration.py seed --run /external/new-fixture
python /path/to/skills/writing-sync/tests/live_integration.py initialize --run /external/new-fixture --research-token /private/probe-token.json --apply
python /path/to/skills/writing-sync/tests/live_integration.py sync --run /external/new-fixture --research-token /private/probe-token.json --apply
python /path/to/skills/writing-sync/tests/live_integration.py edit-remote --run /external/new-fixture --research-token /private/probe-token.json --apply
python /path/to/skills/writing-sync/tests/live_integration.py sync --run /external/new-fixture --research-token /private/probe-token.json --apply
```

`seed` refuses an existing directory. Later stages reuse that index; do not
regenerate identities. Save each stage's result before repeating the same
stage name. Pending: runner `inspect` / `recover`. Do not repeat initialize.
After returns verify, `sync` must be all no-op. Compare original bytes, HTML
comments, text line endings, EPUB member payloads. Runner does not delete
Google resources.

Styled fixture, **new directory**: `seed-styled`, `initialize`, `sync`,
`edit-styled`, `sync`, `sync`, `verify-styled`. `edit-styled` changes one
word per Doc. `verify-styled` writes `styled-verification.json`. Run
EPUBCheck on source and returned EPUB separately.

After simple four-format no-op: `rebind-file` renames `notes/a.md` →
`notes/a-renamed.md`, reviewed rebind + `restore-layout`. Same Doc ID.
Attempt marker is written before the local rename; reruns refused. Do not
rename it back.

`replace-original` then `replace-doc`: reviewed `replace-storage` each way.
One-shot. Uncertain create → recover, not replay.

Original-file: `seed-original` adds `e.bin` with an original-storage
override. Sync, local-edit, sync, `edit-original`, sync. Separate evidence
from Docs conversion.

`make-conflict` diverges disposable `b.txt` both sides. Ordinary sync must
report `both_changed`. `resolve-conflict` is reviewed accept-remote.

`add-comment` puts one unanchored comment on disposable `c.html` and changes
local HTML. Sync must report `annotations_protected`. Leave the comment.

Large Unicode: `cancel-large` cancels after the first batch. Then
`resume-large --operation JOURNAL_UUID`. First checkpoint must not be
replayed.

After a fresh four-format no-op: `lost-batch-repair` expands synthetic
`b.txt`, discards the second batch receipt, then reviewed `repair-batches`.
One-shot. Leaves the expanded file.

`folder-layout`: new four-format fixture. Before initialize, create
`notes/left` and `notes/right`; move `a.md`/`b.txt` into left,
`c.html`/`d.epub` into right. Stage moves `left` under `right`, requires a
folder conflict, restores via `restore-layout`, then renames/restores the
managed root. Child Doc IDs unchanged. Attempt marker prevents replay.

`stale-original`: saved pre-edit ETag, expect HTTP 412 and unchanged
bytes **and** metadata. One-shot. Never target a Doc or an irreplaceable
file.

`seed-nested` adds `notes/level1/level2/g.md` linking to `../../a.md`.
`verify-nested` is read-only; writes `nested-verification.json`. Needs
verified `a.md` already in the fixture.

`move-nested` (existing nested fixture): one conditional remote
move/rename of `g.md` → `level1/g-moved.md`. Ordinary `sync` must report
`remote_structure_changed`. Then `restore-nested` for the production
`restore-layout` plan. Do not replay the move probe.

`repair-created-layout --operation JOURNAL_UUID` / `repair-created-content --operation JOURNAL_UUID`:
production recovery on a disposable Doc. Content-verified / wrong title vs
wrong content. Do not create another object. Uncertain response → `recover`.

Cyclic links: `seed-cyclic --run /external/new-cyclic-fixture` (new
directory). Two Markdown files pointing at each other. `initialize` (folder
plus two empty identities), then `sync`. Do not content-sync first.
`verify-cyclic` is read-only; writes `cyclic-verification.json`.

EPUBCheck (no Google):

```sh
/external/venv/bin/python /path/to/skills/writing-sync/tests/epub_conformance.py \
  --java /external/jre/bin/java \
  --jar /external/epubcheck/epubcheck.jar \
  --output /external/new-conformance-results
```

Nonexistent output directory. Java and EPUBCheck are not sync dependencies.
Keep the EPUBCheck `lib/` next to the JAR. Gate: clean reports for the three
valid EPUBs plus the expected missing-navigation error on the negative
control.
