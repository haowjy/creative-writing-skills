"""Recoverable mirrored-folder creation through the shared executor.

Caller persists layout identities and authorizes the resulting plan before apply.
Existing folders are verified, never adopted from names or silently moved.
"""
from dataclasses import asdict
import json

from .executor import Observation, Prepared
from .google import FOLDER, fingerprint
from .index import Diagnostic
from .layout import Layout
from .planner import LocalSnapshot, RemoteSnapshot, Operation, SyncPlan
from .state import StateStore, read_json
from .creation_identity import unique_created_object


def binding_map(store: StateStore) -> dict:
    path = store.path / 'bindings.json'
    return read_json(path) if path.exists() else {}


def destination_parent(layout: Layout, folder) -> str | None:
    return dict(layout.destination_parents).get(folder.root) if folder.parent_id is None else None


def planned_parent(layout: Layout, folder, bindings: dict) -> str | None:
    if folder.parent_id:
        parent = bindings.get(folder.parent_id, {}).get('remote_id')
        return parent if isinstance(parent, str) and parent else None
    return destination_parent(layout, folder)


def folder_plan(layout: Layout, store: StateStore, remote, index_digest: str) -> SyncPlan:
    inventory = remote.inventory()
    bindings = binding_map(store)
    pending = {i.source_id for i in store.pending()}
    operations = []
    for folder in layout.folders:
        local = LocalSnapshot(folder.id, folder.root + '/' + folder.relative_path,
                              fingerprint(asdict(folder)), 'folder-v1', 'original')
        matches = [m for m in inventory if m.get('appProperties', {}).get('source') == folder.id]
        binding = bindings.get(folder.id)
        reason, direction, action = 'new_folder', 'create', ''
        observed = None
        if len(matches) == 1:
            m=matches[0]
            observed=RemoteSnapshot(m['id'],'',fingerprint(dict(name=m.get('name'),parents=m.get('parents',[]),mime=m.get('mimeType'))),str(m.get('version','')))
        if folder.id in pending:
            reason, direction, action = 'unfinished_operation', 'conflict', 'Recover the pending folder create first.'
        elif binding:
            parent = planned_parent(layout, folder, bindings)
            expected = [parent] if parent else (binding.get('parents', []) if not folder.parent_id else None)
            valid = (len(matches) == 1 and matches[0]['id'] == binding.get('remote_id')
                     and matches[0].get('mimeType') == FOLDER and matches[0].get('name') == folder.name
                     and expected is not None and matches[0].get('parents', []) == expected)
            reason, direction, action = ('unchanged', 'noop', '') if valid else ('folder_changed', 'conflict', 'Restore or review the bound folder; do not recreate automatically.')
        elif matches:
            reason, direction, action = 'missing_folder_state', 'conflict', 'Restore state or review ownership-marker recovery; do not adopt by title.'
        operations.append(Operation(folder.id, direction, reason, action, local, observed, None))
    return SyncPlan(store.index_id, index_digest, tuple(operations))


class FolderEffects:
    def __init__(self, layout: Layout, store: StateStore, remote, current_index_digest):
        self.layout, self.store, self.remote = layout, store, remote
        self.current_index_digest = current_index_digest
        self.folders = {folder.id: folder for folder in layout.folders}
        self.expected_index_digest = None

    def refresh_plan(self, plan):
        self.expected_index_digest = plan.index_digest
        return folder_plan(self.layout, self.store, self.remote, self.current_index_digest())

    def prepare(self, operation):
        folder = self.folders[operation.source_id]
        bindings = binding_map(self.store)
        parent = planned_parent(self.layout, folder, bindings)
        if folder.parent_id and not parent:
            raise Diagnostic('parent_pending', 'Parent folder has not been verified.', 'Recover or create its parent before continuing.')
        payload = dict(name=folder.name, parent=parent, source_id=folder.id)
        return Prepared(folder.id, None, fingerprint(payload), json.dumps(payload).encode(),
                        dict(kind='folder', root=folder.root, relative_path=folder.relative_path))

    def guard(self, operation):
        if self.current_index_digest() != self.expected_index_digest:
            raise Diagnostic('stale_index', 'Index changed during execution.', 'Restore the index before writes.')
        matches = [m for m in self.remote.inventory() if m.get('appProperties', {}).get('source') == operation.source_id]
        if matches:
            raise Diagnostic('folder_exists', 'Ownership inventory changed before create.', 'Refresh the plan or recover state; do not create another folder.')

    def mutate(self, operation, prepared, intent):
        payload = json.loads(prepared.payload)
        self.remote.create(payload['name'], FOLDER, payload['source_id'], intent.id, parent=payload['parent'])

    def observe(self, intent, prepared):
        payload = json.loads(prepared.payload)
        source = prepared.binding.get('root', '') + '/' + prepared.binding.get('relative_path', '')
        item = unique_created_object(self.remote, intent, FOLDER, source=source)
        parents = item.get('parents', [])
        if not isinstance(parents, list) or len(parents) != 1 or not isinstance(parents[0], str) or not parents[0]:
            raise Diagnostic('creation_layout_mismatch', 'Created folder has no unique verifiable parent.',
                             'Inspect the created folder and retain the journal; do not create a replacement.',
                             source, destination=item['id'], operation='read-back')
        # Root's My Drive parent is unknown before creation, but must be recorded
        # unambiguously. Child folders require their exact staged parent.
        actual = dict(name=item.get('name'), parent=None if payload['parent'] is None else parents[0],
                      source_id=intent.source_id)
        return (Observation(fingerprint(actual), dict(remote_id=item['id'], parents=parents)),)
