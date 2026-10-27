"""Local-authoritative mirrored folder planning, independent of Google transport."""
from dataclasses import dataclass
from pathlib import PurePosixPath
import uuid

from .index import Index, Source, Diagnostic


@dataclass(frozen=True)
class Folder:
    id: str
    root: str
    relative_path: str
    name: str
    parent_id: str | None


@dataclass(frozen=True)
class Destination:
    source_id: str
    root: str
    relative_path: str
    name: str
    parent_id: str


@dataclass(frozen=True)
class Layout:
    folders: tuple[Folder, ...]
    files: tuple[Destination, ...]
    destination_parents: tuple[tuple[str, str], ...] = ()


def plan_layout(index: Index, sources: tuple[Source, ...], identities: dict[str, str]) -> Layout:
    """Use persisted UUIDs; allocate only for genuinely new, selected identities.

    The caller persists the returned identity map before remote writes. Paths
    address bindings, not identity: rename/rebind moves the same UUID explicitly.
    """
    folders = {}
    files = []
    roots = {r.name: r for r in index.roots}
    def identity(key):
        if key not in identities:
            identities[key] = str(uuid.uuid4())
        return str(uuid.UUID(identities[key]))
    def folder(root, relative):
        key = (root, relative)
        if key not in folders:
            parent = None if relative == '.' else folder(root, str(PurePosixPath(relative).parent)).id
            name = roots[root].destination_name if relative == '.' else PurePosixPath(relative).name
            folders[key] = Folder(identity(f'folder:{root}:{relative}'), root, relative, name, parent)
        return folders[key]
    for source in sources:
        if source.root not in roots:
            raise Diagnostic('invalid_layout', 'Source references an unknown root.', 'Resolve the index again.')
        parent = folder(source.root, str(PurePosixPath(source.relative_path).parent))
        files.append(Destination(identity(f'file:{source.root}:{source.relative_path}'), source.root,
                                 source.relative_path, PurePosixPath(source.relative_path).name, parent.id))
    parents = tuple((root.name, root.destination_parent) for root in index.roots if root.destination_parent)
    return Layout(tuple(folders.values()), tuple(files), parents)


def rebind_identity(identities: dict[str, str], *, old_root: str, old_path: str,
                    new_root: str, new_path: str) -> dict[str, str]:
    old = f'file:{old_root}:{old_path}'
    new = f'file:{new_root}:{new_path}'
    if old not in identities or new in identities:
        raise Diagnostic('invalid_rebind', 'Old binding is absent or the new source already has an identity.', 'Inspect both bindings; do not merge identities by filename or hash.')
    result = dict(identities)
    result[new] = result.pop(old)
    return result
