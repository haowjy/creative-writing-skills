"""Reviewed local source identity relocation; remote layout is a separate plan."""
from dataclasses import dataclass, asdict
from pathlib import Path
import copy

from .google import fingerprint
from .index import Diagnostic, resolve
from .layout import plan_layout
from .sources import snapshot
from .state import StateStore, read_json
from .storage import load_index


@dataclass(frozen=True)
class RebindPlan:
    index_id: str
    index_digest: str
    source_id: str
    old_path: str
    new_path: str
    source_hash: str
    remote_id: str
    desired_name: str
    desired_parent: str
    identities: dict
    bindings: dict

    @property
    def digest(self):
        return fingerprint(asdict(self))


def plan_rebind(index_path: Path, store: StateStore, source_id: str, root: str, relative_path: str, remote=None) -> RebindPlan:
    loaded = load_index(index_path)
    if loaded.model.id != store.index_id:
        raise Diagnostic('wrong_state', 'Index and state identities differ.', 'Use the correct index state.')
    if remote is not None:
        if getattr(remote, 'index_id', store.index_id) != store.index_id:
            raise Diagnostic('wrong_state', 'Remote adapter and index identities differ.', 'Use the correct index adapter.')
        store.bind_account(getattr(remote, 'identity', None))
    sources = resolve(loaded.model,index_path)
    target = next((s for s in sources if s.root == root and s.relative_path == relative_path),None)
    if target is None:
        raise Diagnostic('unselected_rebind', 'New source is not selected by this index.', 'Edit selection to include its new location before rebinding.')
    captured = snapshot(target.path)
    identities = read_json(store.path/'identities.json')
    bindings = read_json(store.path/'bindings.json')
    binding = bindings.get(source_id)
    if not binding or binding.get('kind') != 'file' or any(i.source_id == source_id for i in store.pending()):
        raise Diagnostic('invalid_rebind', 'Source binding is absent or has unfinished operations.', 'Recover or inspect the original binding first.')
    old_path = Path(binding['path'])
    try:
        old_path.lstat()  # A dangling symlink is still an occupied old path.
    except FileNotFoundError:
        pass
    except OSError:
        raise Diagnostic('rebind_old_path_unreadable', 'The old source path could not be checked.',
                         'Restore access and verify the relocation before rebinding.', str(old_path)) from None
    else:
        raise Diagnostic('rebind_old_path_present', 'The old source path still exists; this is not an unambiguous relocation.',
                         'Keep both files separately selected, or complete the intended move before rebinding. Do not delete either copy automatically.',
                         str(old_path), destination=str(target.path), operation='rebind')
    old_keys=[k for k,v in identities.items() if v==source_id and k.startswith('file:')]
    new_key=f'file:{root}:{relative_path}'
    if len(old_keys)!=1 or (new_key in identities and identities[new_key] == source_id):
        raise Diagnostic('rebind_identity_conflict', 'Old identity is ambiguous or source already uses this path.', 'Rebind before preview allocates a new identity; inspect any existing destination binding.')
    if new_key in identities:
        placeholder = identities[new_key]
        if (placeholder in bindings or any(i.source_id == placeholder for i in store.pending()) or remote is None):
            raise Diagnostic('rebind_identity_conflict','New path has a binding, pending write, or unverified remote ownership.','Inspect both identities; do not merge existing representations.')
        if any(item.get('appProperties',{}).get('source') == placeholder for item in remote.inventory()):
            raise Diagnostic('rebind_identity_conflict','The allocated new identity already owns a remote object.','Review both representations; never merge them by name or hash.')
    if target.storage != binding['storage']:
        raise Diagnostic('rebind_storage_change', 'Rebinding cannot also change storage mode.', 'Keep the original storage policy during source relocation.')
    updated_ids=dict(identities)
    del updated_ids[old_keys[0]]
    updated_ids[new_key]=source_id
    layout=plan_layout(loaded.model,sources,updated_ids)
    destination=next(d for d in layout.files if d.source_id==source_id)
    parent=bindings.get(destination.parent_id,{}).get('remote_id')
    if not parent:
        raise Diagnostic('rebind_parent_pending', 'New parent folder has no verified binding.', 'Create and verify the mirrored destination folder before rebinding.')
    updated=copy.deepcopy(bindings)
    changed=updated[source_id]
    changed.update(path=str(target.path),name=destination.name,parent=parent,layout_pending=True)
    changed['baseline']['local']['path']=root+'/'+relative_path
    return RebindPlan(store.index_id,loaded.digest,source_id,binding['path'],str(target.path),captured.digest,
                      binding['remote_id'],destination.name,parent,updated_ids,updated)


def apply_rebind(plan: RebindPlan, index_path: Path, store: StateStore, expected_digest: str, root: str, relative_path: str, remote=None):
    with store.lock():
        fresh=plan_rebind(index_path,store,plan.source_id,root,relative_path,remote)
        if fresh.digest != expected_digest or fresh.digest != plan.digest:
            raise Diagnostic('stale_rebind', 'Source or state changed after rebind review.', 'Preview and authorize the new rebind plan.')
        store.claim((Path(fresh.new_path),))
        store.commit_records({'identities.json':fresh.identities,'bindings.json':fresh.bindings})
        return dict(rebound=True,source_id=plan.source_id,remote_id=plan.remote_id,layout_pending=True)
