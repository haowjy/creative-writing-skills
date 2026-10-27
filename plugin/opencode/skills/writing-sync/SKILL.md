---
name: writing-sync
description: |
  Load when syncing selected local files to a remote reading copy, or bringing remote edits back into those files. Google Drive/Docs only.
metadata:
  type: reference
---

Run the installed CLI. Do not rewrite YAML or call the remote API by hand.
Never ask for token or client JSON contents. Saving the index does not write
remotely. Preview, then apply that digest.

A pending result is not permission to retry a create.

## Resources

- [installation](resources/installation.md)
- Google login, folder pick, SSH: [Google setup](resources/google-auth-setup.md)
- Index create/edit: [configuration](resources/configuration.md)
- Index fields: [schema](resources/schema.md)
- First push of a new selection: [first sync](resources/first-sync.md)
- Everyday preview/apply/scope: [sync](resources/sync.md)
- Place a mirrored root in an existing Drive folder: [destination parent](resources/destination-parent.md)
- Whether converted storage is safe to choose: [conversion limits](resources/conversion-limits.md)
- Pending writes, conflicts, missing sources, rebind: [recovery](resources/recovery.md)
