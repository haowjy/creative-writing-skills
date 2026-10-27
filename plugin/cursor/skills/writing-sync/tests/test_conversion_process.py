from base64 import b64encode
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from drive_sync.conversion_process import ConversionLimits, execute
from drive_sync.conversion import render
from drive_sync.index import Diagnostic
from drive_sync.storage import digest


class ConversionProcessTests(unittest.TestCase):
    def test_subprocess_renderer_preserves_model_and_fingerprint(self):
        result = render(b'Hello **world**.\n', 'markdown')
        self.assertEqual(result.text, 'Hello world.\n')
        self.assertTrue(result.supported)
        self.assertEqual(result.styles[0].kind, 'strong')
        self.assertEqual(result.fingerprint, render(b'Hello **world**.\n', 'markdown').fingerprint)

    def test_actual_worker_wall_memory_and_output_limits_fail_closed(self):
        args = {'data': b64encode(b'x' * 10000).decode(), 'format': 'text'}
        limits = (ConversionLimits(wall_seconds=0.001),
                  ConversionLimits(memory_bytes=1024 * 1024),
                  ConversionLimits(output_bytes=128))
        for limit in limits:
            with self.subTest(limit=limit), self.assertRaises(Diagnostic) as caught:
                execute('render', args, limits=limit)
            self.assertEqual(caught.exception.code, 'conversion_resource_limit')

    def test_actual_cpu_bound_for_adversarial_return_matching(self):
        import signal
        import subprocess
        real = subprocess.run
        return_codes = []
        def observe(*args, **kwargs):
            result = real(*args, **kwargs)
            return_codes.append(result.returncode)
            return result
        text = 'a' * 50000
        source = ('<p>' + text + '</p>').encode()
        args = dict(source=b64encode(source).decode(), expected_source_hash=digest(source),
                    format='html', baseline_text=text + '\n', remote_text=text[:-1] + 'b\n')
        with patch('drive_sync.conversion_process.subprocess.run', side_effect=observe), self.assertRaises(Diagnostic) as caught:
            execute('return', args, limits=ConversionLimits(cpu_seconds=1, wall_seconds=10))
        self.assertEqual(caught.exception.code, 'conversion_resource_limit')
        self.assertEqual(len(return_codes), 1)
        self.assertIn(return_codes[0], (-signal.SIGKILL, -signal.SIGXCPU))

    def test_private_transport_cleanup_and_no_credential_environment(self):
        import subprocess
        real = subprocess.run
        paths = []
        def inspect(command, **kwargs):
            paths.append(Path(kwargs['cwd']))
            self.assertEqual(paths[-1].stat().st_mode & 0o777, 0o700)
            self.assertEqual((paths[-1] / 'request.json').stat().st_mode & 0o777, 0o600)
            self.assertNotIn('SECRET_TEST_TOKEN', kwargs['env'])
            self.assertFalse(kwargs.get('shell', False))
            return real(command, **kwargs)
        with patch.dict(os.environ, {'SECRET_TEST_TOKEN': 'do-not-pass'}), \
                patch('drive_sync.conversion_process.subprocess.run', side_effect=inspect):
            self.assertEqual(render(b'private text\n', 'text').text, 'private text\n')
            with self.assertRaises(Diagnostic):
                execute('render', {'data': 'YQ==', 'format': 'text'}, limits=ConversionLimits(wall_seconds=0.001))
        self.assertTrue(paths)
        self.assertTrue(all(not path.exists() for path in paths))

    def test_diagnostics_survive_transport_and_invalid_requests_never_spawn(self):
        with self.assertRaises(Diagnostic) as caught:
            render(b'\xff', 'text')
        self.assertEqual(caught.exception.code, 'invalid_text')
        with patch('drive_sync.conversion_process.subprocess.run') as run:
            with self.assertRaises(Diagnostic):
                execute('unknown', {})
            with self.assertRaises(Diagnostic):
                execute('render', {'data': 'too long'}, limits=ConversionLimits(input_bytes=1))
            run.assert_not_called()
