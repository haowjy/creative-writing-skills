"""Prepare the real guarded pull candidate for private review, without apply."""
from dataclasses import asdict, dataclass
from pathlib import Path
import uuid

from .candidate_review import describe_candidate
from .index import Diagnostic, resolve
from .layout import plan_layout
from .scoping import scoped_plan
from .sources import snapshot
from .state import StateStore, private_directory, read_json, write_json
from .storage import atomic_write, digest, load_index


@dataclass(frozen=True)
class ReturnReview:
    index_id: str
    source_id: str
    source: str
    destination: str
    directory: Path
    plan_digest: str
    before_hash: str
    candidate_hash: str
    format: str
    storage: str
    candidate_may_change_at_apply: tuple[str, ...] = ()
    resolution: str = 'pull'


def preview_return(index_path: Path, remote, source_id: str, *, home=None, accept_remote: bool = False) -> ReturnReview:
    from .application import SyncEffects, combined_plan, preview_sync, state_home
    from .resolution import resolution_plan
    initial = load_index(index_path)
    if getattr(remote, 'index_id', initial.model.id) != initial.model.id:
        raise Diagnostic('wrong_state', 'Adapter and index differ.', 'Use the matching index adapter.')
    scope = frozenset([source_id])
    plan = combined_plan(preview_sync(index_path, remote, home=home, source_ids=scope))
    if accept_remote:
        plan = resolution_plan(plan, source_id, 'accept-remote')
    operation = next(o for o in plan.operations if o.source_id == source_id)
    if operation.direction != 'pull':
        raise Diagnostic('return_review_ineligible', 'Source does not have a conflict-free planned pull.',
                         'Inspect the sync plan or conflict; this command cannot bypass conversion or conflict guards.',
                         operation.local.path if operation.local else '',
                         destination=operation.remote.file_id if operation.remote else '', operation='preview-return')
    loaded = load_index(index_path)
    store = StateStore(home or state_home(), loaded.model.id)
    with store.lock():
        if getattr(remote, 'index_id', store.index_id) != store.index_id:
            raise Diagnostic('wrong_state', 'Adapter and index differ.', 'Use the matching index adapter.')
        store.bind_account(remote.identity)
        sources = resolve(loaded.model, index_path)
        layout = plan_layout(loaded.model, sources, read_json(store.path / 'identities.json'))
        effects = SyncEffects(layout, sources, store, remote, lambda: load_index(index_path).digest)
        refreshed = effects.refresh_plan(plan)
        refreshed = resolution_plan(refreshed, source_id, 'accept-remote') if accept_remote else scoped_plan(refreshed, layout, scope)
        if refreshed.digest != plan.digest:
            raise Diagnostic('stale_plan', 'Return inputs changed during review.', 'Preview the return again.')
        source = effects.original.by_id[source_id]
        before = snapshot(source.path)
        prepared = effects.prepare(operation)  # Same candidate validation as apply.
        effects.guard(operation)
        if before.digest != prepared.before_hash or snapshot(source.path) != before:
            raise Diagnostic('source_race', 'Source changed while generating its candidate.', 'Preview the return again.', str(source.path))
        report = describe_candidate(before.data, prepared.payload, source.format)
        directory = private_directory(store.path / 'reviews' / str(uuid.uuid4()))
        atomic_write(directory / 'before.source', before.data)
        atomic_write(directory / 'candidate.source', prepared.payload)
        write_json(directory / 'changes.json', asdict(report))
        if report.diff is not None:
            atomic_write(directory / 'source.diff', report.diff.encode('utf-8'))
        result = ReturnReview(store.index_id, source_id, str(source.path), operation.remote.file_id,
                              directory, plan.digest, before.digest, digest(prepared.payload), source.format, source.storage,
                              ('EPUB modification timestamp and dependent ZIP checksums',)
                              if source.format == 'epub' and source.storage == 'google-doc' else (),
                              'accept-remote' if accept_remote else 'pull')
        write_json(directory / 'review.json', asdict(result) | {'directory': str(directory), 'applied': False})
        return result
