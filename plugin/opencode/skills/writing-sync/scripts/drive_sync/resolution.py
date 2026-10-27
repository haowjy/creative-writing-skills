"""Explicit reviewed conflict plans; no baseline rewriting to hide conflicts."""
from dataclasses import replace
from .index import Diagnostic
from .planner import SyncPlan


def resolution_plan(plan: SyncPlan, source_id: str, choice: str) -> SyncPlan:
    operations = [o for o in plan.operations if o.source_id == source_id]
    if len(operations) != 1:
        raise Diagnostic('unknown_conflict', 'Source is not uniquely present in this plan.', 'Inspect current selections and bindings.')
    operation = operations[0]
    if choice == 'replace-storage' and operation.reason == 'storage_changed' and operation.local and operation.remote and operation.baseline:
        return SyncPlan(plan.index_id,plan.index_digest,(replace(operation,direction='create',reason='reviewed_replace_storage'),))
    if choice == 'restore-layout' and operation.reason == 'folder_changed' and operation.local and operation.remote:
        return SyncPlan(plan.index_id,plan.index_digest,(replace(operation,direction='push',reason='reviewed_restore_layout'),))
    if choice == 'restore-layout' and operation.reason == 'remote_structure_changed' and operation.local and operation.remote and operation.baseline:
        return SyncPlan(plan.index_id,plan.index_digest,(replace(operation,direction='push',reason='reviewed_restore_layout'),))
    if operation.reason != 'both_changed' or not operation.local or not operation.remote or not operation.baseline:
        raise Diagnostic('unsupported_resolution', 'This operation is not a two-sided content conflict.', 'Use the specific repair action from the current plan; do not bypass missing-state or structure guards.')
    if choice == 'keep-local':
        if not operation.remote.annotations_readable or operation.remote.comments or operation.remote.suggestions:
            raise Diagnostic('annotations_protected', 'Annotations block local-over-remote replacement.', 'Review comments and suggestions first.')
        direction = 'push'
    elif choice == 'accept-remote':
        direction = 'pull'
    else:
        raise Diagnostic('invalid_resolution', 'Unknown conflict choice.', 'Choose keep-local or accept-remote after reviewing both versions.')
    return SyncPlan(plan.index_id, plan.index_digest,
                    (replace(operation, direction=direction, reason='reviewed_' + choice,
                             action='Apply only with authorization for this exact resolution digest.'),))


class ResolutionEffects:
    def __init__(self, effects, source_id, choice):
        self.effects, self.source_id, self.choice = effects, source_id, choice
    def refresh_plan(self, plan):
        return resolution_plan(self.effects.refresh_plan(plan), self.source_id, self.choice)
    def prepare(self, operation):
        return self.effects.prepare(operation)
    def guard(self, operation):
        return self.effects.guard(operation)
    def mutate(self, operation, prepared, intent):
        return self.effects.mutate(operation,prepared,intent)
    def observe(self, intent, prepared):
        return self.effects.observe(intent,prepared)
