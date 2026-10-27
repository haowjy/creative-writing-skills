"""Checkpointed native batch sequence, below final baseline verification.

Caller holds the index state lock and supplies exact-plan authorization. This
module never advances bindings/baselines and never retries an uncertain write.
"""
from dataclasses import asdict
from pathlib import Path
from typing import Callable
import uuid

from .batching import BatchSegment
from .document_model import read_document
from .google import fingerprint
from .index import Diagnostic
from .state import private_directory, read_json, write_json


def blocked(reason):
    raise Diagnostic('batch_sequence_pending', reason,
                     'Recover and review the persisted sequence; never replay an uncertain batch.')


def observe(remote, file_id):
    observation = remote.observe_document(file_id)
    model = read_document(observation)
    if model.snapshot.comments or model.snapshot.suggestions or not model.snapshot.annotations_readable:
        blocked('Annotations prevent continuing a partial document update.')
    return observation, asdict(model.snapshot)


def validate_record(record):
    """Reject corrupted/skipped checkpoint chains before any remote mutation."""
    try:
        specification = {k: record[k] for k in ('file_id', 'segments', 'initial')}
        if record['specification_hash'] != fingerprint(specification):
            raise ValueError()
        segments = tuple(BatchSegment(**s) for s in record['segments'])
        verified = record['verified']
        if not isinstance(verified, list) or len(verified) > len(segments):
            raise ValueError()
        before = record['initial']
        if before['file_id'] != record['file_id']:
            raise ValueError()
        entries = verified + ([record['inflight']] if record['inflight'] is not None else [])
        for index, entry in enumerate(entries):
            if index >= len(segments) or entry['segment'] != index or entry['before'] != before:
                raise ValueError()
            expected_hash = fingerprint(segments[index].bind_revision(before['revision']))
            if entry['request_hash'] != expected_hash:
                raise ValueError()
            if index < len(verified):
                after = entry['after']
                if (after['file_id'] != record['file_id'] or not after['revision']
                        or after['structure_hash'] != before['structure_hash']):
                    raise ValueError()
                before = after
            elif entry['receipt_revision'] is not None and not isinstance(entry['receipt_revision'], str):
                raise ValueError()
    except (KeyError, TypeError, ValueError):
        blocked('Batch checkpoint schema, specification or verified chain is invalid.')


def recover_sequence(path: Path, remote, *, review_unchanged: bool = False) -> dict:
    """Read-only remote reconciliation of a saved, acknowledged batch receipt."""
    record = read_json(path)
    validate_record(record)
    pending = record.get('inflight')
    if pending is None:
        return record
    receipt = pending.get('receipt_revision')
    if not receipt:
        if review_unchanged:
            _, current = observe(remote, record['file_id'])
            if current == pending['before']:
                # Preview only: do not turn an observation into a fabricated
                # write receipt or discard the uncertain attempt.
                return record
        blocked('The pending batch has no durable post-write revision receipt.')
    _, current = observe(remote, record['file_id'])
    if current['revision'] != receipt or current['structure_hash'] != pending['before']['structure_hash']:
        blocked('Remote state no longer matches the acknowledged batch revision and structure.')
    record['verified'].append({'segment': pending['segment'], 'before': pending['before'],
                               'after': current, 'request_hash': pending['request_hash']})
    record['inflight'] = None
    write_json(path, record)
    return record


def close_unchanged_attempt(path: Path, remote, checkpoint_hash: str,
                           authorized_digest: str) -> None:
    """Archive an explicitly reviewed, still-unchanged attempt before resuming.

    No remote write or baseline advancement. The next request retains the same
    required revision, so a delayed earlier request cannot be silently combined
    with a new content-changing request against a different revision.
    """
    record = read_json(path)
    validate_record(record)
    pending = record['inflight']
    if (fingerprint(record) != checkpoint_hash or pending is None
            or pending['receipt_revision'] is not None or not authorized_digest):
        blocked('The reviewed unchanged attempt no longer matches the checkpoint.')
    _, current = observe(remote, record['file_id'])
    if current != pending['before']:
        blocked('Remote state changed before closure of the unchanged attempt.')
    # Persist evidence first. A crash here leaves the original inflight marker;
    # a crash after clearing it leaves an ordinary reviewed-resume checkpoint.
    write_json(path.parent / ('unchanged-' + checkpoint_hash + '.json'),
               {'sequence': record, 'observation': current,
                'authorized_digest': authorized_digest})
    record['inflight'] = None
    write_json(path, record)


def run_sequence(store, operation_id: str, file_id: str, segments: tuple[BatchSegment, ...],
                 initial_snapshot: dict, remote, before_write: Callable[[], None],
                 *, reviewed_resume: bool = False, cancellation=None) -> bool:
    """Send ordered guarded batches; False means cancelled at a safe checkpoint.

    A successful receipt only identifies the revision to read. Each receipt must
    match a fresh full observation before continuing; final desired-content
    verification is still the parent operation's responsibility.
    """
    directory = private_directory(store.journals / (str(uuid.UUID(operation_id)) + '.batches'))
    path = directory / 'sequence.json'
    specification = {'file_id': file_id, 'segments': [asdict(s) for s in segments],
                     'initial': initial_snapshot}
    identity = fingerprint(specification)
    if path.exists():
        record = read_json(path)
        validate_record(record)
        if record.get('specification_hash') != identity:
            blocked('Staged batch specification changed.')
        if not reviewed_resume:
            blocked('An existing sequence requires explicit reviewed resumption.')
        record = recover_sequence(path, remote)
    else:
        if reviewed_resume:
            blocked('There is no existing batch sequence to resume.')
        record = dict(specification, specification_hash=identity, verified=[], inflight=None)
        write_json(path, record)
    for index in range(len(record['verified']), len(segments)):
        if cancellation is not None and cancellation.is_set():
            return False
        before_write()
        observation, current = observe(remote, file_id)
        expected = record['verified'][-1]['after'] if record['verified'] else initial_snapshot
        if current != expected:
            blocked('Remote snapshot changed between verified batches.')
        batch = segments[index].bind_revision(current['revision'])
        record['inflight'] = {'segment': index, 'before': current,
                              'request_hash': fingerprint(batch), 'receipt_revision': None}
        write_json(path, record)
        # No catch-and-retry: exceptions leave an inflight marker, even if the
        # API applied the request but its response was lost.
        response = remote.update_document(observation, batch)
        receipt = response.get('writeControl', {}).get('requiredRevisionId') if isinstance(response, dict) else None
        if not isinstance(receipt, str) or not receipt or response.get('documentId') != file_id:
            blocked('Write response lacks an attributable updated required revision.')
        record['inflight']['receipt_revision'] = receipt
        write_json(path, record)
        record = recover_sequence(path, remote)
    return True
