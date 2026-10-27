"""Reviewed missing-source acknowledgment without deletion or baseline changes."""
from dataclasses import dataclass, asdict
from pathlib import Path
from copy import deepcopy
from .folders import binding_map
from .google import fingerprint
from .index import Diagnostic, resolve_roots
from .state import StateStore
from .storage import load_index


@dataclass(frozen=True)
class MissingPlan:
    index_id: str
    index_digest: str
    source_id: str
    path: str
    root: str
    root_path: str
    root_device: int
    root_inode: int
    remote_id: str | None
    binding_hash: str
    action: str = 'Retain remote copy and baselines; acknowledge local absence only.'

    @property
    def digest(self) -> str:
        return fingerprint(asdict(self))


def missing_plan(index_path: Path, store: StateStore, source_id: str) -> MissingPlan:
    loaded = load_index(index_path)
    if loaded.model.id != store.index_id:
        raise Diagnostic('wrong_state', 'Index and state identities differ.', 'Use the correct index state.')
    bindings = binding_map(store)
    binding = bindings.get(source_id)
    if not binding or binding.get('kind') != 'file' or not binding.get('path'):
        raise Diagnostic('unknown_source', 'No complete file identity exists.', 'Inspect source bindings.')
    source = Path(binding['path'])
    roots = resolve_roots(loaded.model, index_path)
    matches = [(name, root) for name, root in roots.items() if root in source.parents]
    if not source.is_absolute() or len(matches) != 1:
        raise Diagnostic('missing_source_root', 'Bound source is outside the current configured roots.',
                         'Restore its original root configuration before acknowledging absence.', str(source))
    root_name, root = matches[0]
    # Include physical root identity in the reviewed plan, not just its pathname.
    try:
        root_stat = root.stat()
    except OSError:
        raise Diagnostic('missing_root', 'Source root became unavailable during review.',
                         'Restore access to the original root and preview again.', str(root)) from None
    if any(parent.is_symlink() for parent in source.parents):
        raise Diagnostic('unsafe_source', 'Source ancestry contains a symlink.',
                         'Restore the original directory tree before acknowledging absence.', str(source))
    try:
        source.lstat()
    except FileNotFoundError:
        pass
    except OSError:
        raise Diagnostic('source_presence_unreadable', 'The source path could not be checked for absence.',
                         'Restore access and preview again; unreadable is not missing.',
                         str(source), operation='acknowledge-missing') from None
    else:
        raise Diagnostic('source_present', 'The source path still exists.',
                         'Do not acknowledge a present source as missing.', str(source))
    if any(i.source_id == source_id for i in store.pending()):
        raise Diagnostic('pending_write', 'Source has an uncertain write.', 'Recover it before acknowledging removal.')
    return MissingPlan(store.index_id, loaded.digest, source_id, str(source), root_name,
                       str(root), root_stat.st_dev, root_stat.st_ino,
                       binding.get('remote_id'), fingerprint(binding))


def acknowledge_missing(index_path: Path, store: StateStore, source_id: str, expected_digest: str) -> dict:
    with store.lock():
        plan = missing_plan(index_path, store, source_id)
        if plan.digest != expected_digest:
            raise Diagnostic('stale_acknowledgment', 'Index, root or binding changed after review.',
                             'Preview missing-source acknowledgment again.')
        bindings = deepcopy(binding_map(store))
        bindings[source_id]['missing_acknowledged'] = True
        store.commit_records({'bindings.json': bindings})
        return dict(acknowledged=True, source_id=source_id, remote_deleted=False)
