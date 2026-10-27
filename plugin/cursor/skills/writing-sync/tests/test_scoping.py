from contextlib import nullcontext, redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from drive_sync.application import (preview_sync, combined_plan, apply_reviewed,
                                    initialize_documents, initialize_folders)
from drive_sync.index import Diagnostic
from drive_sync.storage import Draft, commit
from drive_sync.planner import Authorization
from fake_google import FakeGoogle
from test_index import fixture


def authorize(plan):
    return Authorization(plan.digest, plan.index_id,
                         frozenset(o.source_id for o in plan.operations),
                         frozenset(('create', 'push', 'pull')))


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('one', 'two'):
            directory = self.root / 'notes' / name
            directory.mkdir(parents=True)
            (directory / (name + '.txt')).write_text(name + '\n')
        self.index = self.root / 'index.yaml'
        commit(self.index, Draft(fixture()), None)
        self.remote = FakeGoogle()
        self.home = self.root / 'state'
        full = combined_plan(preview_sync(self.index, self.remote, home=self.home))
        self.ids = {o.local.path: o.source_id for o in full.operations}
        self.scope = frozenset([self.ids['notes/one/one.txt']])

    def preview(self, scope=None):
        return combined_plan(preview_sync(self.index, self.remote, home=self.home, source_ids=scope))

    def test_scoped_initialization_population_and_parent_dependencies(self):
        plan = initialize_documents(self.index, self.remote, home=self.home, source_ids=self.scope)
        self.assertEqual([o.local.path for o in plan.operations], ['notes/.', 'notes/one', 'notes/one/one.txt'])
        result = initialize_documents(self.index, self.remote, authorize(plan), home=self.home, source_ids=self.scope)
        self.assertEqual([f.status for f in result.files], ['verified'] * 3)
        self.assertEqual({f['name'] for f in self.remote.files.values()}, {'Notes', 'one', 'one.txt'})
        plan = self.preview(self.scope)
        result = apply_reviewed(self.index, self.remote, authorize(plan), home=self.home, source_ids=self.scope)
        self.assertEqual([f.status for f in result.files], ['noop', 'noop', 'verified'])
        self.assertTrue(all(o.direction == 'noop' for o in self.preview(self.scope).operations))
        self.assertTrue(any(o.direction == 'create' for o in self.preview().operations))

    def test_scope_cannot_be_widened_with_existing_approval(self):
        scoped = self.preview(self.scope)
        with self.assertRaises(Diagnostic):
            apply_reviewed(self.index, self.remote, authorize(scoped), home=self.home)
        self.assertEqual(self.remote.calls, [])
        for scope in (frozenset(), frozenset(['unknown']), self.scope | {'unknown'}):
            with self.assertRaises(Diagnostic) as caught:
                self.preview(scope)
            self.assertEqual(caught.exception.code, 'invalid_sync_scope')
        self.assertEqual(self.remote.calls, [])

    def test_folder_scope_has_ancestors_not_sibling_or_child_writes(self):
        scope = frozenset([self.ids['notes/one']])
        plan = initialize_folders(self.index, self.remote, home=self.home, source_ids=scope)
        self.assertEqual([o.local.path for o in plan.operations], ['notes/.', 'notes/one'])
        result = initialize_folders(self.index, self.remote, authorize(plan), home=self.home, source_ids=scope)
        self.assertTrue(all(f.status == 'verified' for f in result.files))
        self.assertEqual(len(self.remote.files), 2)

    def test_unselected_content_changes_are_not_applied(self):
        plan = initialize_documents(self.index, self.remote, home=self.home)
        initialize_documents(self.index, self.remote, authorize(plan), home=self.home)
        plan = self.preview()
        apply_reviewed(self.index, self.remote, authorize(plan), home=self.home)
        self.remote.calls.clear()
        for name in ('one', 'two'):
            (self.root / 'notes' / name / (name + '.txt')).write_text('Edited ' + name + '\n')
        plan = self.preview(self.scope)
        result = apply_reviewed(self.index, self.remote, authorize(plan), home=self.home, source_ids=self.scope)
        self.assertTrue(all(f.status in ('verified', 'noop') for f in result.files))
        two = next(k for k, v in self.remote.files.items() if v['name'] == 'two.txt')
        self.assertEqual(self.remote.bodies[two], 'two\n')
        self.assertEqual(len(self.remote.calls), 1)
        self.assertEqual(next(o.direction for o in self.preview().operations
                              if o.source_id == self.ids['notes/two/two.txt']), 'push')

    def test_cli_scoped_preview_and_initialization(self):
        from drive_sync.cli import main
        args = ['--index', str(self.index), 'sync', '--initialize', '--source', next(iter(self.scope)),
                '--state-home', str(self.home)]
        with patch('drive_sync.auth.authorized_session', return_value=nullcontext(object())), \
                patch('drive_sync.google.GoogleDrive', return_value=self.remote):
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(args), 0)
            plan = json.loads(output.getvalue())
            self.assertEqual(len(plan['plan']['operations']), 3)
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(args + ['--apply', '--plan-digest', plan['digest']]), 0)
            self.assertEqual(len(json.loads(output.getvalue())['files']), 3)
