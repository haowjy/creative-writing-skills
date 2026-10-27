"""Capability services work without importing or invoking a CLI."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from drive_sync.capabilities import check_conversion, format_capabilities
from drive_sync.storage import Draft, commit
from test_index import fixture


class CapabilityTests(unittest.TestCase):
    def test_invalid_format_does_not_hide_other_reports(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'notes').mkdir()
            (root / 'notes/a.txt').write_bytes(b'\xff invalid UTF-8')
            (root / 'notes/b.md').write_bytes(b'Valid **Markdown**.\n')
            (root / 'notes/c.bin').write_bytes(b'\x00\xff')
            raw = fixture()
            raw['policy']['overrides'] = [{'root': 'notes', 'glob': '*.bin', 'storage': 'original'}]
            index = root / 'index.yaml'
            commit(index, Draft(raw), None)
            reports = check_conversion(index)
            self.assertEqual(len(reports), 3)
            self.assertEqual([r.supported for r in reports], [False, True, True])
            self.assertEqual(reports[0].findings[0].code, 'invalid_text')
            self.assertIsNotNone(reports[1].fingerprint)
            self.assertEqual(reports[2].storage, 'original')
            self.assertEqual(reports[0].return_policy, 'not_evaluated')
            self.assertEqual(reports[1].return_policy, 'candidate_verification_required')
            self.assertEqual(reports[2].return_policy, 'guarded_original_bytes')
            self.assertFalse((root / 'state').exists())

    def test_unreadable_original_is_not_claimed_supported(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'notes').mkdir()
            (root / 'notes/a.txt').write_bytes(b'valid')
            raw = fixture()
            raw['policy']['default_storage'] = 'original'
            index = root / 'index.yaml'
            commit(index, Draft(raw), None)
            with patch('drive_sync.capabilities.snapshot', side_effect=PermissionError('private detail')):
                reports = check_conversion(index)
            self.assertFalse(reports[0].supported)
            self.assertEqual(reports[0].findings[0].code, 'source_unreadable')
            self.assertNotIn('private detail', str(reports))

    def test_capability_table_is_offline_and_conditional_for_all_four_formats(self):
        with patch('drive_sync.capabilities.snapshot', side_effect=AssertionError('Unexpected I/O')):
            capabilities = format_capabilities()
        self.assertEqual({c.format for c in capabilities}, {'markdown', 'text', 'html', 'epub'})
        for capability in capabilities:
            self.assertTrue(capability.return_requires_candidate_verification)
            self.assertTrue(capability.protected_material)
            self.assertIn('requiredRevisionId', capability.update_route)
            self.assertTrue(capability.return_route)

    def test_blocked_source_does_not_claim_return_support(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'notes').mkdir()
            (root / 'notes/a.html').write_text('<p>Text</p><script>danger()</script>')
            index = root / 'index.yaml'
            commit(index, Draft(fixture()), None)
            report, = check_conversion(index)
            self.assertFalse(report.supported)
            self.assertEqual(report.return_policy, 'blocked_by_source_conversion')

    def test_cli_capabilities_needs_no_index_or_credentials(self):
        from contextlib import redirect_stdout
        from io import StringIO
        import json
        from drive_sync.cli import main
        with patch('drive_sync.auth.authorized_session', side_effect=AssertionError('Unexpected OAuth')), \
                patch('drive_sync.cli.load_index', side_effect=AssertionError('Unexpected index')), \
                redirect_stdout(StringIO()) as output:
            self.assertEqual(main(['conversion', 'capabilities']), 0)
        self.assertEqual(len(json.loads(output.getvalue())['formats']), 4)
