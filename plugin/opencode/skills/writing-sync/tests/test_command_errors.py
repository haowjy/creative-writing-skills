"""Command-level failure context and preauthorization checks, without Google."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from drive_sync.cli import main
from drive_sync.index import Diagnostic
from drive_sync.storage import Draft, commit, parse_edits
from test_index import fixture


INDEX_COMMANDS = (
    ('index', 'show'), ('index', 'validate'), ('index', 'preview'),
    ('index', 'edit', '--expected-digest', 'digest', '--edits', '[]'),
    ('conversion', 'check'), ('sync',), ('sync', '--initialize'), ('sync', '--folders-only'),
    ('source', 'rebind', '--source', 'sid', '--root', 'notes', '--path', 'a.md'),
    ('source', 'preview-return', '--source', 'sid'),
    ('state', 'recover'),
    *(( 'state', command, '--operation', 'oid') for command in
      ('close-unchanged', 'resume-batches', 'repair-batches', 'repair-created-layout', 'repair-created-content')),
    ('state', 'acknowledge-missing', '--source', 'sid'),
    ('state', 'rebaseline', '--source', 'sid'),
    ('conflict', 'inspect', '--source', 'sid'),
    ('conflict', 'resolve', '--source', 'sid', '--choice', 'keep-local'),
)


class CommandErrorTests(unittest.TestCase):
    def invoke(self, args):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            result = main(args)
        self.assertEqual(out.getvalue(), '')
        self.assertNotIn('Traceback', err.getvalue())
        return result, json.loads(err.getvalue())['error']

    def test_all_index_command_missing_paths_have_context_without_auth(self):
        with TemporaryDirectory() as directory, patch('drive_sync.auth.authorized_session') as auth:
            index = str(Path(directory) / 'missing.yaml')
            for command in INDEX_COMMANDS:
                with self.subTest(command=command):
                    code, error = self.invoke(['--index', index, *command])
                    self.assertEqual(code, 2)
                    self.assertEqual(error['code'], 'local_io_error')
                    self.assertEqual(error['source'], index)
                    self.assertEqual(error['context']['index'], index)
                    self.assertTrue(error['operation'].startswith(command[0]))
                    self.assertIn('state recover', error['action'])
                    self.assertEqual(error['destination'], '')  # Unknown, not fabricated.
            auth.assert_not_called()

    def test_other_commands_redact_os_error_messages(self):
        cases = [
            (['--index', '/test/index.yaml', 'index', 'create'], 'drive_sync.cli.commit'),
            (['conversion', 'capabilities'], 'drive_sync.capabilities.format_capabilities'),
            (['auth', 'login', '--client', '/private/client.json'], 'drive_sync.auth.begin_login'),
            (['auth', 'pick-folder', '--client', '/private/client.json'], 'drive_sync.auth.begin_pick_folder'),
            (['auth', 'status'], 'drive_sync.auth.auth_status'),
            (['auth', 'logout'], 'drive_sync.auth.logout'),
        ]
        for command, target in cases:
            with self.subTest(command=command), patch(target, side_effect=OSError('secret-token-and-source-text')):
                code, error = self.invoke(command)
                self.assertEqual(code, 2)
                self.assertEqual(error['code'], 'local_io_error')
                self.assertNotIn('secret-token-and-source-text', json.dumps(error))
                self.assertTrue(error['operation'])

    def test_existing_diagnostic_context_is_preserved(self):
        problem = Diagnostic('revision_conflict', 'Changed.', 'Review both copies.',
                             '/actual/source.md', destination='remote-id', operation='push')
        with patch('drive_sync.cli.load_index', side_effect=problem):
            _, error = self.invoke(['--index', '/index.yaml', 'state', 'repair-batches', '--operation', 'journal-id'])
        self.assertEqual(error['source'], '/actual/source.md')
        self.assertEqual(error['destination'], 'remote-id')
        self.assertEqual(error['operation'], 'push')
        self.assertEqual(error['context']['operation'], 'journal-id')

    def test_missing_authorization_and_incompatible_flags_fail_before_io(self):
        commands = [c for c in INDEX_COMMANDS if c[0] == 'sync' or
                    c[:2] in (('source', 'rebind'), ('conflict', 'resolve')) or
                    (c[0] == 'state' and c[1] != 'recover')]
        requests = [[*c, '--apply'] for c in commands]
        requests.append(['sync', '--initialize', '--folders-only'])
        with patch('drive_sync.cli.load_index') as load, patch('drive_sync.auth.authorized_session') as auth:
            for command in requests:
                with self.subTest(command=command), redirect_stderr(StringIO()), self.assertRaises(SystemExit) as exit:
                    main(['--index', '/missing.yaml', *command])
                self.assertEqual(exit.exception.code, 2)
            load.assert_not_called()
            auth.assert_not_called()

    def test_malformed_edit_shapes_never_change_index(self):
        invalid = [None, {}, 'payload', [None], [1], [[]], [{}],
                   [{'operation': 'set', 'path': 'auth', 'value': 'x'}],
                   [{'operation': 'set', 'path': [1], 'value': 'x'}],
                   [{'operation': 'set', 'path': ['auth']}],
                   [{'operation': 'remove', 'path': ['auth'], 'unknown': True}]]
        with TemporaryDirectory() as directory:
            index = Path(directory) / 'index.yaml'
            loaded = commit(index, Draft(fixture()), None)
            before = index.read_bytes()
            for value in invalid:
                with self.subTest(value=value):
                    with self.assertRaises(Diagnostic):
                        parse_edits(value)
                    code, error = self.invoke(['--index', str(index), 'index', 'edit',
                        '--edits', json.dumps(value), '--expected-digest', loaded.digest, '--save'])
                    self.assertEqual(code, 2)
                    self.assertEqual(error['code'], 'invalid_edit')
                    self.assertEqual(error['operation'], 'index edit')
                    self.assertEqual(index.read_bytes(), before)
