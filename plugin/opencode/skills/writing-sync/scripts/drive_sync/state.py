"""Private, durable state and uncertain-operation journal.

Callers hold StateStore.lock() across complete plan/apply/recovery operations.
The registry lock is held only while changing ownership claims.
"""
from __future__ import annotations
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator
import json
import math
import os
import uuid

from .index import Diagnostic
from .storage import atomic_write, digest, locked


def private_directory(path: Path) -> Path:
    path = path.expanduser().absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise Diagnostic('unsafe_state_path', 'Private directory contains a symlink.', 'Choose a private nonsymlink state/config path.')
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('Non-finite JSON number')


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        reject_constant(value)
    return result


def check_depth(value):
    pending = [(value, 0)]
    while pending:
        current, depth = pending.pop()
        if depth > 128:
            raise ValueError('State JSON nesting exceeds limit')
        children = current.values() if isinstance(current, dict) else current if isinstance(current, list) else ()
        pending.extend((child, depth + 1) for child in children)


def read_json(path: Path):
    if path.is_symlink():
        raise Diagnostic('unsafe_state_path', 'State file is a symlink.', 'Restore private regular state files.')
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique_object,
                           parse_constant=reject_constant, parse_float=finite_float)
        check_depth(value)
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise Diagnostic('corrupt_state', 'State JSON is invalid or ambiguous.',
                         'Restore a backup; do not silently reset state.', str(path),
                         operation='read-state') from None


def write_json(path: Path, value):
    if path.is_symlink():
        raise Diagnostic('unsafe_state_path', 'State file is a symlink.', 'Restore private regular state files.')
    try:
        check_depth(value)
        data = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    except (ValueError, TypeError, RecursionError):
        raise Diagnostic('invalid_state', 'State value cannot be serialized as strict JSON.',
                         'Retain the existing record and inspect the attempted transition.',
                         str(path), operation='write-state') from None
    atomic_write(path, data)


@dataclass(frozen=True)
class Intent:
    id: str
    source_id: str
    kind: str
    before: str | None
    desired: str
    remote_id: str | None
    status: str = 'pending'


