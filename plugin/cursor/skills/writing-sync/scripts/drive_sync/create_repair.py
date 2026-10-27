"""Reviewed one-write repairs of an already-created, unverified native Doc."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from .document_model import read_document
from .executor import Cancellation, FileResult, SyncResult, load_prepared, reconcile
from .folders import binding_map
from .google import DOC, fingerprint
from .index import Diagnostic, resolve
from .native_effects import semantic
from .sources import snapshot
from .state import StateStore, write_json, private_directory
from .storage import load_index


@dataclass(frozen=True)
class CreatedRepairPlan:
    index_id: str
    index_digest: str
    operation_id: str
    source_id: str
    remote_id: str
    desired_name: str
    desired_parent: str
    metadata: dict
    etag: str
    remote_snapshot: dict
    preparation_hash: str
    binding_hash: str
    source_identity: tuple
    repair_kind: str
    before_text: str
    batch: dict | None

    @property
    def digest(self):
        return fingerprint(asdict(self))


def _report(result, progress):
    if isinstance(result, SyncResult) and progress is not None:
        for file in result.files:
            progress(file)
    return result


def repair_created_layout(index_path: Path, remote, operation_id: str, expected_digest=None, *, home=None,
                          cancellation: Cancellation | None = None,
                          progress: Callable[[FileResult], None] | None = None) -> CreatedRepairPlan | SyncResult:
    """Preview or make one conditional metadata write; never create or edit text."""
    return _report(_repair_created(index_path, remote, operation_id, expected_digest,
                   home=home, kind='layout', cancellation=cancellation), progress)


def repair_created_content(index_path: Path, remote, operation_id: str, expected_digest=None, *, home=None,
                           cancellation: Cancellation | None = None,
                           progress: Callable[[FileResult], None] | None = None) -> CreatedRepairPlan | SyncResult:
    """Replace supported observed text/styles with the staged create payload."""
    return _report(_repair_created(index_path, remote, operation_id, expected_digest,
                   home=home, kind='content', cancellation=cancellation), progress)


def _repair_created(index_path, remote, operation_id, expected_digest, *, home, kind, cancellation):
    from .application import SyncEffects, state_home
    from .layout import plan_layout
    from .state import read_json
    loaded = load_index(index_path)
    store = StateStore(home or state_home(), loaded.model.id)
    with store.lock():
        if getattr(remote, 'index_id', store.index_id) != store.index_id:
            raise Diagnostic('wrong_state', 'Remote adapter and index differ.', 'Use the correct index adapter.')
        store.bind_account(remote.identity)
        intent = next((i for i in store.pending() if i.id == operation_id), None)
        if intent is None or intent.kind != 'create':
            raise Diagnostic('repair_ineligible', 'No pending create matches this operation.', 'Use normal state recovery.')
        prepared = load_prepared(store, intent)
        binding = prepared.binding
        attempt = store.journals / (intent.id + '.repair') / (kind + '.json')
        if attempt.exists():
            raise Diagnostic('repair_already_attempted', 'This repair was already attempted.',
                             'Run state recover and inspect the retained attempt; do not replay a possibly applied write.')
        if (binding.get('kind') != 'file' or binding.get('storage') != 'google-doc'
                or binding.get('effect_kind') or not binding.get('parent')):
            raise Diagnostic('repair_ineligible', 'Only native file creates with a staged parent are supported.', 'Inspect the pending preparation.')
        sources = resolve(loaded.model, index_path)
        source = next((s for s in sources if str(s.path) == binding['path']), None)
        if source is None or source.storage != binding['storage']:
            raise Diagnostic('stale_repair_source', 'The staged source is not selected in the original mode.', 'Restore its selection before repair.')
        captured = snapshot(source.path)
        identity = lambda s: (s.digest, s.device, s.inode, s.mode)
        if (captured.digest != prepared.before_hash or captured.device != binding['device']
                or captured.inode != binding['inode']):
            raise Diagnostic('stale_repair_source', 'The staged source changed.', 'Retain both versions and review before repair.')
        matches = remote.inventory(operation_id=intent.id)
        if len(matches) != 1 or matches[0].get('appProperties', {}).get('source') != intent.source_id:
            raise Diagnostic('ambiguous_identity', 'Creation identity is not unique.', 'Inspect operation markers; never recreate by title.')
        file_id = matches[0]['id']
        observed = remote.observe_document(file_id)
        model = read_document(observed)
        if (observed.metadata.get('id') != file_id or observed.metadata.get('mimeType') != DOC
                or observed.metadata.get('appProperties', {}).get('source') != intent.source_id
                or observed.metadata.get('appProperties', {}).get('operation') != intent.id):
            raise Diagnostic('repair_ineligible', 'Observed representation does not match the staged identity.', 'Inspect without modifying it.')
        if model.snapshot.comments or model.snapshot.suggestions:
            raise Diagnostic('annotations_protected', 'Annotations prevent pending-create repair.', 'Review annotations without overwriting them.')
        content_matches = semantic(model.text, model.styles) == prepared.outcome_hash
        batch = None
        etag = ''
        if kind == 'layout':
            if not content_matches:
                raise Diagnostic('repair_content_mismatch', 'Content does not match the original create intent.',
                                 'Review repair-created-content first; layout-only repair cannot replace text.')
            metadata, etag = remote.metadata_guard(file_id)
            if metadata != observed.metadata:
                raise Diagnostic('remote_race', 'Metadata changed during repair preview.', 'Preview again.')
            if metadata.get('name') == binding['name'] and metadata.get('parents') == [binding['parent']]:
                raise Diagnostic('repair_unnecessary', 'Layout already matches the create intent.', 'Run state recover without another write.')
        else:
            if content_matches:
                raise Diagnostic('repair_unnecessary', 'Content already matches the create intent.',
                                 'Run state recover or preview repair-created-layout if the title/parent differs.')
            if any(s.kind == 'unrepresentable' for s in model.styles):
                raise Diagnostic('repair_unsupported_content', 'Observed formatting cannot be safely represented.',
                                 'Preserve and review the remote formatting; do not flatten it through this repair.')
            from .conversion import Rendering, Style, docs_requests
            from .google import validate_batch_limits
            desired = Rendering(binding['format'], binding['text'], tuple(Style(**s) for s in binding['styles']))
            if semantic(desired.text, desired.styles) != prepared.outcome_hash:
                raise Diagnostic('repair_invalid_preparation', 'Staged content differs from its intended hash.', 'Restore the correct preparation; never edit hashes to bypass verification.')
            batch = docs_requests(desired, tab_id=model.tab_id, revision=model.snapshot.revision, old_end=model.end_index)
            validate_batch_limits(batch)
            metadata = observed.metadata
        plan = CreatedRepairPlan(store.index_id, loaded.digest, intent.id, intent.source_id, file_id,
                                 binding['name'], binding['parent'], metadata, etag, asdict(model.snapshot),
                                 fingerprint(asdict(prepared) | {'payload': prepared.payload.hex()}),
                                 fingerprint(binding_map(store).get(intent.source_id)), identity(captured),
                                 kind, model.text, batch)
        if expected_digest is None:
            return plan
        if expected_digest != plan.digest:
            raise Diagnostic('stale_repair', 'Repair inputs changed since review.', 'Preview and approve the new digest.')
        if load_index(index_path).digest != loaded.digest or identity(snapshot(source.path)) != plan.source_identity:
            raise Diagnostic('stale_repair', 'Source or index changed before repair.', 'Preview again; no write was sent.')
        if cancellation is not None and cancellation.is_set():
            return SyncResult((FileResult(intent.source_id, 'pending', 'repair_cancelled',
                              'No repair write was sent; preview and authorize repair when ready.',
                              intent.id, str(source.path), file_id, 'repair-created-' + kind),), True)
        private_directory(attempt.parent)
        evidence = {'plan': asdict(plan), 'authorized_digest': expected_digest,
                    'observed_before': asdict(observed), 'status': 'attempting'}
        write_json(attempt, evidence)
        try:
            if kind == 'layout':
                remote.update_layout(file_id, name=plan.desired_name, parent=plan.desired_parent,
                                     before=metadata, etag=etag)
            else:
                remote.update_document(observed, batch)
        except Exception:
            pass  # One attempt only. Read-back, never replay, decides the outcome.
        if load_index(index_path).digest != loaded.digest or identity(snapshot(source.path)) != plan.source_identity:
            result = FileResult(intent.source_id, 'pending', 'stale_repair',
                                'Source or index changed; inspect the retained repair and run recovery.',
                                intent.id, str(source.path), file_id, 'create')
        else:
            layout = plan_layout(loaded.model, sources, read_json(store.path / 'identities.json'))
            effects = SyncEffects(layout, sources, store, remote, lambda: load_index(index_path).digest)
            result = reconcile(store, effects, intent, prepared)
        write_json(attempt, evidence | {'status': result.status, 'result': asdict(result)})
        return SyncResult((result,), bool(cancellation is not None and cancellation.is_set()))
