"""Strict state decoding must fail before ambiguous recovery can act."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import uuid
from drive_sync.index import Diagnostic
from drive_sync.state import StateStore, read_json, write_json


class StateJSONTests(unittest.TestCase):
    def test_duplicate_and_nonfinite_values_rejected_without_echoing_data(self):
        cases = (b'{"status":"pending","status":"verified"}',
                 b'{"nested":{"remote_id":"a","remote_id":"b"}}',
                 b'{"revision":NaN}', b'{"revision":1e999}', b'{"revision":Infinity}',
                 b'{"revision":-Infinity}', b'{"private":"SECRET",broken}',
                 b'[' * 2000 + b']' * 2000)
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'record.json'
            for data in cases:
                with self.subTest(data=data[:40]):
                    path.write_bytes(data)
                    with self.assertRaises(Diagnostic) as caught:
                        read_json(path)
                    error = caught.exception
                    self.assertEqual(error.code, 'corrupt_state')
                    self.assertEqual(error.source, str(path))
                    self.assertEqual(error.operation, 'read-state')
                    self.assertNotIn('SECRET', str(error.as_dict()))
                    self.assertEqual(path.read_bytes(), data)

    def test_invalid_write_preserves_prior_record(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'record.json'
            write_json(path, {'status': 'pending'})
            original = path.read_bytes()
            cycle = []
            cycle.append(cycle)
            for value in (float('nan'), float('inf'), float('-inf'), object(), cycle):
                with self.assertRaises(Diagnostic) as caught:
                    write_json(path, {'value': value})
                self.assertEqual(caught.exception.code, 'invalid_state')
                self.assertEqual(path.read_bytes(), original)

    def test_duplicate_journal_status_cannot_hide_pending_write(self):
        with TemporaryDirectory() as directory:
            store = StateStore(Path(directory), str(uuid.uuid4()))
            operation = str(uuid.uuid4())
            path = store.journals / (operation + '.json')
            path.write_text('{"status":"pending","status":"verified"}')
            with self.assertRaises(Diagnostic) as caught:
                store.pending()
            self.assertEqual(caught.exception.code, 'corrupt_state')

    def test_valid_unicode_round_trip(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'record.json'
            value = {'title': '😀', 'nested': [{'before': None, 'after': 42}]}
            write_json(path, value)
            self.assertEqual(read_json(path), value)
