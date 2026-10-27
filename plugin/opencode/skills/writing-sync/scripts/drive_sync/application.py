"""Index-to-plan application composition; no CLI or presentation dependencies."""
from dataclasses import dataclass
from pathlib import Path
import os

from .folders import folder_plan
from .index import resolve
from .layout import plan_layout
from .state import StateStore, read_json, write_json
from .storage import load_index
from .sync_plan import file_plan
from .planner import SyncPlan
from .scoping import ScopedEffects, scoped_plan


@dataclass(frozen=True)
class Preview:
    folders: SyncPlan
    files: SyncPlan


def state_home() -> Path:
    return Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'drive-sync'


def preview_sync(index_path: Path, remote, *, home: Path | None = None,
                 source_ids: frozenset[str] | None = None) -> Preview:
    loaded = load_index(index_path)
    sources = resolve(loaded.model, index_path)
    store = StateStore(home or state_home(), loaded.model.id)
    with store.lock():
        store.bind_account(remote.identity)
        store.claim(tuple(source.path for source in sources))
        path = store.path / 'identities.json'
        if not path.exists() and remote.inventory():
            from .index import Diagnostic
            raise Diagnostic('missing_state', 'This index already owns remote objects but source identities are missing.', 'Restore private state or perform reviewed recovery; do not allocate replacement identities.')
        identities = read_json(path) if path.exists() else {}
        known_ids = set(identities.values())
        unknown = [item for item in remote.inventory()
                   if item.get('appProperties', {}).get('source') not in known_ids]
        if unknown:
            from .index import Diagnostic
            raise Diagnostic('incomplete_state', 'Remote ownership markers are absent from the local identity map.', 'Restore missing identity state before selecting or creating new copies.')
        layout = plan_layout(loaded.model, sources, identities)
        # Local UUID allocation is persisted even for preview; no remote writes.
        write_json(path, identities)
        folders = folder_plan(layout, store, remote, loaded.digest)
        files = file_plan(loaded.digest, layout, sources, store, remote)
        scoped = scoped_plan(SyncPlan(store.index_id, loaded.digest, folders.operations + files.operations), layout, source_ids)
        folder_ids = {o.source_id for o in folders.operations}
        return Preview(SyncPlan(store.index_id, loaded.digest, tuple(o for o in scoped.operations if o.source_id in folder_ids)),
                       SyncPlan(store.index_id, loaded.digest, tuple(o for o in scoped.operations if o.source_id not in folder_ids)))


class SyncEffects:
    """Route folder/original/native operations without a universal plugin API."""
    def __init__(self, layout, sources, store, remote, current_digest):
        from .folders import FolderEffects
        from .original_effects import OriginalEffects
        from .native_effects import NativeEffects
        self.layout, self.sources, self.store, self.remote = layout, sources, store, remote
        self.current_digest = current_digest
        self.folder = FolderEffects(layout, store, remote, current_digest)
        self.original = OriginalEffects(layout, sources, store, remote, current_digest)
        self.native = NativeEffects(layout, sources, store, remote, current_digest)
        self.folder_ids = {f.id for f in layout.folders}

    def route(self, source_id):
        if source_id in self.folder_ids:
            return self.folder
        return self.original if self.original.by_id[source_id].storage == 'original' else self.native

    def refresh_plan(self, plan):
        self.folder.expected_index_digest = plan.index_digest
        self.original.expected_digest = plan.index_digest
        self.native.expected_digest = plan.index_digest
        digest = self.current_digest()
        folders = folder_plan(self.layout, self.store, self.remote, digest)
        files = file_plan(digest, self.layout, self.sources, self.store, self.remote)
        return SyncPlan(self.store.index_id, digest, folders.operations + files.operations)

    def prepare(self, operation):
        return self.route(operation.source_id).prepare(operation)

    def guard(self, operation):
        return self.route(operation.source_id).guard(operation)

    def mutate(self, operation, prepared, intent):
        return self.route(operation.source_id).mutate(operation, prepared, intent)

    def observe(self, intent, prepared):
        if prepared.binding.get('effect_kind') == 'initialize':
            from .initialization import InitializationEffects
            return InitializationEffects(self).observe(intent, prepared)
        if prepared.binding.get('effect_kind') == 'layout':
            from .layout_effects import LayoutEffects
            return LayoutEffects(self).observe(intent, prepared)
        return self.route(intent.source_id).observe(intent, prepared)


def combined_plan(preview: Preview) -> SyncPlan:
    return SyncPlan(preview.files.index_id, preview.files.index_digest,
                    preview.folders.operations + preview.files.operations)


