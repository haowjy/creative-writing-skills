# Conversion and return limits

Before converted storage on a new selection:

```sh
drive-sync conversion capabilities
drive-sync --index /external/drive.yaml conversion check
```

Both offline. `capabilities` lists implemented routes. `check` reads the
selected files. `supported: true` is a local rendering gate, not approval of
later Google edits.

| Format | What can return | What blocks |
| --- | --- | --- |
| Markdown | Uniquely mapped literal-text edits in the original bytes | Frontmatter, comments, markup, local link syntax stay local. Ambiguous correspondence, structural changes, edits across protected boundaries. |
| Plain text | UTF-8 with the source newline convention | Formatting that plain text cannot represent. |
| HTML | Uniquely mapped text edits in the original HTML | Tags, attributes, comments, unmapped whitespace stay. Scripts, CSS, assets, unsupported structures. Do not regenerate a DOM. |
| EPUB | Mapped XHTML text inside the original package | Spine order and unrelated members stay. Unsupported assets/layout, invalid packages, ambiguous mapping. |

Renderer findings decide support, not the file extension. Splitting or
reordering paragraphs, style changes, or new links are not the same as
replacing one unambiguous word. No lossless rich-document merge.

Paragraph spacing stays in Google. A spacing-only edit is a `noop`. Do not
use Drive's whole-file Markdown export/import as the round-trip.

## Preview a return

```sh
drive-sync --index /external/drive.yaml source preview-return --source SOURCE_UUID
```

Same validation as apply. Writes private review artifacts only
(`before.source`, `candidate.source`, `changes.json`, `source.diff` when
available). Prints paths and hashes, not source text. Does not change the
source or Google.

Two-sided conflict: `--accept-remote` previews that candidate. Still
inspection.

After a normal pull review: `sync --source SOURCE_UUID --apply --plan-digest DIGEST`.
After accept-remote: `conflict resolve --source SOURCE_UUID --choice accept-remote --apply --plan-digest DIGEST`.
Same `--index` and state/profile flags. Apply regenerates the candidate; it
does not trust a hand-edited review artifact. EPUB package timestamps may
change at apply (`candidate_may_change_at_apply`).

## Links, assets, annotations

- Local links need verified destination identities. First-time cross-links:
  reviewed `sync --initialize` before populate. Do not substitute `file://`
  or expand write scope.
- Converters do not fetch URLs or run scripts. EPUB ZIP members surviving is
  not proof the visual survived in Docs.
- Comments, suggestions, extra tabs, unrepresentable styles can block.
  Removing them is a human decision. An unreadable annotation response is
  not "no annotations."

Large or pathological inputs may fail with `conversion_resource_limit`. Do
not strip protected content to force success. Index fields cannot raise the
limits.

## Blocked conversion

Show path, finding code/reason, and action. Keep both copies. Pending or
conflict: [recovery](recovery.md). Do not strip comments, regenerate an EPUB,
or flatten HTML to pass a check.

Original-file storage: explicit [index override](schema.md). Already bound:
reviewed `replace-storage`, which keeps the old object. Original mode is
bytes, not an editable Doc.
