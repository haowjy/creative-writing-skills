from pathlib import Path
import tempfile
import unittest
import uuid
from drive_sync.conflicts import inspect_conflict
from drive_sync.state import StateStore, write_json
from test_index import fixture
from drive_sync.index import Diagnostic
from unittest.mock import patch


class ConflictTests(unittest.TestCase):
    def test_inspection_retains_three_versions_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            source = path/'source'
            source.write_bytes(b'local')
            store = StateStore(path/'state', fixture()['id'])
            identity = {'account': 'test-account', 'client': 'test-client'}
            store.bind_account(identity)
            source_id = str(uuid.uuid4())
            write_json(store.path/'bindings.json', {source_id:dict(kind='file', storage='original', path=str(source),
                remote_id='remote', source_blob=store.save_blob(b'base'))})
            class Remote:
                def read_original(self, file_id):
                    return b'remote', {'id': file_id, 'version':'2', 'appProperties': {'source': source_id}}
            remote = Remote()
            remote.identity = identity
            review = inspect_conflict(store, remote, source_id)
            self.assertEqual(source.read_bytes(),b'local')
            self.assertEqual((review.directory/'base.source').read_bytes(),b'base')
            self.assertEqual((review.directory/'remote.original').read_bytes(),b'remote')
            self.assertEqual((review.directory/'local.source').stat().st_mode & 0o777, 0o600)

    def test_wrong_profile_blocks_before_source_or_remote_reads(self):
        for identity in ({'account': 'other', 'client': 'client'},
                         {'account': 'account', 'client': 'other'}, None):
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as directory:
                store = StateStore(Path(directory), fixture()['id'])
                store.bind_account({'account': 'account', 'client': 'client'})
                class Remote:
                    def read_original(self, file_id):
                        raise AssertionError('Remote content must not be read')
                remote = Remote()
                remote.identity = identity
                with patch('drive_sync.conflicts.snapshot', side_effect=AssertionError('Source must not be read')):
                    with self.assertRaises(Diagnostic) as caught:
                        inspect_conflict(store, remote, str(uuid.uuid4()))
                self.assertIn(caught.exception.code, ('wrong_account', 'unverified_account'))
                self.assertFalse((store.path / 'reviews').exists())

    def test_wrong_adapter_index_blocks_inspection(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory:
            store = StateStore(Path(directory), fixture()['id'])
            identity = {'account': 'account', 'client': 'client'}
            store.bind_account(identity)
            remote = SimpleNamespace(identity=identity, index_id=str(uuid.uuid4()))
            with self.assertRaises(Diagnostic) as caught:
                inspect_conflict(store, remote, str(uuid.uuid4()))
            self.assertEqual(caught.exception.code, 'wrong_state')
            self.assertFalse((store.path / 'reviews').exists())

    def test_wrong_remote_source_never_stages_review(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.write_bytes(b'local')
            store = StateStore(root / 'state', fixture()['id'])
            identity = {'account': 'account', 'client': 'client'}
            store.bind_account(identity)
            source_id = str(uuid.uuid4())
            write_json(store.path / 'bindings.json', {source_id: dict(kind='file', storage='original',
                path=str(source), remote_id='remote', source_blob=store.save_blob(b'base'))})
            remote = SimpleNamespace(identity=identity, read_original=lambda file_id:
                (b'unrelated', {'id': file_id, 'version': '2', 'appProperties': {'source': 'other'}}))
            with self.assertRaises(Diagnostic) as caught:
                inspect_conflict(store, remote, source_id)
            self.assertEqual(caught.exception.code, 'wrong_remote_source')
            self.assertFalse((store.path / 'reviews').exists())
            self.assertEqual(source.read_bytes(), b'local')

    def test_native_inspection_checks_identity_and_keeps_semantic_evidence(self):
        from types import SimpleNamespace
        from test_document_model import observation
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source.md'
            source.write_bytes(b'Local<!-- retained -->\n')
            store = StateStore(root / 'state', fixture()['id'])
            identity = {'account': 'account', 'client': 'client'}
            store.bind_account(identity)
            source_id = str(uuid.uuid4())
            write_json(store.path / 'bindings.json', {source_id: dict(kind='file', storage='google-doc',
                path=str(source), remote_id='doc', source_blob=store.save_blob(b'Base\n'))})
            observed = observation()
            observed.metadata['appProperties'] = {'source': source_id}
            remote = SimpleNamespace(identity=identity, observe_document=lambda file_id: observed)
            review = inspect_conflict(store, remote, source_id)
            self.assertEqual((review.directory / 'remote.txt').read_bytes(), b'Hello\n')
            self.assertEqual(source.read_bytes(), b'Local<!-- retained -->\n')
            observed.metadata['appProperties']['source'] = 'wrong'
            with self.assertRaises(Diagnostic):
                inspect_conflict(store, remote, source_id)
            self.assertEqual(len(list((store.path / 'reviews').iterdir())), 1)
