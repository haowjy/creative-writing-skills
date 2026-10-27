"""Original-file effects: guarded create/push/pull and read-only reconciliation."""
from dataclasses import asdict, replace
import json

from .executor import Prepared, Observation
from .folders import binding_map
from .google import fingerprint
from .index import Diagnostic
from .planner import Baseline
from .sources import snapshot, commit_candidate
from .storage import digest
from .sync_plan import file_plan, observe_file


class OriginalEffects:
    def __init__(self, layout, sources, store, remote, current_index_digest):
        self.layout, self.sources, self.store, self.remote = layout, sources, store, remote
        self.current_index_digest = current_index_digest
        source_map = {(s.root,s.relative_path):s for s in sources}
        self.destinations = {d.source_id:d for d in layout.files}
        self.by_id = {d.source_id:source_map[d.root,d.relative_path] for d in layout.files}
        self.expected_digest = None

    def refresh_plan(self, plan):
        self.expected_digest = plan.index_digest
        return file_plan(self.current_index_digest(), self.layout, self.sources, self.store, self.remote)

    def prepare(self, operation):
        source = self.by_id[operation.source_id]
        if source.storage != 'original':
            raise Diagnostic('wrong_effects', 'Original effects cannot handle converted sources.', 'Route through the native document effects service.')
        captured = snapshot(source.path)
        if captured.digest != operation.local.content_hash:
            raise Diagnostic('source_race', 'Source changed since preview.', 'Preview again before applying.')
        destination = self.destinations[operation.source_id]
        parent = binding_map(self.store).get(destination.parent_id, {}).get('remote_id')
        if not parent:
            raise Diagnostic('parent_pending', 'Destination folder has not been verified.', 'Complete folder operations first.')
        data = captured.data
        etag = None
        if operation.direction == 'pull':
            data, metadata = self.remote.read_original(operation.remote.file_id)
            if digest(data) != operation.remote.content_hash:
                raise Diagnostic('remote_race', 'Original file changed since preview.', 'Preview again before pulling.')
        elif operation.direction == 'push':
            etag = self.remote.original_etag(operation.remote.file_id)
            if observe_file(self.remote, operation.remote.file_id, 'original') != operation.remote:
                raise Diagnostic('remote_race', 'Original file changed during ETag capture.', 'Preview again before pushing.')
        local = replace(operation.local, content_hash=digest(data), rendering_hash=digest(data))
        binding = dict(kind='file', storage='original', local=asdict(local),
                       source_blob=self.store.save_blob(data), prior_blob=self.store.save_blob(captured.data),
                       path=str(source.path), device=captured.device, inode=captured.inode,
                       name=destination.name, parent=parent, etag=etag,
                       remote_id=operation.remote.file_id if operation.remote else None,
                       prior_remote=asdict(operation.remote) if operation.remote else None)
        previous = binding_map(self.store).get(operation.source_id, {})
        if previous.get('retained_bindings'):
            binding['retained_bindings'] = previous['retained_bindings']
        if operation.reason == 'reviewed_replace_storage':
            old = binding_map(self.store)[operation.source_id]
            binding['retained_bindings'] = old.get('retained_bindings', []) + [{k:v for k,v in old.items() if k != 'retained_bindings'}]
        return Prepared(operation.source_id, captured.digest if operation.direction == 'pull' else
                        operation.remote.content_hash if operation.remote else None,
                        digest(data), data, binding)

    def guard(self, operation):
        if self.current_index_digest() != self.expected_digest:
            raise Diagnostic('stale_index', 'Index changed during apply.', 'Preview again.')
        if snapshot(self.by_id[operation.source_id].path).digest != operation.local.content_hash:
            raise Diagnostic('source_race', 'Source changed during apply.', 'Preview again.')
        if operation.remote and observe_file(self.remote, operation.remote.file_id, operation.baseline.local.storage if operation.reason == 'reviewed_replace_storage' else 'original') != operation.remote:
            raise Diagnostic('remote_race', 'Remote changed during apply.', 'Preview again.')

    def mutate(self, operation, prepared, intent):
        binding = prepared.binding
        if operation.direction == 'create':
            self.remote.create(binding['name'], 'application/octet-stream', operation.source_id, intent.id,
                               parent=binding['parent'], data=prepared.payload, import_mime='application/octet-stream')
        elif operation.direction == 'push':
            self.remote.update_original(binding['remote_id'], prepared.payload, binding['etag'])
        else:
            captured = snapshot(self.by_id[operation.source_id].path)
            if captured.digest != prepared.before_hash or captured.inode != binding['inode'] or captured.device != binding['device']:
                raise Diagnostic('source_race', 'Source changed before replacement.', 'Review the retained candidate.')
            commit_candidate(captured, prepared.payload, self.store.path / 'backups')

    def observation_metadata(self, intent, prepared):
        """Resolve identity before checking layout; never filter duplicates away."""
        binding = prepared.binding
        if intent.kind == 'create':
            matches = self.remote.inventory(operation_id=intent.id)
        else:
            matches = (self.remote.metadata(binding['remote_id']),)
        if len(matches) != 1:
            raise Diagnostic('creation_not_found' if not matches else 'ambiguous_identity',
                             'No unique remote object matches the recorded operation.',
                             'Inspect operation markers and retain the journal; never repeat the create blindly.',
                             binding.get('path', ''), operation='read-back')
        metadata = matches[0]
        def invalid(code, reason):
            return Diagnostic(code, reason,
                              'Review the already-created object against the saved plan; retain both versions and do not repeat the create.',
                              binding.get('path', ''), destination=metadata.get('id', ''), operation='read-back')
        if metadata.get('appProperties', {}).get('source') != intent.source_id:
            raise invalid('remote_identity_mismatch', 'Operation marker belongs to a different source identity.')
        if intent.kind != 'create' and metadata.get('id') != binding['remote_id']:
            raise invalid('remote_identity_mismatch', 'Read-back returned a different remote identity.')
        if metadata.get('name') != binding['name'] or metadata.get('parents') != [binding['parent']]:
            raise invalid('remote_layout_mismatch', 'Remote name or parent differs from the staged destination.')
        from .google import DOC
        native = metadata.get('mimeType', '').startswith('application/vnd.google-apps.')
        if ((binding['storage'] == 'google-doc' and metadata.get('mimeType') != DOC)
                or (binding['storage'] == 'original' and native)):
            raise invalid('remote_storage_mismatch', 'Read-back storage type differs from the staged representation.')
        return (metadata,)

    def observe(self, intent, prepared):
        binding = prepared.binding
        matches = self.observation_metadata(intent, prepared)
        results = []
        for metadata in matches:
            observed = observe_file(self.remote, metadata['id'], 'original')
            if intent.kind == 'pull':
                if asdict(observed) != binding['prior_remote']:
                    continue
                actual = snapshot(self.by_id[intent.source_id].path).digest
            else:
                actual = observed.content_hash
            from .planner import LocalSnapshot
            baseline = Baseline(LocalSnapshot(**binding['local']), observed)
            results.append(Observation(actual, dict(remote_id=metadata['id'], baseline=asdict(baseline))))
        return tuple(results)
