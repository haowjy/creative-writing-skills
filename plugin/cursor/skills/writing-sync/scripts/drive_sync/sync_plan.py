"""Build file plans from selected sources, persisted bindings and fresh Google reads."""
from dataclasses import dataclass, replace
from pathlib import Path

from .conversion import render, Style
from .document_semantics import semantic, document_settings
from .presentation import capture, content_styles
from .document_model import read_document
from .folders import binding_map
from .google import fingerprint
from .index import Source, Diagnostic
from .layout import Layout
from .planner import Baseline, LocalSnapshot, RemoteSnapshot, SyncPlan, classify, Operation
from .sources import snapshot
from .state import StateStore
from .storage import digest


def baseline_from_binding(binding: dict) -> Baseline:
    try:
        raw = binding['baseline']
        return Baseline(LocalSnapshot(**raw['local']), RemoteSnapshot(**raw['remote']))
    except (KeyError, TypeError):
        raise Diagnostic('missing_baseline', 'Binding lacks a complete verified baseline.', 'Restore state or review rebaselining; do not infer it from current source bytes.') from None


def observe_file(remote, file_id: str, storage: str):
    if storage == 'google-doc':
        return read_document(remote.observe_document(file_id)).snapshot
    data, metadata = remote.read_original(file_id)
    return RemoteSnapshot(file_id, digest(data),
                          fingerprint(dict(name=metadata.get('name'), parents=metadata.get('parents', []), mime=metadata.get('mimeType'))),
                          str(metadata['version']), True, False, False, 0)



def render_source(source, data, layout, sources, bindings):
    from .links import rewrite_links
    paths = {(s.root, s.relative_path): s.path.resolve() for s in sources}
    destinations = {}
    for destination in layout.files:
        binding = bindings.get(destination.source_id, {})
        if binding.get('storage') == 'google-doc' and binding.get('remote_id') and (binding.get('baseline') or binding.get('identity_verified')):
            destinations[paths[destination.root, destination.relative_path]] = (destination.source_id, binding['remote_id'])
    return rewrite_links(render(data, source.format), source.path, destinations)


def file_plan(index_digest: str, layout: Layout, sources: tuple[Source, ...],
              store: StateStore, remote) -> SyncPlan:
    bindings = binding_map(store)
    inventory = remote.inventory()
    by_id = {m['id']: m for m in inventory}
    by_source = {}
    for item in inventory:
        by_source.setdefault(item.get('appProperties', {}).get('source'), []).append(item)
    pending = {i.source_id for i in store.pending()}
    source_map = {(s.root, s.relative_path): s for s in sources}
    operations = []
    missing_bound = [sid for sid,b in bindings.items()
                     if b.get('kind') == 'file' and b.get('path') and not Path(b['path']).exists()
                     and not b.get('missing_acknowledged')]
    selected = set()
    for destination in layout.files:
        selected.add(destination.source_id)
        source = source_map[destination.root, destination.relative_path]
        bound = bindings.get(destination.source_id)
        local = None
        observed = None
        base = None
        presentation_only = False
        try:
            captured = snapshot(source.path)
            rendering = render_source(source, captured.data, layout, sources, bindings)[0] if source.storage == 'google-doc' else None
            if rendering is not None and not rendering.supported:
                raise Diagnostic('conversion_blocked', 'Source has unresolved conversion findings.', 'Run conversion check and resolve findings before syncing.', str(source.path))
            local = LocalSnapshot(destination.source_id, destination.root + '/' + destination.relative_path,
                                  captured.digest, rendering.fingerprint if rendering else captured.digest, source.storage)
            if bound and bound.get('incomplete'):
                observed = observe_file(remote,bound['remote_id'],'google-doc')
                stored = RemoteSnapshot(**bound['skeleton_remote'])
                if observed != stored:
                    raise Diagnostic('initialized_doc_changed','The incomplete Doc changed after identity verification.','Review the incomplete copy before writing source content.')
                operations.append(Operation(destination.source_id,'push','populate_initialized_doc',
                    'Write content into the verified empty identity.',local,observed,None))
                continue
            if bound:
                base = baseline_from_binding(bound)
                file_id = base.remote.file_id
                if file_id in by_id:
                    if by_id[file_id].get('appProperties', {}).get('source') != destination.source_id:
                        raise Diagnostic('identity_mismatch', 'Remote source marker differs from the binding.', 'Inspect state and ownership before continuing.')
                    if base.local.storage == 'google-doc':
                        observation = remote.observe_document(file_id)
                        model = read_document(observation)
                        observed = model.snapshot
                        overlay = capture(observation.document)
                        if (any(row['style'] for row in overlay) or bound.get('presentation_v1')):
                            # Preserve the real snapshot in the plan/guards. Only
                            # content-change classification ignores verified
                            # spacing; baseline state itself is never rewritten.
                            presentation_only = (
                                'text' in bound and 'styles' in bound
                                and bound.get('remote_settings') == document_settings(observation.document)
                                and semantic(bound['text'], tuple(Style(**s) for s in bound['styles']))
                                == semantic(model.text, content_styles(model.styles)))
                    else:
                        observed = observe_file(remote, file_id, base.local.storage)
            elif missing_bound:
                raise Diagnostic('possible_source_relocation','A previously bound source is missing while this new path is selected.','Use source rebind if it moved, or acknowledge the missing archived source before creating an unrelated copy.')
            elif by_source.get(destination.source_id):
                raise Diagnostic('missing_baseline', 'Owned remote source exists without its binding.', 'Recover private state; do not create another reading copy.')
            retained_ids = {b.get('remote_id') for b in (bound or {}).get('retained_bindings', [])}
            active_matches = [m for m in by_source.get(destination.source_id, []) if m['id'] not in retained_ids]
            if len(active_matches) > 1:
                raise Diagnostic('duplicate_remote', 'Several owned objects claim one source identity.', 'Review ownership markers and pending journals; do not choose by title.')
            if bound and bound.get('layout_pending') and observed and base:
                operations.append(Operation(destination.source_id,'conflict','remote_structure_changed',
                    'Review restore-layout to apply the rebound source name/parent.',local,observed,base))
                continue
            comparison = replace(observed, content_hash=base.remote.content_hash) if presentation_only else observed
            operation = classify(destination.source_id, local, comparison, base,
                                 ownership_checked=True, pending=destination.source_id in pending)
            operations.append(replace(operation, remote=observed))
        except Diagnostic as exc:
            operations.append(Operation(destination.source_id, 'conflict', exc.code, exc.action, local, observed, base))
        except FileNotFoundError:
            operations.append(Operation(destination.source_id, 'conflict', 'missing_source', 'Restore or explicitly rebind the source.', None, observed, base))
    # Deselection retains bindings and objects; a later reselect uses its old base.
    return SyncPlan(store.index_id, index_digest, tuple(operations))
