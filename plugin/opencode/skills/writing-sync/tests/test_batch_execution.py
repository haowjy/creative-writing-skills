from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
import uuid
from unittest.mock import patch

from drive_sync.batch_execution import close_unchanged_attempt, run_sequence, recover_sequence
from drive_sync.batching import plan_batches
from drive_sync.document_model import read_document
from drive_sync.google import DOC, fingerprint
from drive_sync.index import Diagnostic
from drive_sync.state import StateStore, read_json, write_json
from fake_google import FakeGoogle
from test_index import fixture


class ReceiptFake(FakeGoogle):
    lose_response = False
    lose_read = False
    after_write = None
    def update_document(self, observation, batch):
        file_id = observation.metadata['id']
        assert batch['writeControl']['requiredRevisionId'] == self.files[file_id]['version']
        self.calls.append(batch)
        self.files[file_id]['version'] = str(int(self.files[file_id]['version']) + 1)
        if self.after_write:
            self.after_write()
        if self.lose_response:
            raise TimeoutError('lost write response')
        return {'documentId': file_id, 'writeControl': {'requiredRevisionId': self.files[file_id]['version']}}
    def observe_document(self, file_id):
        if self.lose_read and self.calls:
            raise TimeoutError('lost read')
        return super().observe_document(file_id)


class BatchExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = StateStore(Path(self.temp.name), fixture()['id'])
        self.remote = ReceiptFake()
        self.remote.create('a.md', DOC, 'source', 'initial')
        self.remote.calls.clear()
        self.initial = asdict(read_document(self.remote.observe_document('id-1')).snapshot)
        self.operation_id = str(uuid.uuid4())
        self.segments = plan_batches({'writeControl': {'requiredRevisionId': '1'},
                                     'requests': [{'updateTextStyle': {}}] * 3}, max_requests=1)
        self.path = self.store.journals / (self.operation_id + '.batches') / 'sequence.json'

    def run_batches(self, **kwargs):
        with self.store.lock():
            return run_sequence(self.store, self.operation_id, 'id-1', self.segments,
                                self.initial, self.remote, lambda: None, **kwargs)

    def test_each_batch_uses_read_back_revision_and_no_baseline_commit(self):
        self.assertTrue(self.run_batches())
        self.assertEqual([b['writeControl']['requiredRevisionId'] for b in self.remote.calls], ['1', '2', '3'])
        self.assertEqual(len(read_json(self.path)['verified']), 3)
        self.assertFalse((self.store.path / 'bindings.json').exists())

    def test_lost_response_never_replays(self):
        self.remote.lose_response = True
        with self.assertRaises(TimeoutError):
            self.run_batches()
        with self.assertRaises(Diagnostic):
            self.run_batches(reviewed_resume=True)
        self.assertEqual(len(self.remote.calls), 1)

    def test_lost_read_can_reconcile_receipt_before_reviewed_resume(self):
        self.remote.lose_read = True
        with self.assertRaises(TimeoutError):
            self.run_batches()
        self.remote.lose_read = False
        with self.store.lock():
            self.assertEqual(len(recover_sequence(self.path, self.remote)['verified']), 1)
        self.assertEqual(len(self.remote.calls), 1)
        self.assertTrue(self.run_batches(reviewed_resume=True))
        self.assertEqual(len(self.remote.calls), 3)

    def test_cancellation_and_interbatch_remote_edit(self):
        token = threading.Event()
        self.remote.after_write = token.set
        self.assertFalse(self.run_batches(cancellation=token))
        self.assertEqual(len(self.remote.calls), 1)

        self.remote.files['id-1']['version'] = 'unexpected'
        with self.assertRaises(Diagnostic):
            self.run_batches(reviewed_resume=True)
        self.assertEqual(len(self.remote.calls), 1)

    def test_corrupted_checkpoint_cannot_skip_a_batch(self):
        token = threading.Event()
        self.remote.after_write = token.set
        self.assertFalse(self.run_batches(cancellation=token))
        record = read_json(self.path)
        record['verified'][0]['segment'] = 2
        write_json(self.path, record)
        with self.assertRaises(Diagnostic):
            self.run_batches(reviewed_resume=True)
        self.assertEqual(len(self.remote.calls), 1)

    def unchanged_attempt(self):
        with patch.object(self.remote, 'update_document', side_effect=TimeoutError):
            with self.assertRaises(TimeoutError):
                self.run_batches()
        return fingerprint(read_json(self.path))

    def test_unchanged_closure_rechecks_remote_and_retains_marker_on_race(self):
        checkpoint = self.unchanged_attempt()
        before = self.path.read_bytes()
        self.remote.files['id-1']['version'] = 'changed-after-review'
        with self.assertRaises(Diagnostic):
            close_unchanged_attempt(self.path, self.remote, checkpoint, 'authorization')
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob('unchanged-*.json')), [])
        self.assertEqual(self.remote.calls, [])

    def test_unchanged_closure_crash_keeps_audit_and_requires_review_again(self):
        checkpoint = self.unchanged_attempt()
        before = self.path.read_bytes()
        def crash_on_clear(path, value):
            if path == self.path:
                raise OSError('synthetic state write failure')
            write_json(path, value)
        with patch('drive_sync.batch_execution.write_json', side_effect=crash_on_clear):
            with self.assertRaises(OSError):
                close_unchanged_attempt(self.path, self.remote, checkpoint, 'authorization')
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(len(list(self.path.parent.glob('unchanged-*.json'))), 1)
        with self.assertRaises(Diagnostic):
            self.run_batches(reviewed_resume=True)
        self.assertEqual(self.remote.calls, [])
        close_unchanged_attempt(self.path, self.remote, checkpoint, 'authorization')
        self.assertIsNone(read_json(self.path)['inflight'])
        self.assertEqual(self.remote.calls, [])
        self.assertTrue(self.run_batches(reviewed_resume=True))
