from pathlib import Path
import tempfile
import stat
import unittest
from drive_sync.index import Diagnostic
from drive_sync.sources import commit_candidate, snapshot


class SourceTests(unittest.TestCase):
    def test_unrestorable_owner_blocks_atomic_replacement(self):
        from dataclasses import replace
        from unittest.mock import patch
        from drive_sync.file_metadata import restore
        from drive_sync.storage import atomic_write
        original = snapshot(self.path)
        expected = replace(original.metadata, uid=original.metadata.uid + 1)
        with patch('drive_sync.file_metadata.os.fchown', side_effect=PermissionError('ownership denied')):
            with self.assertRaises(Diagnostic) as caught:
                atomic_write(self.path, b'candidate', mode=original.mode,
                             prepare_fd=lambda fd: restore(fd, expected))
        self.assertEqual(caught.exception.code, 'source_metadata_restore_failed')
        self.assertEqual(self.path.read_bytes(), original.data)

    def test_posix_acl_survives_return_when_acl_tools_are_available(self):
        import os
        import shutil
        import subprocess
        if not shutil.which('setfacl') or not shutil.which('getfacl'):
            self.skipTest('Optional POSIX ACL test tools are unavailable')
        subprocess.run(['setfacl', '-m', f'u:{os.getuid() + 1}:r--', str(self.path)], check=True, capture_output=True)
        before = subprocess.check_output(['getfacl', '-cpn', str(self.path)])
        original = snapshot(self.path)
        self.assertIn('system.posix_acl_access', dict(original.metadata.attributes))
        commit_candidate(original, b'updated ACL content\n', self.path.parent / 'backup')
        self.assertEqual(subprocess.check_output(['getfacl', '-cpn', str(self.path)]), before)
        self.assertEqual(snapshot(self.path).metadata, original.metadata)

    def test_extended_attributes_and_ownership_survive_return(self):
        import os
        import json
        os.setxattr(self.path, 'user.drive-sync-test', b'\x00opaque\xff')
        self.path.chmod(0o640)
        original = snapshot(self.path)
        result = commit_candidate(original, b'edited metadata\n', self.path.parent / 'backup')
        self.assertEqual(result.metadata, original.metadata)
        self.assertEqual(os.getxattr(self.path, 'user.drive-sync-test'), b'\x00opaque\xff')
        self.assertEqual((self.path.stat().st_uid, self.path.stat().st_gid),
                         (original.metadata.uid, original.metadata.gid))
        record = json.loads(next((self.path.parent / 'backup').glob('*.metadata-*.json')).read_text())
        self.assertEqual(record['attributes']['user.drive-sync-test'], b'\x00opaque\xff'.hex())
        self.assertEqual(record['mode'], 0o640)

    def test_changed_extended_attribute_blocks_replacement(self):
        import os
        os.setxattr(self.path, 'user.drive-sync-test', b'before')
        original = snapshot(self.path)
        os.setxattr(self.path, 'user.drive-sync-test', b'concurrent')
        with self.assertRaises(Diagnostic) as caught:
            commit_candidate(original, b'candidate', self.path.parent / 'backup')
        self.assertEqual(caught.exception.code, 'source_race')
        self.assertEqual(self.path.read_bytes(), original.data)
        self.assertEqual(os.getxattr(self.path, 'user.drive-sync-test'), b'concurrent')

    def test_failed_metadata_restoration_never_replaces_source(self):
        import os
        from unittest.mock import patch
        os.setxattr(self.path, 'user.drive-sync-test', b'original')
        original = snapshot(self.path)
        with patch('drive_sync.file_metadata.os.setxattr', side_effect=PermissionError('private failure')):
            with self.assertRaises(Diagnostic) as caught:
                commit_candidate(original, b'candidate', self.path.parent / 'backup')
        self.assertEqual(caught.exception.code, 'source_metadata_restore_failed')
        self.assertEqual(self.path.read_bytes(), original.data)
        self.assertEqual(snapshot(self.path).metadata, original.metadata)
        self.assertFalse(list(self.path.parent.glob('.source.md.*')))
        self.assertNotIn('private failure', str(caught.exception.as_dict()))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'source.md'
        self.path.write_bytes(b'original\r\n')

    def test_snapshot_and_commit(self):
        original = snapshot(self.path)
        result = commit_candidate(original, b'edited\r\n', self.path.parent / 'backup')
        self.assertEqual(result.data, b'edited\r\n')
        self.assertEqual((self.path.parent / 'backup' / (original.digest + '.source')).read_bytes(), b'original\r\n')

    def test_race_preserves_current(self):
        original = snapshot(self.path)
        self.path.write_bytes(b'concurrent')
        with self.assertRaises(Diagnostic):
            commit_candidate(original, b'candidate', self.path.parent / 'backup')
        self.assertEqual(self.path.read_bytes(), b'concurrent')

    def test_symlink_and_size(self):
        with self.assertRaises(Diagnostic):
            snapshot(self.path, max_bytes=2)
        alias = self.path.parent / 'alias'
        alias.symlink_to(self.path)
        with self.assertRaises(Diagnostic):
            snapshot(alias)

    def test_source_permissions_preserved_backups_private(self):
        for mode in (0o640, 0o644, 0o755):
            with self.subTest(mode=oct(mode)):
                self.path.chmod(mode)
                original = snapshot(self.path)
                commit_candidate(original, b'edited permissions\n', self.path.parent / 'backup')
                self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), mode)
                for backup in (self.path.parent / 'backup').iterdir():
                    self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)

    def test_permission_change_blocks_candidate(self):
        self.path.chmod(0o644)
        original = snapshot(self.path)
        self.path.chmod(0o600)
        with self.assertRaises(Diagnostic) as caught:
            commit_candidate(original, b'candidate', self.path.parent / 'backup')
        self.assertEqual(caught.exception.code, 'source_race')
        self.assertEqual(self.path.read_bytes(), original.data)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)

    def test_special_permission_bits_block_replacement(self):
        self.path.chmod(0o2640)
        original = snapshot(self.path)
        with self.assertRaises(Diagnostic) as caught:
            commit_candidate(original, b'candidate', self.path.parent / 'backup')
        self.assertEqual(caught.exception.code, 'unsupported_source_permissions')
        self.assertEqual(self.path.read_bytes(), original.data)
