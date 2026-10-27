# Installation

Python 3.11+ on POSIX. Locked CLI into its own environment:

```sh
UV_PROJECT_ENVIRONMENT=/external/drive-sync-venv uv sync --locked --no-editable --project /path/to/skills/writing-sync
/external/drive-sync-venv/bin/drive-sync --help
```

Use that binary. Do not import from the skill source. Indexes, sources, state,
and OAuth profiles stay outside the skill. Install does not authorize Google
writes.

```sh
/external/drive-sync-venv/bin/python -m unittest discover -s /path/to/skills/writing-sync/tests
```

Passing tests does not mean the user's files convert.

Reinstall isolation (fake Drive, new fixture directory, no source `PYTHONPATH`):

```sh
/external/drive-sync-venv/bin/python /path/to/skills/writing-sync/tests/portability_check.py seed /external/reinstall-fixture
UV_PROJECT_ENVIRONMENT=/external/drive-sync-venv uv sync --locked --no-editable --reinstall-package independent-drive-sync --project /path/to/skills/writing-sync
/external/drive-sync-venv/bin/python /path/to/skills/writing-sync/tests/portability_check.py verify /external/reinstall-fixture
```

Keep the fixture at the same absolute path. Copying it is a relocation, not
this check. For Python 3.11, a second `UV_PROJECT_ENVIRONMENT` with
`uv sync --locked --no-editable --python 3.11`.
