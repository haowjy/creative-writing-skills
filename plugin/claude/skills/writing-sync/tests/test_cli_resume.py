"""CLI resume dispatch tests; no OAuth, remote requests or signal handlers."""
from contextlib import nullcontext, redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from unittest.mock import patch
import json
import unittest

from drive_sync.batch_resume import ResumePlan
from drive_sync.cli import main
from drive_sync.executor import FileResult, SyncResult
from drive_sync.storage import Draft, commit
from test_index import fixture


class ResumeCLITests(unittest.TestCase):
    def run_cli(self, result, *flags):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / 'index.yaml'
            commit(index, Draft(fixture()), None)
            remote = object()
            token = Event()
            with patch('drive_sync.auth.authorized_session', return_value=nullcontext(object())), \
                 patch('drive_sync.google.GoogleDrive', return_value=remote), \
                 patch('drive_sync.batch_resume.resume_batches', return_value=result) as resume, \
                 patch('drive_sync.application.recover_sync', side_effect=AssertionError('Wrong dispatch')), \
                 patch('drive_sync.cli.cancellable', side_effect=lambda fn: fn(token)), \
                 redirect_stdout(StringIO()) as out:
                code = main(['--index', str(index), 'state', 'resume-batches',
                             '--operation', 'operation', '--state-home', str(root / 'state'), *flags])
                args, kwargs = resume.call_args
                self.assertEqual(args[:3], (index, remote, 'operation'))
                self.assertEqual(kwargs['home'], root / 'state')
                if '--apply' in flags:
                    self.assertEqual(args[3], 'reviewed-digest')
                    self.assertIs(kwargs['cancellation'], token)
                else:
                    self.assertEqual(len(args), 3)
                    self.assertNotIn('cancellation', kwargs)
                return code, json.loads(out.getvalue())

    def test_preview_calls_resume_service_not_recovery(self):
        plan = ResumePlan('index', 'index-hash', 'operation', 'source', 'remote',
                          1, 3, 'checkpoint', 'preparation', 'binding', 'source-hash')
        code, output = self.run_cli(plan)
        self.assertEqual(code, 0)
        self.assertEqual(output['digest'], plan.digest)
        self.assertEqual(output['plan']['completed_batches'], 1)

    def test_apply_translates_outcomes_and_authorization(self):
        for status, cancelled, expected in (('verified', False, 0), ('pending', False, 2),
                                             ('pending', True, 130)):
            with self.subTest(status=status, cancelled=cancelled):
                result = SyncResult((FileResult('source', status, 'reason'),), cancelled)
                code, output = self.run_cli(result, '--apply', '--plan-digest', 'reviewed-digest')
                self.assertEqual(code, expected)
                self.assertEqual(output['files'][0]['status'], status)

    def test_apply_without_digest_does_not_call_resume(self):
        with TemporaryDirectory() as directory:
            index = Path(directory) / 'index.yaml'
            commit(index, Draft(fixture()), None)
            with patch('drive_sync.auth.authorized_session') as auth, \
                 patch('drive_sync.google.GoogleDrive'), \
                 patch('drive_sync.batch_resume.resume_batches') as resume, \
                 redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    main(['--index', str(index), 'state', 'resume-batches', '--operation', 'operation', '--apply'])
                self.assertEqual(caught.exception.code, 2)
                resume.assert_not_called()
                auth.assert_not_called()
