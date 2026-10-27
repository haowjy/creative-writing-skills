"""End-to-end metadata preservation through native and original return services."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import unittest

from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
from drive_sync.sources import snapshot
from drive_sync.storage import Draft, commit
from fake_google import FakeGoogle
from live_integration import authorize
from test_index import fixture


class ByteRemote(FakeGoogle):
    def __init__(self):
        super().__init__()
        self.data = {}

    def create(self, name, mime, source_id, operation_id, parent=None, data=None, import_mime=None):
        super().create(name, mime, source_id, operation_id, parent=parent)
        self.data[self.calls[-1][1]] = data

    def read_original(self, file_id):
        return self.data[file_id], self.metadata(file_id)


class MetadataApplicationTests(unittest.TestCase):
    def test_both_storage_return_paths_preserve_metadata_and_rerun_noop(self):
        for storage in ('original', 'google-doc'):
            with self.subTest(storage=storage), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'notes').mkdir()
                source = root / 'notes/a.md'
                source.write_bytes(b'Before\n')
                source.chmod(0o640)
                os.setxattr(source, 'user.drive-sync-fixture', b'opaque\x00metadata\xff')
                original = snapshot(source)
                raw = fixture()
                raw['policy']['default_storage'] = storage
                index = root / 'index.yaml'
                commit(index, Draft(raw), None)
                remote = ByteRemote() if storage == 'original' else FakeGoogle()
                if storage == 'google-doc':
                    plan = initialize_documents(index, remote, home=root / 'state')
                    result = initialize_documents(index, remote, authorize(plan), home=root / 'state')
                    self.assertTrue(all(f.status == 'verified' for f in result.files))
                plan = combined_plan(preview_sync(index, remote, home=root / 'state'))
                result = apply_reviewed(index, remote, authorize(plan), home=root / 'state')
                self.assertTrue(all(f.status in ('verified', 'noop') for f in result.files))
                file_id = next(k for k, v in remote.files.items() if v['name'] == 'a.md')
                if storage == 'original':
                    remote.data[file_id] = b'After\n'
                else:
                    remote.bodies[file_id] = 'After\n'
                remote.files[file_id]['version'] = str(int(remote.files[file_id]['version']) + 1)
                remote.calls.clear()
                plan = combined_plan(preview_sync(index, remote, home=root / 'state'))
                self.assertEqual([o.direction for o in plan.operations], ['noop', 'pull'])
                result = apply_reviewed(index, remote, authorize(plan), home=root / 'state')
                self.assertEqual([f.status for f in result.files], ['noop', 'verified'])
                actual = snapshot(source)
                self.assertEqual(actual.data, b'After\n')
                self.assertEqual(actual.metadata, original.metadata)
                records = list((root / 'state').rglob('*.metadata-*.json'))
                self.assertEqual(len(records), 1)
                record = json.loads(records[0].read_text())
                self.assertEqual(record['content_hash'], original.digest)
                self.assertEqual(bytes.fromhex(record['attributes']['user.drive-sync-fixture']),
                                 b'opaque\x00metadata\xff')
                plan = combined_plan(preview_sync(index, remote, home=root / 'state'))
                self.assertTrue(all(o.direction == 'noop' for o in plan.operations))
                result = apply_reviewed(index, remote, authorize(plan), home=root / 'state')
                self.assertTrue(all(f.status == 'noop' for f in result.files))
                self.assertEqual(remote.calls, [])
                self.assertEqual(snapshot(source).metadata, original.metadata)
