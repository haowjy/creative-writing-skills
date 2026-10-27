"""Exact-digest reviewed resumption of staged native batch sequences."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from .batch_execution import close_unchanged_attempt, recover_sequence, run_sequence, observe
from .batching import BatchSegment
from .executor import Cancellation, FileResult, load_prepared, reconcile, SyncResult
from .folders import binding_map
from .google import fingerprint
from .index import Diagnostic, resolve
from .sources import snapshot
from .state import StateStore, read_json
from .storage import load_index


@dataclass(frozen=True)
class ResumePlan:
    index_id: str
    index_digest: str
    operation_id: str
    source_id: str
    remote_id: str
    completed_batches: int
    total_batches: int
    checkpoint_hash: str
    preparation_hash: str
    binding_hash: str
    source_hash: str
    close_unchanged_attempt: bool = False

    @property
    def digest(self):
        return fingerprint(asdict(self))


def guard_source(index_path, prepared):
    binding = prepared.binding
    if load_index(index_path).digest != binding['batch_index_digest']:
        raise Diagnostic('stale_batch_index', 'Index differs from the staged batch plan.', 'Restore or explicitly reconcile the staged configuration; no batch was sent.')
    current = snapshot(Path(binding['path']))
    if (current.digest != prepared.before_hash or current.inode != binding['inode']
            or current.device != binding['device']):
        raise Diagnostic('stale_batch_source', 'Source differs from the staged batch payload.', 'Retain both versions and reconcile the partial document; no batch was sent.')


def resume_batches(index_path, remote, operation_id, expected_digest=None, *, home=None,
                   cancellation: Cancellation | None = None,
                   progress: Callable[[FileResult], None] | None = None) -> ResumePlan | SyncResult:
    from .application import SyncEffects, state_home
    from .layout import plan_layout
    loaded = load_index(index_path)
    sources = resolve(loaded.model, index_path)
    store = StateStore(home or state_home(), loaded.model.id)
    with store.lock():
        store.bind_account(remote.identity)
        intent = next((i for i in store.pending() if i.id == operation_id), None)
        if intent is None or intent.kind != 'push':
            raise Diagnostic('no_batch_resume', 'No pending content push matches this operation.', 'Inspect the journal and use normal recovery first.')
        prepared = load_prepared(store, intent)
        binding = prepared.binding
        if not binding.get('batch_segments') or binding.get('storage') != 'google-doc':
            raise Diagnostic('no_batch_resume', 'This operation has no staged native batch sequence.', 'Use normal recovery instead.')
        guard_source(index_path, prepared)
        if not any(str(s.path) == binding['path'] for s in sources):
            raise Diagnostic('missing_batch_source', 'Staged source is no longer selected.', 'Restore the reviewed source selection.')
        path = store.journals / (intent.id + '.batches') / 'sequence.json'
        record = recover_sequence(path, remote, review_unchanged=True)
        specification = {'file_id': binding['remote_id'], 'segments': binding['batch_segments'],
                         'initial': binding['prior_remote']}
        if record['specification_hash'] != fingerprint(specification):
            raise Diagnostic('changed_batch_specification', 'Checkpoint and staged preparation differ.', 'Inspect the preserved operation; do not resume mismatched payloads.')
        _, current = observe(remote, binding['remote_id'])
        expected = record['verified'][-1]['after'] if record['verified'] else binding['prior_remote']
        if current != expected:
            raise Diagnostic('batch_remote_changed', 'Remote changed after the last verified batch.', 'Review partial and remote versions before further writes.')
        plan = ResumePlan(store.index_id, loaded.digest, intent.id, intent.source_id,
                          binding['remote_id'], len(record['verified']), len(binding['batch_segments']),
                          fingerprint(record), fingerprint(asdict(prepared) | {'payload': prepared.payload.hex()}),
                          fingerprint(binding_map(store).get(intent.source_id)), prepared.before_hash,
                          record['inflight'] is not None)
        if expected_digest is None:
            return plan
        if expected_digest != plan.digest:
            raise Diagnostic('stale_batch_resume', 'Resume plan changed after review.', 'Preview and authorize the current resume digest.')
        layout = plan_layout(loaded.model, sources, read_json(store.path / 'identities.json'))
        effects = SyncEffects(layout, sources, store, remote, lambda: load_index(index_path).digest)
        if plan.close_unchanged_attempt and not (cancellation is not None and cancellation.is_set()):
            guard_source(index_path, prepared)
            close_unchanged_attempt(path, remote, plan.checkpoint_hash, plan.digest)
        try:
            run_sequence(store, intent.id, binding['remote_id'],
                         tuple(BatchSegment(**s) for s in binding['batch_segments']),
                         binding['prior_remote'], remote, lambda: guard_source(index_path, prepared),
                         reviewed_resume=True, cancellation=cancellation)
        except Exception:
            # Final reconciliation, never an automatic replay. A lost final
            # response can still have completed the entire desired document.
            pass
        result = reconcile(store, effects, intent, prepared)
        outcome = SyncResult((result,), bool(cancellation is not None and cancellation.is_set()))
    if progress is not None:
        progress(result)
    return outcome
