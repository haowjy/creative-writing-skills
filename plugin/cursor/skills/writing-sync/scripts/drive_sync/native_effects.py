"""Converted-file effects with source-preserving pull candidates and read-back."""
from dataclasses import asdict, replace

from .conversion import render, docs_requests, Rendering, Style
from .document_model import read_document
from .executor import Prepared, Observation
from .folders import binding_map
from .google import DOC
from .import_payload import import_html
from .index import Diagnostic
from .original_effects import OriginalEffects
from .planner import Baseline, LocalSnapshot
from .return_conversion import return_candidate
from .sources import snapshot, commit_candidate
from .storage import digest
from .sync_plan import observe_file, render_source
from .document_semantics import semantic, document_settings
from .presentation import capture, content_styles, map_spacing, restore_requests


class NativeEffects(OriginalEffects):
    def prepare(self, operation):
        source = self.by_id[operation.source_id]
        if operation.direction == 'create':
            capabilities = self.remote.capabilities()
            if DOC not in capabilities.get('importFormats', {}).get('text/html', []):
                raise Diagnostic('unsupported_import', 'This Google account does not advertise HTML-to-Docs import.', 'Use an explicitly selected original-file mode or resolve account capabilities; no silent fallback.')
        captured = snapshot(source.path)
        if captured.digest != operation.local.content_hash:
            raise Diagnostic('source_race', 'Source changed after preview.', 'Preview again.')
        rendering, provenance = render_source(source, captured.data, self.layout, self.sources, binding_map(self.store))
        if not rendering.supported:
            raise Diagnostic('conversion_blocked', 'Unresolved source conversion findings.', 'Run conversion check.')
        destination = self.destinations[operation.source_id]
        parent = binding_map(self.store).get(destination.parent_id, {}).get('remote_id')
        if not parent:
            raise Diagnostic('parent_pending', 'Destination folder is unverified.', 'Complete folder operations first.')
        data = captured.data
        segments = None
        presentation = None
        presentation_settings = None
        if operation.direction == 'push':
            from .google import validate_batch_limits
            observation = self.remote.observe_document(operation.remote.file_id)
            model = read_document(observation)
            if model.snapshot != operation.remote:
                raise Diagnostic('remote_race', 'Google document changed after preview.', 'Preview again.')
            presentation = map_spacing(observation.document, rendering.text)
            presentation_settings = document_settings(observation.document)
            batch = docs_requests(rendering, tab_id=model.tab_id,
                                  revision=model.snapshot.revision, old_end=model.end_index)
            batch['requests'].extend(restore_requests(presentation, model.tab_id))
            try:
                validate_batch_limits(batch)
            except Diagnostic as exc:
                if exc.code != 'batch_limit':
                    raise
                from .batching import plan_batches
                segments = plan_batches(batch)
        if operation.direction == 'pull':
            observation = self.remote.observe_document(operation.remote.file_id)
            model = read_document(observation)
            if model.snapshot != operation.remote:
                raise Diagnostic('remote_race', 'Google document changed after preview.', 'Preview again.')
            bound = binding_map(self.store)[operation.source_id]
            if bound.get('remote_settings') != document_settings(observation.document):
                raise Diagnostic('return_formatting_conflict','Document-level formatting differs from the verified baseline.','Review style/layout changes before pulling text into source format.')
            baseline_text = self.store.load_blob(bound['remote_text_blob']).decode()
            patch_source = captured.data
            if operation.reason == 'reviewed_accept-remote':
                patch_source = self.store.load_blob(bound['source_blob'])
                # Explicit resolution discards reviewed local prose edits, not
                # unseen changes to comments/frontmatter/package structure.
                restored = return_candidate(captured.data, expected_source_hash=captured.digest,
                    format=source.format, baseline_text=rendering.text, remote_text=baseline_text).data
                if restored != patch_source:
                    raise Diagnostic('protected_source_conflict',
                        'Local source structure changed beyond the reviewed readable text.',
                        'Reconcile source-only changes manually; accept-remote cannot discard them.')
            data = return_candidate(patch_source, expected_source_hash=digest(patch_source), format=source.format,
                                    baseline_text=baseline_text, remote_text=model.text).data
            rendering, provenance = render_source(source, data, self.layout, self.sources, binding_map(self.store))
            captured_presentation = capture(observation.document)
            if any(row['style'] for row in captured_presentation):
                presentation = captured_presentation
                presentation_settings = document_settings(observation.document)
            comparable = content_styles(model.styles) if presentation is not None else model.styles
            if semantic(rendering.text, rendering.styles) != semantic(model.text, comparable):
                raise Diagnostic('return_formatting_conflict', 'The source-preserving candidate does not reproduce remote formatting.', 'Review formatting changes rather than silently discarding them.')
        local = replace(operation.local, content_hash=digest(data), rendering_hash=rendering.fingerprint)
        binding = dict(kind='file', storage='google-doc', format=source.format, local=asdict(local),
                       source_blob=self.store.save_blob(data), prior_blob=self.store.save_blob(captured.data),
                       path=str(source.path), device=captured.device, inode=captured.inode,
                       name=destination.name, parent=parent,
                       remote_id=operation.remote.file_id if operation.remote else None,
                       prior_remote=asdict(operation.remote) if operation.remote else None,
                       text=rendering.text, styles=[asdict(s) for s in rendering.styles],
                       link_provenance=[asdict(p) for p in provenance])
        if presentation is not None:
            binding['presentation_v1'] = presentation
            binding['presentation_settings'] = presentation_settings
        if segments is not None:
            binding['batch_segments'] = [asdict(s) for s in segments]
            binding['batch_index_digest'] = self.expected_digest
        previous = binding_map(self.store).get(operation.source_id, {})
        if previous.get('retained_bindings'):
            binding['retained_bindings'] = previous['retained_bindings']
        if operation.reason == 'reviewed_replace_storage':
            old = binding_map(self.store)[operation.source_id]
            binding['retained_bindings'] = old.get('retained_bindings', []) + [{k:v for k,v in old.items() if k != 'retained_bindings'}]
        desired = digest(data) if operation.direction == 'pull' else semantic(rendering.text, rendering.styles)
        return Prepared(operation.source_id, captured.digest, desired, data, binding)

    def guard(self, operation):
        if self.current_index_digest() != self.expected_digest:
            raise Diagnostic('stale_index', 'Index changed during execution.', 'Preview again.')
        if snapshot(self.by_id[operation.source_id].path).digest != operation.local.content_hash:
            raise Diagnostic('source_race', 'Source changed during execution.', 'Preview again.')
        if operation.remote and observe_file(self.remote, operation.remote.file_id, operation.baseline.local.storage if operation.reason == 'reviewed_replace_storage' else 'google-doc') != operation.remote:
            raise Diagnostic('remote_race', 'Google changed during execution.', 'Preview again.')

    def mutate(self, operation, prepared, intent):
        binding = prepared.binding
        rendering = Rendering(binding['format'], binding['text'], tuple(Style(**s) for s in binding['styles']))
        if operation.direction == 'create':
            self.remote.create(binding['name'], DOC, operation.source_id, intent.id,
                               parent=binding['parent'], data=import_html(rendering), import_mime='text/html')
        elif operation.direction == 'push':
            if binding.get('batch_segments'):
                from .batching import BatchSegment
                from .batch_execution import run_sequence
                def guard_source():
                    current = snapshot(self.by_id[operation.source_id].path)
                    if (self.current_index_digest() != binding['batch_index_digest']
                            or current.digest != prepared.before_hash
                            or current.inode != binding['inode'] or current.device != binding['device']):
                        raise Diagnostic('source_race', 'Source or index changed between batches.', 'Review the partial sequence before resuming.')
                completed = run_sequence(self.store, intent.id, binding['remote_id'],
                    tuple(BatchSegment(**s) for s in binding['batch_segments']),
                    binding['prior_remote'], self.remote, guard_source,
                    cancellation=getattr(self, 'cancellation', None))
                if not completed:
                    raise Diagnostic('batch_cancelled', 'Stopped at a durable batch checkpoint.', 'Review and resume the staged sequence.')
                return
            observation = self.remote.observe_document(binding['remote_id'])
            model = read_document(observation)
            if model.snapshot != operation.remote:
                raise Diagnostic('remote_race', 'Google changed before the guarded write.', 'Preview again.')
            batch = docs_requests(rendering, tab_id=model.tab_id, revision=model.snapshot.revision, old_end=model.end_index)
            batch['requests'].extend(restore_requests(binding.get('presentation_v1'), model.tab_id))
            self.remote.update_document(observation, batch)
        else:
            captured = snapshot(self.by_id[operation.source_id].path)
            if captured.digest != prepared.before_hash or captured.inode != binding['inode'] or captured.device != binding['device']:
                raise Diagnostic('source_race', 'Source changed before pull commit.', 'Review the candidate.')
            if captured.data != prepared.payload:
                commit_candidate(captured, prepared.payload, self.store.path / 'backups')

    def observe(self, intent, prepared):
        binding = prepared.binding
        matches = self.observation_metadata(intent, prepared)
        results = []
        for metadata in matches:
            observation=self.remote.observe_document(metadata['id'])
            model = read_document(observation)
            comparable = model.styles
            if 'presentation_v1' in binding:
                if (capture(observation.document) != binding['presentation_v1']
                        or document_settings(observation.document) != binding['presentation_settings']):
                    continue
                comparable = content_styles(model.styles)
            if intent.kind == 'pull':
                if asdict(model.snapshot) != binding['prior_remote']:
                    continue
                actual = snapshot(self.by_id[intent.source_id].path).digest
            else:
                actual = semantic(model.text, comparable)
            baseline = Baseline(LocalSnapshot(**binding['local']), model.snapshot)
            results.append(Observation(actual, dict(remote_id=metadata['id'], baseline=asdict(baseline),
                                                   remote_text_blob=self.store.save_blob(model.text.encode()),
                                                   remote_settings=document_settings(observation.document))))
        return tuple(results)
