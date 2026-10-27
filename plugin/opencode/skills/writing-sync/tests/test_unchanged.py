from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from drive_sync.document_model import read_document
from drive_sync.executor import Prepared, save_prepared
from drive_sync.google import DOC
from drive_sync.index import Diagnostic
from drive_sync.state import StateStore, write_json
from drive_sync.storage import Draft, commit
from drive_sync.unchanged import close_unchanged
from fake_google import FakeGoogle
from test_index import fixture


class UnchangedTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.index = self.path / 'index.yaml'
        raw = fixture()
        commit(self.index, Draft(raw), None)
        self.store = StateStore(self.path / 'state', raw['id'])
        self.remote = FakeGoogle()
        self.store.bind_account(self.remote.identity)
        self.remote.create('a.md', DOC, 'source', 'initial')
        self.remote.calls.clear()
        self.intent = self.store.begin('source', 'push', 'old', 'desired', 'id-1')
        binding = dict(kind='file', storage='google-doc', remote_id='id-1',
                       prior_remote=asdict(read_document(self.remote.observe_document('id-1')).snapshot))
        save_prepared(self.store, self.intent, Prepared('source', 'old', 'desired', b'data', binding))
        write_json(self.store.path / 'bindings.json', {'source': {'preserved': 'baseline'}})

    def test_close_preserves_baselines_and_audit_without_remote_writes(self):
        before = (self.store.path / 'bindings.json').read_bytes()
        plan = close_unchanged(self.index, self.store, self.remote, self.intent.id)
        result = close_unchanged(self.index, self.store, self.remote, self.intent.id, plan.digest)
        self.assertFalse(result['baseline_advanced'])
        self.assertEqual(self.store.pending(), ())
        self.assertEqual((self.store.path / 'bindings.json').read_bytes(), before)
        self.assertTrue((self.store.journals / (self.intent.id + '.closure.json')).exists())
        self.assertEqual(self.remote.calls, [])

    def test_changed_remote_and_stale_authorization_block(self):
        plan = close_unchanged(self.index, self.store, self.remote, self.intent.id)
        with self.assertRaises(Diagnostic):
            close_unchanged(self.index, self.store, self.remote, self.intent.id, 'wrong')
        self.remote.files['id-1']['version'] = '2'
        with self.assertRaises(Diagnostic):
            close_unchanged(self.index, self.store, self.remote, self.intent.id, plan.digest)
        self.assertEqual(len(self.store.pending()), 1)

    def test_create_cannot_be_dismissed(self):
        write_json(self.store.journals / (self.intent.id + '.json'), asdict(self.intent) | {'kind': 'create'})
        with self.assertRaises(Diagnostic):
            close_unchanged(self.index, self.store, self.remote, self.intent.id)
