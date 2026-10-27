"""Strict index schema and source selection; no Google or presentation dependency."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping
import os
from functools import lru_cache
import re
import uuid


class Diagnostic(ValueError):
    def __init__(self, code: str, reason: str, action: str, source: str = "",
                 *, destination: str = "", operation: str = ""):
        super().__init__(reason)
        self.code, self.reason, self.action, self.source = code, reason, action, source
        self.destination, self.operation = destination, operation

    def as_dict(self) -> dict:
        return dict(code=self.code, reason=self.reason, action=self.action, source=self.source,
                    destination=self.destination, operation=self.operation)


def fail(reason: str, source: str = "") -> None:
    raise Diagnostic("invalid_index", reason, "Correct the index and validate again.", source)


def fields(value, required: set[str], optional: set[str] = frozenset()) -> dict:
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        fail("Expected a mapping with string keys.")
    if required - value.keys() or value.keys() - required - optional:
        fail(f"Required fields: {sorted(required)}; allowed optional fields: {sorted(optional)}.")
    return value


def string(value) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        fail("Expected a nonempty string without NUL.")
    return value


def relative(value) -> str:
    value = string(value)
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        fail("Selectors must be relative POSIX paths without traversal.", value)
    return value


def sequence(value) -> list:
    if not isinstance(value, list):
        fail("Expected a list.")
    return value


@dataclass(frozen=True)
class Root:
    name: str
    location: str
    environment: bool
    destination_name: str
    destination_parent: str | None = None


@dataclass(frozen=True)
class Selector:
    root: str
    path: str = "."
    glob: str | None = None


@dataclass(frozen=True)
class Override:
    root: str
    glob: str
    storage: str


@dataclass(frozen=True)
class Index:
    id: str
    auth: str
    roots: tuple[Root, ...]
    includes: tuple[Selector, ...]
    files: tuple[Selector, ...]
    excludes: tuple[Selector, ...]
    default_storage: str
    formats: tuple[str, ...]
    overrides: tuple[Override, ...]


FORMATS = {".md": "markdown", ".markdown": "markdown", ".txt": "text",
           ".html": "html", ".htm": "html", ".epub": "epub"}


def _parse_index(raw: dict) -> Index:
    fields(raw, {"version", "kind", "id", "auth", "roots", "selection", "policy"})
    if type(raw["version"]) is not int or raw["version"] != 1 or raw["kind"] != "drive-sync":
        fail("Only version 1, kind drive-sync is supported; migrate other schemas explicitly.")
    try:
        identifier = str(uuid.UUID(string(raw["id"])))
    except ValueError:
        fail("Index id must be a UUID.")
    auth = string(raw["auth"])
    if not re.fullmatch(r"[A-Za-z0-9_-]+", auth):
        fail("Auth profile must be a simple name.")
    roots = []
    fields(raw["roots"], set(), set(raw["roots"]) if isinstance(raw["roots"], dict) else set())
    for name, value in raw["roots"].items():
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            fail("Root keys must be simple names.")
        fields(value, {"destination_name"}, {"path", "env", "destination_parent"})
        if ("path" in value) == ("env" in value):
            fail("A root needs exactly one of path or env.")
        parent = None
        if "destination_parent" in value:
            parent = string(value["destination_parent"])
            if not re.fullmatch(r"[A-Za-z0-9_-]+", parent):
                fail("destination_parent must be a Drive file id.")
        roots.append(Root(name, string(value.get("path", value.get("env"))),
                          "env" in value, string(value["destination_name"]), parent))
    names = {r.name for r in roots}
    if len({r.destination_name for r in roots}) != len(roots):
        fail("Destination root names must be unique.")

    def selectors(values, keys):
        result = []
        for value in sequence(values):
            fields(value, keys)
            if value["root"] not in names:
                fail("Selector references an unknown root.")
            result.append(Selector(value["root"], relative(value.get("path", ".")),
                                   relative(value["glob"]) if "glob" in value else None))
        return tuple(result)

    selection = fields(raw["selection"], {"include", "files", "exclude"})
    policy = fields(raw["policy"], {"default_storage", "formats", "overrides"})
    def storage(value):
        if value not in ("google-doc", "original"):
            fail("Storage must be google-doc or original.")
        return value
    formats = sequence(policy["formats"])
    if any(not isinstance(f, str) or f not in set(FORMATS.values()) for f in formats):
        fail("Unknown conversion format.")
    overrides = []
    for value in sequence(policy["overrides"]):
        fields(value, {"root", "glob", "storage"})
        if value["root"] not in names:
            fail("Override references an unknown root.")
        overrides.append(Override(value["root"], relative(value["glob"]), storage(value["storage"])))
    return Index(identifier, auth, tuple(roots),
                 selectors(selection["include"], {"root", "path", "glob"}),
                 selectors(selection["files"], {"root", "path"}),
                 selectors(selection["exclude"], {"root", "glob"}),
                 storage(policy["default_storage"]), tuple(formats), tuple(overrides))


def matches(path: str, pattern: str) -> bool:
    """Segment-aware glob: ** also matches zero complete segments."""
    parts, pats = PurePosixPath(path).parts, PurePosixPath(pattern).parts
    @lru_cache(maxsize=None)
    def match(i, j):
        if j == len(pats):
            return i == len(parts)
        if pats[j] == "**":
            return match(i, j + 1) or (i < len(parts) and match(i + 1, j))
        expression = re.escape(pats[j]).replace(r"\*", ".*").replace(r"\?", ".")
        return i < len(parts) and re.fullmatch(expression, parts[i]) is not None and match(i + 1, j + 1)
    return match(0, 0)


@dataclass(frozen=True)
class Source:
    root: str
    relative_path: str
    path: Path
    format: str | None
    storage: str


def resolve_roots(index: Index, index_path: Path, environment: Mapping[str, str] | None = None) -> dict[str, Path]:
    """Resolve available nonoverlapping roots without walking selected files."""
    environment = os.environ if environment is None else environment
    roots: dict[str, Path] = {}
    for root in index.roots:
        location = environment.get(root.location) if root.environment else root.location
        if not location:
            raise Diagnostic("missing_root", "Root environment variable is unset.", "Set the variable; do not treat this root as empty.", root.name)
        path = Path(location).expanduser()
        if not path.is_absolute():
            path = index_path.absolute().parent / path
        if any(p.is_symlink() for p in (path, *path.parents)):
            fail("Symlink roots are unsupported.", str(path))
        path = path.resolve()
        if not path.is_dir():
            raise Diagnostic("missing_root", "Source root is unavailable.", "Restore the root before syncing this scope.", str(path))
        if any(path == other or path in other.parents or other in path.parents for other in roots.values()):
            fail("Source roots overlap.", str(path))
        roots[root.name] = path
    return roots


def resolve(index: Index, index_path: Path, environment: Mapping[str, str] | None = None) -> tuple[Source, ...]:
    roots = resolve_roots(index, index_path, environment)
    result: dict[tuple[str, str], Source] = {}
    physical: dict[tuple[int, int], tuple[str, str]] = {}
    def add(root, path):
        rel = path.relative_to(roots[root]).as_posix()
        if any(e.root == root and matches(rel, e.glob) for e in index.excludes):
            return
        if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
            fail("Selected sources must be regular files, not symlinks.", str(path))
        modes = {o.storage for o in index.overrides if o.root == root and matches(rel, o.glob)}
        if len(modes) > 1:
            fail("Conflicting storage overrides.", rel)
        mode = next(iter(modes), index.default_storage)
        fmt = FORMATS.get(path.suffix.lower())
        if mode == "google-doc" and fmt not in index.formats:
            raise Diagnostic("unsupported_conversion", "Selected file has no enabled conversion format.", "Exclude it or select original storage explicitly.", str(path))
        metadata = path.stat()
        inode_key = (metadata.st_dev, metadata.st_ino)
        if inode_key in physical and physical[inode_key] != (root, rel):
            fail("Multiple selected paths are hard links to one writable source.", str(path))
        physical[inode_key] = (root, rel)
        result[root, rel] = Source(root, rel, path, fmt, mode)
    for selector in index.includes:
        base = roots[selector.root] / selector.path
        if any(p.is_symlink() for p in (base, *base.parents)) or not base.is_dir():
            fail("Included directory is missing or a symlink.", str(base))
        def unreadable(error):
            raise Diagnostic('source_scan_failed', 'The selected directory tree could not be read completely.',
                             'Restore directory access and preview again; do not treat a partial scan as an empty selection.',
                             str(error.filename or base), operation='resolve-selection') from None
        for directory, dirs, files in os.walk(base, followlinks=False, onerror=unreadable):
            for name in dirs + files:
                path = Path(directory) / name
                if path.is_symlink():
                    rel = path.relative_to(roots[selector.root]).as_posix()
                    if not any(e.root == selector.root and matches(rel, e.glob) for e in index.excludes):
                        fail("Selected tree contains a symlink.", str(path))
            for name in files:
                path = Path(directory) / name
                if matches(path.relative_to(base).as_posix(), selector.glob):
                    add(selector.root, path)
    for selector in index.files:
        add(selector.root, roots[selector.root] / selector.path)
    def natural(source):
        path = source.root + "/" + source.relative_path
        parts = tuple((0, int(p)) if p.isdigit() else (1, p.casefold())
                      for p in re.split(r"(\d+)", path))
        # Casefold and integer conversion collapse distinct POSIX names. Never
        # let filesystem enumeration order become the tie-breaker.
        return parts, path
    return tuple(sorted(result.values(), key=natural))


def parse_index(raw: dict) -> Index:
    """Public validation boundary: malformed types always yield diagnostics."""
    try:
        return _parse_index(raw)
    except Diagnostic:
        raise
    except (TypeError, KeyError, AttributeError, ValueError, RecursionError):
        fail("Index contains invalid field types or excessively nested values.")
