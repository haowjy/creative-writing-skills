"""Reviewed file/folder layout restoration without touching content."""
from dataclasses import asdict, replace
import json
from .executor import Prepared, Observation
from .folders import binding_map
from .google import DOC, FOLDER, fingerprint
from .index import Diagnostic
from .sync_plan import baseline_from_binding, observe_file


def verify_identity(metadata, binding, source_id):
    mime = metadata.get('mimeType', '')
    expected = FOLDER if binding.get('kind') == 'folder' else DOC if binding.get('storage') == 'google-doc' else None
    if (metadata.get('id') != binding['remote_id']
            or metadata.get('appProperties', {}).get('source') != source_id
            or (expected is not None and mime != expected)
            or (expected is None and mime.startswith('application/vnd.google-apps.'))):
        raise Diagnostic('layout_identity_mismatch', 'Remote identity or representation differs from the bound object.',
                         'Inspect source markers and restore the correct binding; do not adopt or repair by title.',
                         source=binding.get('path', binding.get('root', '') + '/' + binding.get('relative_path', '')),
                         destination=binding['remote_id'], operation='restore-layout')


class LayoutEffects:
    def __init__(self, effects):
        self.effects = effects
        self.store, self.remote = effects.store, effects.remote

    def refresh_plan(self, plan):
        return self.effects.refresh_plan(plan)

    def prepare(self, operation):
        binding = binding_map(self.store)[operation.source_id]
        if binding.get('kind') == 'folder':
            folder=self.effects.folder.folders[operation.source_id]
            parents=binding.get('parents',[])
            from .folders import planned_parent
            parent=planned_parent(self.effects.layout, folder, binding_map(self.store)) or (parents[0] if not folder.parent_id and len(parents)==1 else None)
            if not parent:
                raise Diagnostic('parent_pending','Original parent is not verifiable.','Restore parent bindings before restoring this folder.')
            before,etag=self.remote.metadata_guard(binding['remote_id'])
            verify_identity(before, binding, operation.source_id)
            actual=fingerprint(dict(name=before.get('name'),parents=before.get('parents',[]),mime=before.get('mimeType')))
            if actual != operation.remote.structure_hash or str(before.get('version', '')) != operation.remote.revision:
                raise Diagnostic('remote_race','Folder layout changed after preview.','Preview again.')
            desired=dict(name=folder.name,parent=parent)
            return Prepared(operation.source_id,fingerprint(before),fingerprint(desired),json.dumps(dict(desired=desired,before=before,etag=etag)).encode(),dict(binding,effect_kind='layout'))
        before,etag = self.remote.metadata_guard(binding['remote_id'])
        verify_identity(before, binding, operation.source_id)
        observed = observe_file(self.remote,binding['remote_id'],binding['storage'])
        if observed != operation.remote or self.remote.metadata(binding['remote_id']) != before:
            raise Diagnostic('remote_race', 'Remote changed during layout preparation.', 'Preview layout restoration again.')
        desired = dict(name=binding['name'],parent=binding['parent'])
        payload = dict(desired=desired,before=before,etag=etag)
        return Prepared(operation.source_id,fingerprint(before),fingerprint(desired),json.dumps(payload).encode(),
                        dict(binding,effect_kind='layout',expected_remote=asdict(observed)))

    def guard(self, operation):
        if operation.source_id in self.effects.folder_ids:
            if self.effects.current_digest() != self.effects.folder.expected_index_digest:
                raise Diagnostic('stale_index','Index changed during layout repair.','Preview again.')
            return
        self.effects.route(operation.source_id).guard(operation)

    def mutate(self, operation, prepared, intent):
        payload=json.loads(prepared.payload)
        self.remote.update_layout(prepared.binding['remote_id'],name=payload['desired']['name'],
            parent=payload['desired']['parent'],before=payload['before'],etag=payload['etag'])

    def observe(self, intent, prepared):
        binding=prepared.binding
        metadata=self.remote.metadata(binding['remote_id'])
        verify_identity(metadata, binding, intent.source_id)
        if binding.get('kind')=='folder':
            parents=metadata.get('parents',[])
            actual=dict(name=metadata.get('name'),parent=parents[0] if len(parents)==1 else None)
            return (Observation(fingerprint(actual),dict(parents=parents,effect_kind='folder')),)
        observed=observe_file(self.remote,binding['remote_id'],binding['storage'])
        if self.remote.metadata(binding['remote_id']) != metadata:
            raise Diagnostic('remote_race', 'Metadata changed during layout verification.',
                             'Retain the pending repair and run state recover after changes settle.')
        if observed.content_hash != binding['expected_remote']['content_hash']:
            return ()
        parents=metadata.get('parents',[])
        actual=dict(name=metadata.get('name'),parent=parents[0] if len(parents)==1 else None)
        base=baseline_from_binding(binding)
        # Preserve old content baseline: any independent remote content edits must
        # remain detectable after correcting the name/parent.
        updated=replace(base,remote=replace(base.remote,structure_hash=observed.structure_hash,revision=observed.revision))
        return (Observation(fingerprint(actual),dict(baseline=asdict(updated),effect_kind='file',layout_pending=False)),)
