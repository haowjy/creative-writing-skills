"""Journaled application executor with narrow, injectable effect boundaries."""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
from typing import Callable, Protocol

from .index import Diagnostic
from .planner import Authorization, Operation, SyncPlan
from .state import Intent, StateStore, read_json, write_json


@dataclass(frozen=True)
class Prepared:
    """Immutable mutation payload staged by the format-aware preparation service.

    outcome_hash covers intended content and relevant structure. Adapter read-back
    uses the identical canonical representation; it must not return source hashes
    as a substitute for inspecting the destination.
    """
    source_id: str
    before_hash: str | None
    outcome_hash: str
    payload: bytes
    binding: dict


@dataclass(frozen=True)
class Observation:
    outcome_hash: str
    binding: dict


@dataclass(frozen=True)
class FileResult:
    source_id: str
    status: str
    reason: str
    action: str = ''
    operation_id: str | None = None
    source: str = ''
    destination: str = ''
    operation: str = ''
    detail: str = ''


@dataclass(frozen=True)
class SyncResult:
    files: tuple[FileResult, ...]
    cancelled: bool


class Cancellation(Protocol):
    def is_set(self) -> bool: ...


class Effects(Protocol):
    def refresh_plan(self, plan: SyncPlan) -> SyncPlan:
        """Refresh local, remote, configuration, account and baseline guards."""
        ...

    def prepare(self, operation: Operation) -> Prepared:
        """Stage and validate original-format candidate or remote payload, no writes."""
        ...

    def guard(self, operation: Operation) -> None:
        """Check current source/remote guards immediately before mutation."""
        ...

    def mutate(self, operation: Operation, prepared: Prepared, intent: Intent) -> None:
        """One guarded mutation; persist intent.id as remote creation marker.

        Do not retry any ambiguous write here, including creates. Return values
        from writes are never used as read-back verification.
        """
        ...

    def observe(self, intent: Intent, prepared: Prepared) -> tuple[Observation, ...]:
        """Fresh read-back; reconcile creates by ownership marker, not title.

        Zero or multiple matches remain pending. This method performs reads only.
        """
        ...


def _prepared_file(store: StateStore, intent: Intent):
    return store.journals / (intent.id + '.prepared.json')


def save_prepared(store: StateStore, intent: Intent, prepared: Prepared):
    if intent.kind == 'pull' and prepared.binding.get('prior_blob'):
        from .candidate_review import describe_candidate
        from .state import private_directory
        report = describe_candidate(store.load_blob(prepared.binding['prior_blob']),
                                    prepared.payload, prepared.binding.get('format', 'original'))
        directory = private_directory(store.journals / (intent.id + '.review'))
        write_json(directory / 'changes.json', asdict(report) | {
            'before_blob': prepared.binding['prior_blob'],
            'candidate_blob': store.save_blob(prepared.payload)})
    write_json(_prepared_file(store, intent), dict(source_id=prepared.source_id,
               before_hash=prepared.before_hash, outcome_hash=prepared.outcome_hash,
               payload_hash=store.save_blob(prepared.payload), binding=prepared.binding))


def load_prepared(store: StateStore, intent: Intent) -> Prepared:
    try:
        raw = read_json(_prepared_file(store, intent))
        prepared = Prepared(raw['source_id'], raw['before_hash'], raw['outcome_hash'],
                            store.load_blob(raw['payload_hash']), raw['binding'])
        if prepared.source_id != intent.source_id or prepared.outcome_hash != intent.desired:
            raise ValueError()
        return prepared
    except (OSError, ValueError, KeyError, TypeError):
        raise Diagnostic('missing_preparation', 'Pending operation has no valid staged payload.', 'Inspect the journal; do not retry this mutation.') from None


def reconcile(store: StateStore, effects: Effects, intent: Intent, prepared: Prepared) -> FileResult:
    result = _reconcile(store, effects, intent, prepared)
    binding = prepared.binding
    destination = result.destination or binding.get('remote_id') or intent.remote_id or ''
    if not destination and binding.get('name'):
        destination = f"{binding.get('parent', '')}/{binding['name']}"
    return replace(result, source=binding.get('path', ''), destination=destination,
                   operation=intent.kind)