def apply_reviewed(index_path: Path, remote, authorization, *, home: Path | None = None,
                   progress=None, cancellation=None, source_ids: frozenset[str] | None = None):
    from .executor import apply_sync
    loaded = load_index(index_path)
    sources = resolve(loaded.model, index_path)
    store = StateStore(home or state_home(), loaded.model.id)
    with store.lock():
        store.bind_account(remote.identity)
        identities = read_json(store.path / 'identities.json')
        layout = plan_layout(loaded.model, sources, identities)
        # Reject new IDs not present in the reviewed preview; no implicit save.
        persisted = read_json(store.path / 'identities.json')
        if identities != persisted:
            from .index import Diagnostic
            raise Diagnostic('stale_plan', 'Selection acquired new identities since preview.', 'Preview and authorize the new plan.')
        plan = SyncPlan(store.index_id, loaded.digest,
                        folder_plan(layout, store, remote, loaded.digest).operations +
                        file_plan(loaded.digest, layout, sources, store, remote).operations)
    effects = SyncEffects(layout, sources, store, remote, lambda: load_index(index_path).digest)
    effects.native.cancellation = cancellation
    return apply_sync(scoped_plan(plan, layout, source_ids), authorization, store,
                      ScopedEffects(effects, layout, source_ids), progress=progress, cancellation=cancellation)


def recover_sync(index_path: Path, remote, *, home: Path | None = None):
    """Reconcile known pending effects without replaying any remote mutation."""
    from .executor import recover
    loaded = load_index(index_path)
    sources = resolve(loaded.model, index_path)
    store = StateStore(home or state_home(), loaded.model.id)
    with store.lock():
        store.bind_account(remote.identity)
        identities = read_json(store.path / 'identities.json')
        layout = plan_layout(loaded.model, sources, identities)
    effects = SyncEffects(layout, sources, store, remote, lambda: load_index(index_path).digest)
    return recover(store, effects)


def resolve_reviewed(index_path: Path, remote, source_id: str, choice: str,
                     authorization=None, *, home: Path | None = None, cancellation=None, progress=None):
    from .resolution import resolution_plan, ResolutionEffects
    from .executor import apply_sync
    loaded = load_index(index_path)
    sources = resolve(loaded.model, index_path)
    store = StateStore(home or state_home(), loaded.model.id)
    with store.lock():
        store.bind_account(remote.identity)
        identities = read_json(store.path / 'identities.json')
        layout = plan_layout(loaded.model, sources, identities)
        current = SyncPlan(store.index_id,loaded.digest,folder_plan(layout,store,remote,loaded.digest).operations + file_plan(loaded.digest, layout, sources, store, remote).operations)
        plan = resolution_plan(current, source_id, choice)
    if authorization is None:
        return plan
    base_effects = SyncEffects(layout, sources, store, remote, lambda: load_index(index_path).digest)
    base_effects.native.cancellation = cancellation
    if choice == 'restore-layout':
        from .layout_effects import LayoutEffects
        base_effects = LayoutEffects(base_effects)
    effects = ResolutionEffects(base_effects, source_id, choice)
    return apply_sync(plan, authorization, store, effects, cancellation=cancellation, progress=progress)


def initialize_documents(index_path: Path, remote, authorization=None, *, home: Path | None = None,
                         cancellation=None, progress=None, source_ids: frozenset[str] | None = None):
    from .initialization import initialization_plan,InitializationEffects
    from .executor import apply_sync
    preview_sync(index_path,remote,home=home)  # Shared ownership/identity validation.
    loaded=load_index(index_path)
    sources=resolve(loaded.model,index_path)
    store=StateStore(home or state_home(),loaded.model.id)
    with store.lock():
        store.bind_account(remote.identity)
        identities=read_json(store.path/'identities.json')
        layout=plan_layout(loaded.model,sources,identities)
        folders=folder_plan(layout,store,remote,loaded.digest)
        files=initialization_plan(loaded.digest,layout,sources,store,remote)
        plan=scoped_plan(SyncPlan(store.index_id,loaded.digest,folders.operations+files.operations), layout, source_ids)
    if authorization is None:
        return plan
    effects=InitializationEffects(SyncEffects(layout,sources,store,remote,lambda:load_index(index_path).digest))
    return apply_sync(plan,authorization,store,ScopedEffects(effects, layout, source_ids),cancellation=cancellation,progress=progress)


def initialize_folders(index_path: Path, remote, authorization=None, *, home: Path | None = None,
                       cancellation=None, progress=None, source_ids: frozenset[str] | None = None):
    from .folders import FolderEffects
    from .executor import apply_sync
    preview_sync(index_path,remote,home=home)
    loaded=load_index(index_path)
    sources=resolve(loaded.model,index_path)
    store=StateStore(home or state_home(),loaded.model.id)
    with store.lock():
        store.bind_account(remote.identity)
        layout=plan_layout(loaded.model,sources,read_json(store.path/'identities.json'))
        plan=scoped_plan(folder_plan(layout,store,remote,loaded.digest), layout, source_ids)
    if authorization is None:
        return plan
    effects = FolderEffects(layout,store,remote,lambda:load_index(index_path).digest)
    return apply_sync(plan,authorization,store,ScopedEffects(effects, layout, source_ids),cancellation=cancellation,progress=progress)
