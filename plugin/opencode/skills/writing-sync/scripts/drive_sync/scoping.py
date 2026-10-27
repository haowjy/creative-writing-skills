"""Pure per-operation scope with explicit mirrored-parent dependencies."""
from .index import Diagnostic
from .layout import Layout
from .planner import SyncPlan


def scoped_plan(plan: SyncPlan, layout: Layout,
                source_ids: frozenset[str] | None) -> SyncPlan:
    if source_ids is None:
        return plan
    available = {operation.source_id for operation in plan.operations}
    if not source_ids or not source_ids <= available:
        raise Diagnostic('invalid_sync_scope', 'Scope is empty or names an item absent from this plan.',
                         'Preview the full plan and select current source UUIDs; do not guess by title.')
    parents = {folder.id: folder.parent_id for folder in layout.folders}
    parents.update({file.source_id: file.parent_id for file in layout.files})
    selected = set(source_ids)
    for source_id in source_ids:
        parent = parents.get(source_id)
        seen = {source_id}
        while parent is not None:
            if parent in seen or parent not in available:
                raise Diagnostic('invalid_scope_dependency', 'A required parent is missing or cyclic.',
                                 'Restore the complete mirrored parent plan before applying.')
            seen.add(parent)
            selected.add(parent)
            parent = parents.get(parent)
    return SyncPlan(plan.index_id, plan.index_digest,
                    tuple(o for o in plan.operations if o.source_id in selected))


class ScopedEffects:
    """Keep executor refreshes inside the exact reviewed application scope."""
    def __init__(self, effects, layout: Layout, source_ids: frozenset[str] | None):
        self.effects, self.layout, self.source_ids = effects, layout, source_ids

    def refresh_plan(self, plan):
        return scoped_plan(self.effects.refresh_plan(plan), self.layout, self.source_ids)

    def prepare(self, operation):
        return self.effects.prepare(operation)

    def guard(self, operation):
        return self.effects.guard(operation)

    def mutate(self, operation, prepared, intent):
        return self.effects.mutate(operation, prepared, intent)

    def observe(self, intent, prepared):
        return self.effects.observe(intent, prepared)
