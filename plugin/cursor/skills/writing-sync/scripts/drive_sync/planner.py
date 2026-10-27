"""Pure two-way planning. Remote observations are supplied by an adapter."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Literal

Direction = Literal['create', 'push', 'pull', 'noop', 'conflict']


@dataclass(frozen=True)
class LocalSnapshot:
    source_id: str
    path: str
    content_hash: str
    rendering_hash: str
    storage: str


@dataclass(frozen=True)
class RemoteSnapshot:
    file_id: str
    content_hash: str
    structure_hash: str
    revision: str
    annotations_readable: bool = True
    comments: bool = False
    suggestions: bool = False
    content_tabs: int = 1


@dataclass(frozen=True)
class Baseline:
    local: LocalSnapshot
    remote: RemoteSnapshot


@dataclass(frozen=True)
class Operation:
    source_id: str
    direction: Direction
    reason: str
    action: str
    local: LocalSnapshot | None
    remote: RemoteSnapshot | None
    baseline: Baseline | None


@dataclass(frozen=True)
class SyncPlan:
    index_id: str
    index_digest: str
    operations: tuple[Operation, ...]

    @property
    def digest(self) -> str:
        return sha256(json.dumps(asdict(self), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Authorization:
    plan_digest: str
    index_id: str
    sources: frozenset[str]
    directions: frozenset[str]

    def permits(self, plan: SyncPlan, operation: Operation) -> bool:
        return (self.plan_digest == plan.digest and self.index_id == plan.index_id
                and operation in plan.operations
                and operation.source_id in self.sources
                and operation.direction in self.directions)


def classify(source_id: str, local: LocalSnapshot | None,
             remote: RemoteSnapshot | None, baseline: Baseline | None,
             *, ownership_checked: bool = False, pending: bool = False) -> Operation:
    def result(direction: Direction, reason: str, action: str = ''):
        return Operation(source_id, direction, reason, action, local, remote, baseline)
    if pending:
        return result('conflict', 'unfinished_operation', 'Reconcile the pending journal before planning new writes.')
    if local is None:
        return result('conflict', 'missing_source', 'Restore the source or explicitly review its binding; no remote deletion occurs.')
    if local.source_id != source_id or (baseline and baseline.local.source_id != source_id):
        return result('conflict', 'identity_mismatch', 'Inspect source bindings; do not adopt by filename.')
    if baseline is None:
        if remote is not None:
            return result('conflict', 'missing_baseline', 'Restore state or explicitly review rebaselining this object.')
        if not ownership_checked:
            return result('conflict', 'unchecked_ownership', 'Check ownership markers and unresolved creates first.')
        return result('create', 'new_source')
    if remote is None:
        return result('conflict', 'missing_remote', 'Restore or explicitly review the missing object; do not recreate automatically.')
    if remote.file_id != baseline.remote.file_id:
        return result('conflict', 'identity_mismatch', 'Restore the bound remote identity or review a replacement binding.')
    if local.path != baseline.local.path:
        return result('conflict', 'source_moved', 'Use explicit source rebind to preserve identity.')
    if local.storage != baseline.local.storage:
        return result('conflict', 'storage_changed', 'Review a replacement binding; retain the previous remote object.')
    if remote.structure_hash != baseline.remote.structure_hash:
        return result('conflict', 'remote_structure_changed', 'Review remote moves, names and tabs before restoring layout.')
    if local.storage == 'google-doc' and remote.content_tabs != 1:
        return result('conflict', 'extra_tabs', 'Return the Doc to one content tab; do not discard extra tabs automatically.')
    local_changed = (local.content_hash != baseline.local.content_hash
                     or local.rendering_hash != baseline.local.rendering_hash)
    remote_changed = remote.content_hash != baseline.remote.content_hash
    if local_changed and remote_changed:
        return result('conflict', 'both_changed', 'Review local/base/remote differences and choose an explicit resolution.')
    if local_changed:
        if not remote.annotations_readable or remote.comments or remote.suggestions:
            return result('conflict', 'annotations_protected', 'Review comments and suggestions; unreadable annotation state is not empty.')
        return result('push', 'local_changed')
    if remote_changed:
        if not remote.annotations_readable or remote.suggestions:
            return result('conflict', 'suggestions_protected', 'Review pending suggestions before creating a return candidate.')
        return result('pull', 'remote_changed')
    return result('noop', 'unchanged')
