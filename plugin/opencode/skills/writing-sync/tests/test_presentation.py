from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
from drive_sync.index import Diagnostic
from drive_sync.presentation import FIELDS, capture, map_spacing, spacing
from drive_sync.storage import Draft, commit
from fake_google import FakeGoogle
from test_index import fixture
from test_scoping import authorize


class SpacingGoogle(FakeGoogle):
    def __init__(self):
        super().__init__()
        self.paragraph_styles = {}
        self.corrupt_spacing = False

    def observe_document(self, file_id):
        observation = super().observe_document(file_id)
        rows = [b for b in observation.document['tabs'][0]['documentTab']['body']['content'] if 'paragraph' in b]
        saved = self.paragraph_styles.get(file_id, [])
        for i, row in enumerate(rows):
            row['paragraph']['paragraphStyle'] = deepcopy(saved[i] if i < len(saved) else {})
        return observation

    def set_spacing(self, file_id, styles):
        count = len(capture(super().observe_document(file_id).document))
        self.paragraph_styles[file_id] = deepcopy(styles * count if len(styles) == 1 else styles)
        assert len(self.paragraph_styles[file_id]) == count
        self.files[file_id]['version'] = str(int(self.files[file_id]['version']) + 1)

    def update_document(self, observation, batch):
        file_id = observation.metadata['id']
        inherited = (self.paragraph_styles.get(file_id) or [{}])[0]
        result = super().update_document(observation, batch)
        rows = capture(super().observe_document(file_id).document)
        if any('deleteContentRange' in r for r in batch['requests']):
            self.paragraph_styles[file_id] = [deepcopy(inherited) for _ in rows]
        current = self.paragraph_styles.setdefault(file_id, [{} for _ in rows])
        for request in batch['requests']:
            value = request.get('updateParagraphStyle')
            if not value:
                continue
            for i, row in enumerate(rows):
                if row['start'] < value['range']['endIndex'] and row['end'] > value['range']['startIndex']:
                    for field in set(value['fields'].split(',')) & set(FIELDS):
                        current[i].pop(field, None)
                        if field in value['paragraphStyle']:
                            current[i][field] = deepcopy(value['paragraphStyle'][field])
        if self.corrupt_spacing:
            current[0]['spaceBelow'] = {'magnitude': 999, 'unit': 'PT'}
        return result


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        (self.run / 'notes').mkdir()
        self.source = self.run / 'notes/a.md'
        self.original = b'First paragraph.\n\n<!-- craft note -->\n\nSecond paragraph.\n'
        self.source.write_bytes(self.original)
        self.index = self.run / 'index.yaml'
        commit(self.index, Draft(fixture()), None)
        self.remote = SpacingGoogle()
        plan = initialize_documents(self.index, self.remote, home=self.run/'state')
        initialize_documents(self.index, self.remote, authorize(plan), home=self.run/'state')
        self.apply()
        self.doc = next(k for k,v in self.remote.files.items() if v['name'] == 'a.md')
        self.style = {'spaceBelow': {'magnitude': 10, 'unit': 'PT'}, 'spacingMode': 'COLLAPSE_LISTS'}

    def plan(self):
        return combined_plan(preview_sync(self.index, self.remote, home=self.run/'state'))

    def apply(self):
        plan = self.plan()
        return apply_reviewed(self.index, self.remote, authorize(plan), home=self.run/'state')

    def test_spacing_only_is_noop_and_does_not_touch_source(self):
        self.remote.set_spacing(self.doc, [self.style])
        before = self.source.stat()
        writes = list(self.remote.calls)
        self.assertTrue(all(o.direction == 'noop' for o in self.plan().operations))
        self.apply()
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(self.source.stat().st_ino, before.st_ino)
        self.assertEqual(self.source.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(self.remote.calls, writes)

    def test_both_directions_preserve_spacing_and_comments(self):
        self.remote.set_spacing(self.doc, [self.style])
        # Presentation-only Google changes must not create a false both_changed.
        self.source.write_bytes(self.original.replace(b'Second', b'Local'))
        self.assertEqual(self.plan().operations[-1].direction, 'push')
        self.assertTrue(all(f.status in ('verified','noop') for f in self.apply().files))
        self.assertTrue(all(s == spacing(self.style) for s in self.remote.paragraph_styles[self.doc]))
        self.remote.bodies[self.doc] = self.remote.bodies[self.doc].replace('First', 'Remote')
        self.remote.files[self.doc]['version'] = str(int(self.remote.files[self.doc]['version'])+1)
        self.assertEqual(self.plan().operations[-1].direction, 'pull')
        self.assertTrue(all(f.status in ('verified','noop') for f in self.apply().files))
        self.assertEqual(self.source.read_bytes(), self.original.replace(b'Second',b'Local').replace(b'First',b'Remote'))
        self.assertTrue(all(o.direction == 'noop' for o in self.plan().operations))

    def test_mixed_spacing_is_mapped_and_missing_readback_stays_pending(self):
        self.remote.set_spacing(self.doc, [{}, self.style, {}])
        self.source.write_bytes(self.original.replace(b'Second', b'Edited'))
        result = self.apply()
        self.assertTrue(all(f.status in ('verified','noop') for f in result.files))
        self.assertEqual(self.remote.paragraph_styles[self.doc], [{}, spacing(self.style), {}])
        self.source.write_bytes(self.source.read_bytes().replace(b'First', b'Changed'))
        self.remote.corrupt_spacing = True
        result = self.apply()
        self.assertEqual(result.files[-1].status, 'pending')
        self.assertEqual(self.plan().operations[-1].reason, 'unfinished_operation')

    def test_other_formatting_and_two_content_edits_still_conflict(self):
        self.remote.set_spacing(self.doc, [self.style | {'alignment': 'CENTER'}])
        self.assertEqual(self.plan().operations[-1].direction, 'pull')
        self.assertEqual(self.apply().files[-1].status, 'conflict')
        self.assertEqual(self.source.read_bytes(), self.original)
        self.remote.set_spacing(self.doc, [self.style])
        self.remote.bodies[self.doc] = self.remote.bodies[self.doc].replace('First', 'Remote')
        self.source.write_bytes(self.original.replace(b'Second', b'Local'))
        self.assertEqual(self.plan().operations[-1].reason, 'both_changed')

    def test_reviewed_batch_repair_restores_staged_presentation(self):
        from drive_sync.batch_repair import repair_batches
        self.remote.set_spacing(self.doc, [self.style])
        self.source.write_bytes(self.original.replace(b'Second', b'Local'))
        self.remote.corrupt_spacing = True
        # Force the normal staged-sequence path with a small fixture. The fake
        # corrupts spacing after the write; content success must not verify it.
        with patch('drive_sync.google.validate_batch_limits', side_effect=Diagnostic(
                'batch_limit', 'Synthetic segmentation boundary.', 'Use staged batches.')):
            result = self.apply()
        self.assertEqual(result.files[-1].status, 'pending')
        operation = result.files[-1].operation_id
        self.remote.corrupt_spacing = False
        plan = repair_batches(self.index, self.remote, operation, home=self.run/'state')
        repaired = repair_batches(self.index, self.remote, operation, plan.digest, home=self.run/'state')
        self.assertTrue(all(f.status == 'verified' for f in repaired.files), repaired)
        self.assertTrue(all(s == spacing(self.style) for s in self.remote.paragraph_styles[self.doc]))
        self.assertTrue(all(o.direction == 'noop' for o in self.plan().operations))

    def test_validation_and_ambiguous_mapping_fail_closed(self):
        for invalid in ({'spaceBelow': {'magnitude': -1, 'unit': 'PT'}},
                        {'lineSpacing': True}, {'spacingMode': 'unknown'},
                        {'spaceAbove': {'magnitude': 10, 'unit': 'PX'}}):
            with self.subTest(invalid=invalid), self.assertRaises(Diagnostic):
                spacing(invalid)
        self.remote.set_spacing(self.doc, [{}, self.style, {}])
        document = self.remote.observe_document(self.doc).document
        with self.assertRaises(Diagnostic):
            map_spacing(document, 'Replacement for both paragraphs.\n')
        self.remote.set_spacing(self.doc, [self.style])
        document = self.remote.observe_document(self.doc).document
        overlay = map_spacing(document, '😀 First\nNew paragraph\n')
        self.assertEqual(overlay[0]['end'], 10)
        self.assertTrue(all(row['style'] == spacing(self.style) for row in overlay))