def _reconcile(store: StateStore, effects: Effects, intent: Intent, prepared: Prepared) -> FileResult:
    try:
        observations = effects.observe(intent, prepared)
        if len(observations) != 1:
            return FileResult(intent.source_id, 'pending', 'ambiguous_identity',
                              'Inspect ownership matches; never blindly repeat a create.', intent.id)
        observed = observations[0]
        if observed.outcome_hash != intent.desired:
            return FileResult(intent.source_id, 'pending', 'unverified_outcome',
                              'Compare old, intended and observed states before any new write.', intent.id)
        # Preparation owns original bytes/converter metadata; observation supplies
        # fresh remote IDs/revisions and baseline exports after verification.
        store.verify(intent, observed.outcome_hash, dict(prepared.binding, **observed.binding))
        return FileResult(intent.source_id, 'verified', 'read_back_verified', operation_id=intent.id,
                          destination=observed.binding.get('remote_id', ''))
    except Diagnostic as exc:
        return FileResult(intent.source_id, 'pending', exc.code, exc.action, intent.id,
                          detail=exc.reason, destination=exc.destination)
    except Exception:
        # Errors may contain source text or credential-bearing transport details.
        return FileResult(intent.source_id, 'pending', 'verification_failed',
                          'Restore connectivity or inspect state, then run recovery.', intent.id)


def apply_sync(plan: SyncPlan, authorization: Authorization, store: StateStore,
               effects: Effects, *, progress: Callable[[FileResult], None] | None = None,
               cancellation: Cancellation | None = None) -> SyncResult:
    results = []
    cancelled = False
    def emit(result):
        operation = next(o for o in plan.operations if o.source_id == result.source_id)
        local = operation.local or (operation.baseline.local if operation.baseline else None)
        remote = operation.remote or (operation.baseline.remote if operation.baseline else None)
        result = replace(result, source=result.source or (local.path if local else ''),
                         destination=result.destination or (remote.file_id if remote else ''),
                         operation=result.operation or operation.direction)
        results.append(result)
        if progress is not None:
            progress(result)
    with store.lock():
        if store.index_id != plan.index_id:
            raise Diagnostic('wrong_state', 'State namespace does not match this plan.', 'Use the index-specific state directory.')
        if effects.refresh_plan(plan).digest != plan.digest:
            raise Diagnostic('stale_plan', 'Material plan inputs changed.', 'Preview again and authorize the new plan.')
        pending_sources = {i.source_id for i in store.pending()}
        # Validate all mutation permissions before the first write.
        for operation in plan.operations:
            if operation.direction in ('create', 'push', 'pull') and not authorization.permits(plan, operation):
                raise Diagnostic('unauthorized_plan', 'Authorization does not cover this exact plan.', 'Review and authorize the plan digest, sources and directions.')
        for operation in plan.operations:
            if cancellation is not None and cancellation.is_set():
                cancelled = True
                break
            if operation.source_id in pending_sources:
                emit(FileResult(operation.source_id, 'pending', 'unfinished_operation', 'Run recovery first.'))
                continue
            if operation.direction in ('noop', 'conflict'):
                emit(FileResult(operation.source_id, operation.direction, operation.reason, operation.action))
                continue
            try:
                prepared = effects.prepare(operation)
                if prepared.source_id != operation.source_id:
                    raise Diagnostic('wrong_preparation', 'Staged payload belongs to a different source.', 'Discard the plan and inspect preparation.')
                effects.guard(operation)
            except Diagnostic as exc:
                emit(FileResult(operation.source_id, 'conflict', exc.code, exc.action,
                                source=exc.source, destination=exc.destination,
                                operation=exc.operation, detail=exc.reason))
                continue
            if cancellation is not None and cancellation.is_set():
                cancelled = True
                break
            intent = store.begin(operation.source_id, operation.direction, prepared.before_hash,
                                 prepared.outcome_hash, operation.remote.file_id if operation.remote else None)
            save_prepared(store, intent, prepared)
            write_failure = None
            try:
                effects.mutate(operation, prepared, intent)
            except Diagnostic as exc:
                write_failure = exc
            except Exception:
                pass  # Any failure can have side effects. Reconcile before deciding.
            result = reconcile(store, effects, intent, prepared)
            if result.status == 'pending' and write_failure is not None:
                result = replace(result, detail=f'{write_failure.code}: {write_failure.reason}')
            emit(result)
    return SyncResult(tuple(results), cancelled or bool(cancellation is not None and cancellation.is_set()))


def recover(store: StateStore, effects: Effects) -> SyncResult:
    results = []
    with store.lock():
        for intent in store.pending():
            try:
                prepared = load_prepared(store, intent)
            except Diagnostic as exc:
                results.append(FileResult(intent.source_id, 'pending', exc.code, exc.action, intent.id,
                                          destination=intent.remote_id or '', operation=intent.kind,
                                          detail=exc.reason))
                continue
            results.append(reconcile(store, effects, intent, prepared))
    return SyncResult(tuple(results), False)
