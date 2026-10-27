"""Reviewed replacement of a partial native push, retaining every prior attempt."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
import uuid

from .batch_execution import run_sequence, validate_record
from .batch_resume import guard_source
from .batching import BatchSegment, plan_batches
from .conversion import Rendering, Style, docs_requests
from .document_model import read_document
from .executor import FileResult, SyncResult, load_prepared, reconcile
from .folders import binding_map
from .google import DOC, fingerprint
from .index import Diagnostic, resolve
from .native_effects import semantic
from .presentation import capture, content_styles, restore_requests
from .state import StateStore, private_directory, read_json, write_json
from .storage import load_index


@dataclass(frozen=True)
class BatchRepairPlan:
    index_id: str
    index_digest: str
    operation_id: str
    source_id: str
    remote_id: str
    preparation_hash: str
    binding_hash: str
    history_hash: str
    observation: dict
    before_text: str
    desired_text: str
    segments: tuple[BatchSegment, ...]

    @property
    def digest(self):
        return fingerprint(asdict(self))


def repair_batches(index_path: Path, remote, operation_id: str, expected_digest=None,
                   *, home=None, cancellation=None,
                   progress: Callable[[FileResult], None] | None = None) -> BatchRepairPlan | SyncResult:
    """Explicitly supersede observed partial content with the original staged goal.

    This is not resumption or automatic retry. A new reviewed snapshot authorizes
    a new sequence. Original and repair sequences remain as private evidence;
    only ordinary reconciliation may complete the original operation/baseline.
    """
    from .application import SyncEffects, state_home
    from .layout import plan_layout
    loaded = load_index(index_path)
    store = StateStore(home or state_home(), loaded.model.id)
    with store.lock():
        if getattr(remote, 'index_id', store.index_id) != store.index_id:
            raise Diagnostic('wrong_state', 'Remote adapter and index differ.', 'Use the matching adapter.')
        store.bind_account(remote.identity)
        intent = next((i for i in store.pending() if i.id == operation_id), None)
        if intent is None or intent.kind != 'push':
            raise Diagnostic('repair_ineligible', 'No pending native push matches.', 'Run normal recovery first.')
        prepared = load_prepared(store, intent)
        binding = prepared.binding
        if (binding.get('storage') != 'google-doc' or not binding.get('batch_segments')
                or binding.get('effect_kind') or binding.get('remote_id') != intent.remote_id):
            raise Diagnostic('repair_ineligible', 'This is not a staged native batch push.', 'Inspect the original journal.')
        guard_source(index_path, prepared)
        sources = resolve(loaded.model, index_path)
        if not any(str(s.path) == binding['path'] and s.storage == 'google-doc' for s in sources):
            raise Diagnostic('stale_repair_source', 'Staged source is no longer selected.', 'Restore the reviewed selection.')
        original = read_json(store.journals / (intent.id + '.batches') / 'sequence.json')
        validate_record(original)
        specification = dict(file_id=intent.remote_id, segments=binding['batch_segments'], initial=binding['prior_remote'])
        if original['specification_hash'] != fingerprint(specification):
            raise Diagnostic('repair_invalid_preparation', 'Original checkpoint and preparation differ.', 'Restore the correct state; do not edit hashes.')
        directory = store.journals / (intent.id + '.batch-repairs')
        history = [original]
        if directory.exists():
            for path in sorted(directory.glob('*.json')):
                record = read_json(path)
                sequence_id = str(uuid.UUID(record['sequence_id']))
                sequence_path = store.journals / (sequence_id + '.batches') / 'sequence.json'
                history.append(record)
                if sequence_path.exists():
                    sequence = read_json(sequence_path)
                    validate_record(sequence)
                    history.append(sequence)
        observed = remote.observe_document(intent.remote_id)
        model = read_document(observed)
        metadata = observed.metadata
        if (metadata.get('id') != intent.remote_id or metadata.get('mimeType') != DOC
                or metadata.get('appProperties', {}).get('source') != intent.source_id
                or metadata.get('name') != binding['name'] or metadata.get('parents') != [binding['parent']]):
            raise Diagnostic('repair_identity_mismatch', 'Remote identity or layout differs from the staged push.', 'Reconcile identity/layout before content repair.')
        if model.snapshot.comments or model.snapshot.suggestions or not model.snapshot.annotations_readable:
            raise Diagnostic('annotations_protected', 'Annotations prevent partial-content replacement.', 'Review annotations without overwriting them.')
        comparable = model.styles
        if 'presentation_v1' in binding:
            capture(observed.document)  # Validate before excluding spacing fields.
            comparable = content_styles(model.styles)
        if any(s.kind == 'unrepresentable' for s in comparable):
            raise Diagnostic('repair_unsupported_content', 'Observed formatting cannot be preserved for review.', 'Inspect the remote document without flattening it.')
        desired = Rendering(binding['format'], binding['text'], tuple(Style(**s) for s in binding['styles']))
        if semantic(desired.text, desired.styles) != prepared.outcome_hash:
            raise Diagnostic('repair_invalid_preparation', 'Staged content differs from its intended hash.', 'Restore the original preparation.')
        if (semantic(model.text, comparable) == prepared.outcome_hash
                and ('presentation_v1' not in binding or capture(observed.document) == binding['presentation_v1'])):
            raise Diagnostic('repair_unnecessary', 'Desired content already exists.', 'Use state recover; no replacement is needed.')
        batch = docs_requests(desired, tab_id=model.tab_id,
                              revision=model.snapshot.revision, old_end=model.end_index)
        batch['requests'].extend(restore_requests(binding.get('presentation_v1'), model.tab_id))
        segments = plan_batches(batch)
        plan = BatchRepairPlan(store.index_id, loaded.digest, intent.id, intent.source_id,
                               intent.remote_id, fingerprint(asdict(prepared) | {'payload': prepared.payload.hex()}),
                               fingerprint(binding_map(store).get(intent.source_id)), fingerprint(history),
                               asdict(observed), model.text, desired.text, segments)
        if expected_digest is None:
            return plan
        if expected_digest != plan.digest:
            raise Diagnostic('stale_batch_repair', 'Partial content, source or repair history changed after review.', 'Preview and authorize the current replacement plan.')
        guard_source(index_path, prepared)
        layout = plan_layout(loaded.model, sources, read_json(store.path / 'identities.json'))
        effects = SyncEffects(layout, sources, store, remote, lambda: load_index(index_path).digest)
        if cancellation is None or not cancellation.is_set():
            sequence_id = str(uuid.uuid4())
            private_directory(directory)
            attempt = directory / (sequence_id + '.json')
            evidence = dict(sequence_id=sequence_id, plan=asdict(plan), authorized_digest=plan.digest, status='attempting')
            write_json(attempt, evidence)  # Full observed version retained before any write.
            try:
                run_sequence(store, sequence_id, intent.remote_id, segments, asdict(model.snapshot),
                             remote, lambda: guard_source(index_path, prepared), cancellation=cancellation)
            except Exception:
                pass  # No replay. A new partial replacement requires a new reviewed plan.
            result = reconcile(store, effects, intent, prepared)
            write_json(attempt, evidence | {'status': result.status, 'result': asdict(result)})
        else:
            result = reconcile(store, effects, intent, prepared)
        outcome = SyncResult((result,), bool(cancellation is not None and cancellation.is_set()))
    if progress is not None:
        progress(result)
    return outcome
