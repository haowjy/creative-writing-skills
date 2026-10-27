# Google OAuth setup

```sh
drive-sync auth login --profile personal --client /external/client.json
drive-sync auth pick-folder --profile personal --client /external/client.json
drive-sync auth status --profile personal
drive-sync auth logout --profile personal
```

Login prints `open_browser` with a URL, then waits. Open it in the user's
browser. Ctrl-C closes the listener. Login does not upload content.

Tokens: `$XDG_CONFIG_HOME/drive-sync/PROFILE/token.json` or
`~/.config/drive-sync/PROFILE/token.json`. `--config-home` replaces that
directory. Status is local credential presence. Logout deletes local tokens; it
does not revoke Google access or delete client JSON.

1. User's Google Cloud project.
2. Enable Drive API, Docs API, and Picker API.
3. OAuth consent screen. External app in Testing: add the user's account as a
   test user.
4. OAuth client type **Desktop app**, not Web application. JSON must have one
   `installed` section, no `web` section, no duplicate keys. Do not merge
   downloaded client files.
5. Download JSON outside the skill, e.g.
   `~/.config/drive-sync/personal/client.json` (dir `0700`, file `0600`). Ask
   for the path, never the contents.

Use only `https://www.googleapis.com/auth/drive.file`. Do not substitute
broader Drive/Documents scopes, a service account, rclone, or an API key.

Folder grant: [destination parent](destination-parent.md).

Over SSH, the browser's localhost is the user's machine. Forward before login
or pick-folder:

```sh
ssh -o ExitOnForwardFailure=yes -L 127.0.0.1:PORT:127.0.0.1:PORT USER@HOST
```

Same `PORT` as `--port` (default 8765). Testing-mode refresh tokens expire;
reauthorize instead of retrying writes.
