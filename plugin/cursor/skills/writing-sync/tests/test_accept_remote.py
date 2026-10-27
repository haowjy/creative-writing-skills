"""Explicit conflict resolution must discard reviewed local edits, not baseline structure."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed, resolve_reviewed
from drive_sync.storage import Draft, commit
from fake_google import FakeGoogle
from live_integration import authorize
from test_index import fixture


class AcceptRemoteTests(unittest.TestCase):
    def test_accept_remote_uses_verified_source_and_retains_local_backup(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'notes').mkdir()
            source = root / 'notes/a.md'
            source.write_bytes(b'First sentence.<!-- protected -->\n')
            index = root / 'index.yaml'
            commit(index, Draft(fixture()), None)
            remote = FakeGoogle()
            plan = initialize_documents(index, remote, home=root / 'state')
            initialize_documents(index, remote, authorize(plan), home=root / 'state')
            plan = combined_plan(preview_sync(index, remote, home=root / 'state'))
            apply_reviewed(index, remote, authorize(plan), home=root / 'state')
            file_id = next(i for i, m in remote.files.items() if m['name'] == 'a.md')
            source_id = remote.files[file_id]['appProperties']['source']
            local = b'Local edited sentence.<!-- protected -->\n'
            source.write_bytes(local)
            remote.bodies[file_id] = 'Remote sentence.\n'
            remote.files[file_id]['version'] = str(int(remote.files[file_id]['version']) + 1)
            protected_change = local.replace(b'protected', b'new local annotation')
            source.write_bytes(protected_change)
            plan = resolve_reviewed(index, remote, source_id, 'accept-remote', home=root / 'state')
            blocked = resolve_reviewed(index, remote, source_id, 'accept-remote', authorize(plan), home=root / 'state')
            self.assertEqual(blocked.files[0].reason, 'protected_source_conflict')
            self.assertEqual(source.read_bytes(), protected_change)
            source.write_bytes(local)
            plan = resolve_reviewed(index, remote, source_id, 'accept-remote', home=root / 'state')
            result = resolve_reviewed(index, remote, source_id, 'accept-remote', authorize(plan), home=root / 'state')
            self.assertEqual(result.files[0].status, 'verified', result)
            self.assertEqual(source.read_bytes(), b'Remote sentence.<!-- protected -->\n')
            self.assertTrue(any(p.read_bytes() == local for p in (root / 'state').rglob('*.source')))
