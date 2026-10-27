# Destination parent folder

`drive.file` cannot see a user-created folder until the user opens it with
`auth pick-folder`. Pasting a folder URL does not grant access. Do not
widen the Drive scope.

1. `auth status` for the same profile the index uses.
2. Picker API enabled on the same Cloud project as the Desktop OAuth client.
3. Over SSH, forward the callback port first:
   [Google setup](google-auth-setup.md).
4. `auth pick-folder` with that profile, client path, and port. Open the
   `open_browser` URL. Same Google account as login.
5. Click the folder once so the row is highlighted, then Select/Insert. Do
   not double-click or use the expand chevron. If Select is missing,
   highlight the folder name and look at the bottom of the picker.
6. JSON `folder_id` is the grant. From `index show`, take the digest, then
   `index edit --expected-digest DIGEST --save` to set it as the root's
   `destination_parent`. Saving the index does not move Drive objects.

If the mirrored root does not exist yet, the next initialize/create places it
inside that parent.

If it already exists (usually in My Drive), preview `sync`. Expect `conflict`
with `folder_changed` on the root. Preview
`conflict resolve --source ROOT_UUID --choice restore-layout`, then apply
that digest. That moves the existing folder; it does not recreate identities.

Verify: preview `sync` again, all `noop`, root parents include the granted id.
