from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from drive_sync.application import initialize_documents, recover_sync
from drive_sync.google import DOC, FOLDER
from drive_sync.state import StateStore, read_json
from drive_sync.storage import Draft, commit
from fake_google import FakeGoogle
from test_index import fixture
from test_scoping import authorize


class CreationReconciliationTests(unittest.TestCase):
    def scenario(self, root, target, change):
        (root / 'notes').mkdir()
        (root / 'notes/a.txt').write_text('Synthetic.\n')
        index = root / 'index.yaml'
        raw = fixture()
        commit(index, Draft(raw), None)
        class FaultRemote(FakeGoogle):
            def create(self, name, mime, source_id, operation_id, **kwargs):
                super().create(name, mime, source_id, operation_id, **kwargs)
                if mime != target:
                    return
                if change.startswith('observed_'):
                    return
                file_id = self.calls[-1][1]
                if change == 'missing_parent':
                    self.files[file_id]['parents'] = []
                    return
                if change == 'wrong_single_type':
                    self.files[file_id]['mimeType'] = 'text/plain'
                    return
                duplicate = deepcopy(self.files[file_id])
                duplicate['id'] = 'duplicate'
                if change == 'duplicate_source':
                    duplicate['appProperties']['source'] = 'another-source'
                elif change == 'duplicate_type':
                    duplicate['mimeType'] = 'text/plain'
                self.files['duplicate'] = duplicate
                self.bodies['duplicate'] = 'Someone edited this.' if change == 'duplicate_content' else ''
                self.styles['duplicate'] = []
            def observe_document(self, file_id):
                observation = super().observe_document(file_id)
                if change == 'observed_source':
                    observation.metadata['appProperties']['source'] = 'another-source'
                elif change == 'observed_operation':
                    observation.metadata['appProperties']['operation'] = 'another-operation'
                elif change == 'observed_id':
                    observation.metadata['id'] = 'another-object'
                return observation
        remote = FaultRemote()
        plan = initialize_documents(index, remote, home=root / 'state')
        result = initialize_documents(index, remote, authorize(plan), home=root / 'state')
        store = StateStore(root / 'state', raw['id'])
        return index, remote, result, store

    def test_duplicates_cannot_be_hidden_by_type_source_or_content_filters(self):
        for target, changes in ((FOLDER, ('duplicate_source', 'duplicate_type')),
                                (DOC, ('duplicate_source', 'duplicate_type', 'duplicate_content'))):
            for change in changes:
                with self.subTest(target=target, change=change), TemporaryDirectory() as directory:
                    index, remote, result, store = self.scenario(Path(directory), target, change)
                    pending = [r for r in result.files if r.status == 'pending']
                    self.assertEqual(len(pending), 1, result)
                    self.assertEqual(pending[0].reason, 'ambiguous_identity')
                    bindings = read_json(store.path / 'bindings.json') if (store.path / 'bindings.json').exists() else {}
                    self.assertNotIn(pending[0].source_id, bindings)
                    before_calls = list(remote.calls)
                    recovered = recover_sync(index, remote, home=Path(directory) / 'state')
                    self.assertEqual(recovered.files[0].status, 'pending')
                    self.assertEqual(recovered.files[0].reason, 'ambiguous_identity')
                    self.assertEqual(remote.calls, before_calls)

    def test_unique_wrong_representation_reports_actual_created_identity(self):
        for target in (FOLDER, DOC):
            with self.subTest(target=target), TemporaryDirectory() as directory:
                _, remote, result, store = self.scenario(Path(directory), target, 'wrong_single_type')
                pending = next(r for r in result.files if r.status == 'pending')
                self.assertEqual(pending.reason, 'creation_identity_mismatch')
                self.assertIn(pending.destination, remote.files)
                self.assertEqual(len(store.pending()), 1)

    def test_root_parent_must_be_verifiable_before_binding(self):
        with TemporaryDirectory() as directory:
            _, _, result, store = self.scenario(Path(directory), FOLDER, 'missing_parent')
            self.assertEqual(result.files[0].status, 'pending')
            self.assertEqual(result.files[0].reason, 'creation_layout_mismatch')
            self.assertFalse((store.path / 'bindings.json').exists())

    def test_fresh_doc_observation_must_retain_created_identity(self):
        for change in ('observed_source', 'observed_operation', 'observed_id'):
            with self.subTest(change=change), TemporaryDirectory() as directory:
                _, _, result, store = self.scenario(Path(directory), DOC, change)
                pending = next(r for r in result.files if r.status == 'pending')
                self.assertEqual(pending.reason, 'creation_identity_mismatch')
                bindings = read_json(store.path / 'bindings.json')
                self.assertNotIn(pending.source_id, bindings)
