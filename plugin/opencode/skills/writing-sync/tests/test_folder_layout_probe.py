from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
from drive_sync.index import Diagnostic
from drive_sync.state import read_json
from drive_sync.storage import Draft, commit
from fake_google import FakeGoogle
from live_folder_layout import run_folder_layout
from test_index import fixture
from test_scoping import authorize


class LayoutRemote(FakeGoogle):
    def metadata_guard(self, file_id):
        return self.metadata(file_id), self.files[file_id]['version']

    def update_layout(self, file_id, *, name, parent, before, etag):
        assert self.metadata(file_id) == before and etag == self.files[file_id]['version']
        self.files[file_id].update(name=name, parents=[parent], version=str(int(etag) + 1))
        self.calls.append(('layout', file_id))


class FolderLayoutProbeTests(unittest.TestCase):
    def test_probe_restores_metadata_only_and_refuses_repeat(self):
        with TemporaryDirectory() as directory:
            run = Path(directory)
            for parent in ('left', 'right'):
                (run / 'notes' / parent).mkdir(parents=True)
                for name in ('a', 'b'):
                    (run / 'notes' / parent / (name + '.txt')).write_text(parent + name + '\n')
            index = run / 'index.yaml'
            commit(index, Draft(fixture()), None)
            remote = LayoutRemote()
            plan = initialize_documents(index, remote, home=run / 'state')
            initialize_documents(index, remote, authorize(plan), home=run / 'state')
            plan = combined_plan(preview_sync(index, remote, home=run / 'state'))
            apply_reviewed(index, remote, authorize(plan), home=run / 'state')
            remote.calls.clear()
            with redirect_stdout(StringIO()):
                run_folder_layout(run, remote, authorize)
            record = read_json(run / 'folder-layout-probe.json')
            self.assertEqual(record['status'], 'verified')
            self.assertEqual(record['before_docs'], record['after_docs'])
            self.assertEqual([c[0] for c in remote.calls], ['layout'] * 4)
            with self.assertRaises(Diagnostic) as caught:
                run_folder_layout(run, None, None)
            self.assertEqual(caught.exception.code, 'probe_already_attempted')