class StateStore:
    def __init__(self, home: Path, index_id: str):
        self.index_id = str(uuid.UUID(index_id))
        self.home = private_directory(home)
        self.path = private_directory(self.home / self.index_id)
        self.blobs = private_directory(self.path / 'blobs')
        self.journals = private_directory(self.path / 'journal')

    @contextmanager
    def lock(self) -> Iterator[None]:
        with locked(self.path / 'state.lock'):
            self.recover_records()
            yield

    def bind_account(self, identity: dict) -> None:
        if (not isinstance(identity, dict) or set(identity) != {'account', 'client'}
                or not all(isinstance(v, str) and v for v in identity.values())):
            raise Diagnostic('unverified_account', 'Remote account/client identity was not verified.', 'Validate the OAuth profile before opening this state namespace.')
        path = self.path / 'account.json'
        if path.exists():
            if read_json(path) != identity:
                raise Diagnostic('wrong_account', 'State belongs to a different Google account or OAuth client.', 'Use the original profile; do not bind existing sources to another account implicitly.')
        else:
            # Legacy state may already contain remote identities; do not silently
            # assign its ownership to whichever profile is supplied now.
            if (self.path / 'bindings.json').exists() or self.pending():
                raise Diagnostic('missing_account_binding', 'Existing state has no account/client binding.', 'Restore the account binding from backup or perform reviewed migration.')
            write_json(path, identity)

    def claim(self, paths: tuple[Path, ...]) -> None:
        """Claims are intentionally retained until explicitly reviewed/released."""
        canonical = [str(p.resolve()) for p in paths]
        with locked(self.home / 'registry.lock'):
            file = self.home / 'registry.json'
            registry = read_json(file) if file.exists() else {}
            for owner, claims in registry.items():
                if owner == self.index_id:
                    continue
                for path in map(Path, canonical):
                    if any(path == Path(c) or path in Path(c).parents or Path(c) in path.parents
                           or (path.exists() and Path(c).exists() and path.samefile(c)) for c in claims):
                        raise Diagnostic('source_owned', 'Another index claims this writable source scope.', 'Use the owning index or explicitly review an ownership transfer.', str(path))
            registry[self.index_id] = sorted(set(registry.get(self.index_id, []) + canonical))
            write_json(file, registry)

    def save_blob(self, data: bytes) -> str:
        key = digest(data)
        path = self.blobs / key
        if path.exists():
            if path.is_symlink() or digest(path.read_bytes()) != key:
                raise Diagnostic('corrupt_baseline', 'Stored baseline failed integrity verification.', 'Restore private state from backup.')
        else:
            atomic_write(path, data)
        return key

    def load_blob(self, key: str) -> bytes:
        if len(key) != 64 or any(c not in '0123456789abcdef' for c in key):
            raise Diagnostic('corrupt_baseline', 'Invalid baseline identifier.', 'Restore state from backup.')
        path = self.blobs / key
        if path.is_symlink() or not path.is_file():
            raise Diagnostic('missing_baseline', 'Baseline is unavailable.', 'Restore state; do not infer a baseline from current content.')
        data = path.read_bytes()
        if digest(data) != key:
            raise Diagnostic('corrupt_baseline', 'Baseline content hash differs.', 'Restore state from backup.')
        return data

    def begin(self, source_id: str, kind: str, before: str | None,
              desired: str, remote_id: str | None = None) -> Intent:
        if any(i.source_id == source_id for i in self.pending()):
            raise Diagnostic('unfinished_operation', 'This source has a pending write.', 'Recover it before starting another write.')
        intent = Intent(str(uuid.uuid4()), source_id, kind, before, desired, remote_id)
        write_json(self.journals / (intent.id + '.json'), asdict(intent))
        return intent

    def pending(self) -> tuple[Intent, ...]:
        try:
            intents = []
            for path in sorted(p for p in self.journals.glob('*.json') if not p.name.endswith(('.prepared.json', '.closure.json'))):
                intent = Intent(**read_json(path))
                if (str(uuid.UUID(intent.id)) != path.stem or intent.status not in ('pending', 'verified', 'closed_unchanged')
                        or intent.kind not in ('create', 'push', 'pull')
                        or not isinstance(intent.source_id, str) or not intent.source_id
                        or not isinstance(intent.desired, str) or not intent.desired):
                    raise ValueError()
                if intent.status == 'pending':
                    intents.append(intent)
            return tuple(intents)
        except Diagnostic:
            raise
        except (TypeError, KeyError, ValueError):
            raise Diagnostic('corrupt_journal', 'Journal schema is invalid.', 'Inspect recovery state; do not retry writes.') from None

    def verify(self, intent: Intent, observed_hash: str, binding: dict) -> None:
        """Caller supplies a fresh remote/local read-back, never just write success."""
        stored = read_json(self.journals / (str(uuid.UUID(intent.id)) + '.json'))
        if stored != asdict(intent) or observed_hash != intent.desired:
            raise Diagnostic('unverified_write', 'Read-back differs from intended outcome or journal changed.', 'Reconcile the operation; baseline was not advanced.')
        file = self.path / 'bindings.json'
        bindings = read_json(file) if file.exists() else {}
        bindings[intent.source_id] = dict(binding, verified_operation=intent.id)
        write_json(file, bindings)
        # A crash here leaves a pending journal with a binding carrying this id.
        write_json(self.journals / (intent.id + '.json'), dict(stored, status='verified'))


    def commit_records(self, records: dict[str, dict]) -> None:
        """Recoverable local multi-record transition under the caller's lock."""
        if not records or set(records) - {'identities.json', 'bindings.json'}:
            raise Diagnostic('invalid_transition', 'Unsupported state record transition.', 'Use a supported binding operation.')
        manifest = self.path / 'record-transition.json'
        if manifest.exists():
            raise Diagnostic('unfinished_transition', 'A state transition is unfinished.', 'Recover state before applying another transition.')
        changes = {}
        for name, value in records.items():
            path = self.path / name
            changes[name] = dict(before=read_json(path) if path.exists() else None, after=value)
        write_json(manifest, changes)
        self.recover_records()

    def recover_records(self) -> None:
        manifest = self.path / 'record-transition.json'
        if not manifest.exists():
            return
        changes = read_json(manifest)
        if not isinstance(changes, dict) or not changes or set(changes) - {'identities.json','bindings.json'}:
            raise Diagnostic('corrupt_transition', 'State transition manifest is invalid.', 'Restore state from backup.')
        for name, change in changes.items():
            if not isinstance(change, dict) or set(change) != {'before','after'} or not isinstance(change['after'], dict):
                raise Diagnostic('corrupt_transition', 'State transition records are invalid.', 'Restore state from backup.')
            path = self.path / name
            current = read_json(path) if path.exists() else None
            if current != change['before'] and current != change['after']:
                raise Diagnostic('state_transition_conflict', 'State changed outside the journaled transition.', 'Review current, previous and intended records; do not overwrite them manually.')
        for name, change in changes.items():
            write_json(self.path / name, change['after'])
        manifest.unlink()
        fd = os.open(self.path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
