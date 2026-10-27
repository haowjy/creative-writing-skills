"""Index application services: compound drafts and guarded durable commits."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from io import StringIO
from pathlib import Path
from typing import Callable
import fcntl
import os
import tempfile

from ruamel.yaml import YAML
from .index import Diagnostic, Index, parse_index


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def decode(data: bytes) -> dict:
    yaml = YAML(typ="safe")
    yaml.allow_duplicate_keys = False
    try:
        raw = yaml.load(data.decode("utf-8"))
        def walk(value, ancestors):
            if isinstance(value, (dict, list)):
                if id(value) in ancestors:
                    raise ValueError("Cyclic YAML alias")
                for child in (value.values() if isinstance(value, dict) else value):
                    walk(child, ancestors | {id(value)})
        walk(raw, set())
        parse_index(raw)
        return raw
    except Diagnostic:
        raise
    except Exception:
        # Parser errors can contain source text; do not expose their raw message.
        raise Diagnostic("invalid_yaml", "Invalid or unsafe index YAML.", "Check YAML syntax, duplicate keys, aliases and schema.") from None


def encode(raw: dict) -> bytes:
    parse_index(raw)
    stream = StringIO()
    YAML().dump(raw, stream)
    return stream.getvalue().encode("utf-8")


@dataclass(frozen=True)
class LoadedIndex:
    model: Index
    raw: dict
    digest: str


@dataclass(frozen=True)
class Draft:
    raw: dict


@dataclass(frozen=True)
class Edit:
    """Set/remove a mapping field or append to a list, addressed by key path."""
    operation: str
    path: tuple[str, ...]
    value: object = None


def parse_edits(value: object) -> tuple[Edit, ...]:
    """Validate the external compound-edit representation for any interface."""
    action = "Use a JSON list of objects with operation, a nonempty string-key path list, and optional value."
    if not isinstance(value, list):
        raise Diagnostic("invalid_edit", "Compound edits must be a list.", action)
    result = []
    for item in value:
        if (not isinstance(item, dict) or not {"operation", "path"} <= item.keys()
                or item.keys() - {"operation", "path", "value"}
                or item["operation"] not in ("set", "remove", "append")
                or not isinstance(item["path"], list) or not item["path"]
                or any(not isinstance(key, str) or not key or "\x00" in key for key in item["path"])
                or (item["operation"] in ("set", "append") and "value" not in item)
                or (item["operation"] == "remove" and "value" in item)):
            raise Diagnostic("invalid_edit", "Malformed compound edit.", action)
        result.append(Edit(item["operation"], tuple(item["path"]), item.get("value")))
    return tuple(result)


def load_index(path: Path) -> LoadedIndex:
    data = path.read_bytes()
    raw = decode(data)
    return LoadedIndex(parse_index(raw), raw, digest(data))


def edit_draft(loaded: LoadedIndex, edits: tuple[Edit, ...]) -> Draft:
    raw = deepcopy(loaded.raw)
    for edit in edits:
        if not edit.path:
            raise Diagnostic("invalid_edit", "Edit path cannot be empty.", "Address a configuration field.")
        try:
            parent = raw
            for key in edit.path[:-1]:
                parent = parent[key]
            key = edit.path[-1]
            if edit.operation == "set":
                parent[key] = deepcopy(edit.value)
            elif edit.operation == "remove":
                del parent[key]
            elif edit.operation == "append":
                parent[key].append(deepcopy(edit.value))
            else:
                raise ValueError()
        except (KeyError, TypeError, AttributeError, ValueError):
            raise Diagnostic("invalid_edit", "Edit operation or path is invalid.", "Use set/remove on mappings or append on lists.") from None
    parse_index(raw)  # Validate the compound result, not intermediate states.
    return Draft(raw)


@contextmanager
def locked(path: Path):
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def atomic_write(path: Path, data: bytes, *, mode: int = 0o600, prepare_fd: Callable[[int], None] | None = None):
    """Replace durably; private by default, explicit ordinary source mode allowed."""
    if type(mode) is not int or mode < 0 or mode > 0o777:
        raise ValueError("Only ordinary permission bits are supported")
    fd, temp = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            if prepare_fd is not None:
                prepare_fd(stream.fileno())
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def commit(path: Path, draft: Draft, expected_digest: str | None) -> LoadedIndex:
    data = encode(draft.raw)
    with locked(path.with_name(path.name + ".lock")):
        if path.is_symlink():
            raise Diagnostic("unsafe_index", "Index is a symlink.", "Use a regular index file.")
        actual = digest(path.read_bytes()) if path.exists() else None
        if actual != expected_digest:
            raise Diagnostic("stale_index", "Index changed since it was loaded.", "Reload and review your edits again.", str(path))
        atomic_write(path, data)
    return LoadedIndex(parse_index(draft.raw), deepcopy(draft.raw), digest(data))
