"""Offline safety tests for the opt-in disposable integration runner."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from drive_sync.google import DOC
from drive_sync.index import Diagnostic
from fake_google import FakeGoogle
from live_integration import edit_remote, edit_original, add_comment, stale_original, verify_nested
from drive_sync.state import write_json


class EditingFake(FakeGoogle):
    fail = False

    def update_document(self, observation, batch):
        self.calls.append(('edit', observation.metadata['id']))
        if self.fail:
            raise TimeoutError('synthetic uncertain write')
        assert batch['writeControl']['requiredRevisionId'] == observation.revision
        file_id = observation.metadata['id']
        self.bodies[file_id] = self.bodies[file_id].replace('First', 'Changed')
        self.files[file_id]['version'] = str(int(self.files[file_id]['version']) + 1)


class LiveRunnerTests(unittest.TestCase):
    def test_cyclic_verifier_checks_links_and_refuses_fixture_overwrite(self):
        from live_integration import seed_cyclic, verify_cyclic, authorize
        from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            run = Path(directory) / 'new-fixture'
            seed_cyclic(run)
            with self.assertRaises(FileExistsError):
                seed_cyclic(run)
            remote = FakeGoogle()
            index = run / 'index.yaml'
            plan = initialize_documents(index, remote, home=run / 'state')
            initialize_documents(index, remote, authorize(plan), home=run / 'state')
            plan = combined_plan(preview_sync(index, remote, home=run / 'state'))
            apply_reviewed(index, remote, authorize(plan), home=run / 'state')
            remote.calls.clear()
            verify_cyclic(run, remote)
            self.assertEqual(remote.calls, [])
            self.assertTrue((run / 'cyclic-verification.json').exists())
            file_id = next(k for k, v in remote.files.items() if v['name'] == 'a.md')
            remote.styles[file_id] = []
            with self.assertRaises(Diagnostic) as caught:
                verify_cyclic(run, remote)
            self.assertEqual(caught.exception.code, 'cyclic_verification_failed')
            self.assertEqual(remote.calls, [])

    def test_storage_probe_round_trip_retains_all_representations(self):
        from live_integration import replace_storage, authorize
        from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
        from drive_sync.storage import Draft, commit
        from drive_sync.import_payload import import_html
        from drive_sync.conversion import render
        from test_index import fixture
        payload = b'Changed markdown sentence.\n'
        class StorageFake(FakeGoogle):
            def __init__(self):
                super().__init__()
                self.originals = {}
            def create(self, name, mime, source_id, operation_id, parent=None, data=None, import_mime=None):
                super().create(name, mime, source_id, operation_id, parent=parent)
                file_id = self.calls[-1][1]
                if data is not None and mime == DOC:
                    # Fixed synthetic import only, not a fidelity implementation.
                    assert data == import_html(render(payload, 'markdown'))
                    self.bodies[file_id] = payload.decode()
                elif data is not None:
                    self.originals[file_id] = data
            def read_original(self, file_id):
                return self.originals[file_id], self.metadata(file_id)
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            run = Path(directory)
            (run / 'notes').mkdir()
            (run / 'notes/a-renamed.md').write_bytes(payload)
            index = run / 'index.yaml'
            commit(index, Draft(fixture()), None)
            remote = StorageFake()
            plan = initialize_documents(index, remote, home=run / 'state')
            initialize_documents(index, remote, authorize(plan), home=run / 'state')
            plan = combined_plan(preview_sync(index, remote, home=run / 'state'))
            apply_reviewed(index, remote, authorize(plan), home=run / 'state')
            remote.calls.clear()
            for mode in ('original', 'google-doc'):
                try:
                    replace_storage(run, remote, mode)
                except Diagnostic:
                    self.fail((run / ('replace-' + mode + '-result.json')).read_text())
                self.assertTrue((run / ('replace-' + mode + '-verified.json')).exists())
                count = len(remote.calls)
                with self.assertRaises(Diagnostic) as caught:
                    replace_storage(run, remote, mode)
                self.assertEqual(caught.exception.code, 'probe_already_attempted')
                self.assertEqual(len(remote.calls), count)
            self.assertEqual([call[0] for call in remote.calls], ['create', 'create'])
            self.assertEqual(len(remote.files), 4)  # One folder and three retained representations.

    def test_rebind_probe_preserves_identity_and_refuses_replay(self):
        from live_integration import rebind_file, authorize
        from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
        from drive_sync.storage import Draft, commit
        from test_index import fixture
        class LayoutFake(FakeGoogle):
            def metadata_guard(self, file_id):
                return self.metadata(file_id), self.files[file_id]['version']
            def update_layout(self, file_id, *, name, parent, before, etag):
                assert self.metadata(file_id) == before
                assert self.files[file_id]['version'] == etag
                self.files[file_id].update(name=name, parents=[parent], version=str(int(etag) + 1))
                self.calls.append(('layout', file_id))
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            run = Path(directory)
            (run / 'notes').mkdir()
            (run / 'notes/a.md').write_bytes(b'Changed markdown sentence.\n')
            index = run / 'index.yaml'
            commit(index, Draft(fixture()), None)
            remote = LayoutFake()
            plan = initialize_documents(index, remote, home=run / 'state')
            initialize_documents(index, remote, authorize(plan), home=run / 'state')
            plan = combined_plan(preview_sync(index, remote, home=run / 'state'))
            apply_reviewed(index, remote, authorize(plan), home=run / 'state')
            before_ids = set(remote.files)
            remote.calls.clear()
            rebind_file(run, remote)
            self.assertEqual(set(remote.files), before_ids)
            self.assertEqual(len(remote.calls), 1)
            self.assertEqual(remote.calls[0][0], 'layout')
            self.assertTrue((run / 'rebind-verification.json').exists())
            with self.assertRaises(Diagnostic) as caught:
                rebind_file(run, remote)
            self.assertEqual(caught.exception.code, 'probe_already_attempted')
            self.assertEqual(len(remote.calls), 1)

    def test_nested_verifier_rejects_wrong_parent_and_provenance(self):
        from test_index import fixture
        from drive_sync.storage import Draft, commit, load_index
        from drive_sync.state import StateStore
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            run = Path(directory)
            commit(run / 'index.yaml', Draft(fixture()), None)
            index = load_index(run / 'index.yaml').model
            path = run / 'notes/level1/level2'
            path.mkdir(parents=True)
            (path / 'g.md').write_bytes(b'Nested fixture. [Read parent](../../a.md).\n')
            names = [next(r.destination_name for r in index.roots if r.name == 'notes'), 'level1', 'level2', 'g.md', 'a.md']
            items = [{'id': str(i), 'name': name, 'parents': [str(i-1)],
                      'appProperties': {'source': str(i)}} for i, name in enumerate(names)]
            remote = SimpleNamespace(inventory=lambda: items,
                metadata=lambda key: items[int(key)], observe_document=lambda key: None)
            url = 'https://docs.google.com/document/d/4/edit'
            model = SimpleNamespace(text='Nested fixture. Read parent.\n',
                                    styles=[SimpleNamespace(kind='link', value=url)])
            store = StateStore(run / 'state', index.id)
            bindings = {'3': {'link_provenance': [{'source_href': '../../a.md',
                'destination_url': url, 'target_source_id': '4'}]}}
            write_json(store.path / 'bindings.json', bindings)
            with patch('live_integration.read_document', return_value=model):
                verify_nested(run, remote)
                self.assertTrue((run / 'nested-verification.json').exists())
                items[3]['parents'] = ['0']
                with self.assertRaises(Diagnostic):
                    verify_nested(run, remote)
                items[3]['parents'] = ['2']
                bindings['3']['link_provenance'] = []
                write_json(store.path / 'bindings.json', bindings)
                with self.assertRaises(Diagnostic):
                    verify_nested(run, remote)

    def test_stale_write_probe_checks_bytes_and_refuses_repeat(self):
        class StaleFake:
            calls = 0
            data = b'\x00Remote binary edit\r\n\xff'
            accepts = False
            def inventory(self):
                return ({'name': 'e.bin', 'id': 'binary'},)
            def read_original(self, file_id):
                return self.data, {'id': file_id, 'version': '2'}
            def original_etag(self, file_id):
                return 'current'
            def update_original(self, file_id, data, etag):
                self.calls += 1
                if self.accepts:
                    self.data = data
                    return {}
                raise Diagnostic('remote_http', 'Google returned HTTP 412.', 'Reconcile.')
        for accepts in (False, True):
            with self.subTest(accepts=accepts), TemporaryDirectory() as directory, redirect_stdout(StringIO()):
                path = Path(directory)
                write_json(path / 'edit-original-binary.json', {'etag': 'old'})
                remote = StaleFake()
                remote.accepts = accepts
                if accepts:
                    with self.assertRaises(Diagnostic):
                        stale_original(path, remote)
                else:
                    stale_original(path, remote)
                with self.assertRaises(Diagnostic):
                    stale_original(path, remote)
                self.assertEqual(remote.calls, 1)

    def test_uncertain_comment_create_cannot_be_replayed(self):
        class CommentFake:
            calls = 0
            def inventory(self):
                return ({'name': 'c.html', 'mimeType': DOC, 'id': 'doc'},)
            def comments(self, file_id):
                return ()
            def request(self, method, url, **kwargs):
                self.calls += 1
                raise TimeoutError('uncertain comment create')
        with TemporaryDirectory() as directory:
            remote = CommentFake()
            with self.assertRaises(TimeoutError):
                add_comment(Path(directory), remote)
            with self.assertRaises(Diagnostic):
                add_comment(Path(directory), remote)
            self.assertEqual(remote.calls, 1)

    def test_original_edit_is_not_replayed(self):
        class BinaryFake:
            data = b'\x00Local binary edit\r\n\xff'
            calls = 0
            def inventory(self):
                return ({'name': 'e.bin', 'id': 'binary'},)
            def read_original(self, file_id):
                return self.data, {}
            def original_etag(self, file_id):
                return 'etag'
            def update_original(self, file_id, data, etag):
                assert etag == 'etag'
                self.calls += 1
                self.data = data
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            remote = BinaryFake()
            edit_original(Path(directory), remote)
            edit_original(Path(directory), remote)
            self.assertEqual(remote.calls, 1)
            remote.data = b'uncertain'
            with self.assertRaises(Diagnostic):
                edit_original(Path(directory), remote)
            self.assertEqual(remote.calls, 1)

    def remote(self):
        remote = EditingFake()
        remote.create('a.md', DOC, 'source', 'operation')
        remote.bodies['id-1'] = 'First sentence.\n'
        remote.calls.clear()
        return remote

    def test_verified_edit_is_not_repeated(self):
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            remote = self.remote()
            edit_remote(Path(directory), remote)
            edit_remote(Path(directory), remote)
            self.assertEqual(remote.calls, [('edit', 'id-1')])

    def test_uncertain_edit_is_not_retried(self):
        with TemporaryDirectory() as directory, redirect_stdout(StringIO()):
            remote = self.remote()
            remote.fail = True
            with self.assertRaises(TimeoutError):
                edit_remote(Path(directory), remote)
            remote.fail = False
            with self.assertRaises(Diagnostic):
                edit_remote(Path(directory), remote)
            self.assertEqual(remote.calls, [('edit', 'id-1')])

    def test_uncertain_nested_move_is_not_replayed(self):
        from live_integration import move_nested
        from test_document_model import observation
        from copy import deepcopy
        class MovingFake:
            calls = 0
            def inventory(self):
                return ({'id': 'doc', 'name': 'g.md', 'mimeType': DOC},
                        {'id': 'parent', 'name': 'level1'})
            def observe_document(self, file_id):
                value = observation()
                value.metadata['appProperties'] = {'source': 'source'}
                return value
            def metadata_guard(self, file_id):
                return deepcopy(self.observe_document(file_id).metadata), 'etag'
            def update_layout(self, *args, **kwargs):
                self.calls += 1
                raise TimeoutError('uncertain move')
        with TemporaryDirectory() as directory:
            remote = MovingFake()
            with self.assertRaises(TimeoutError):
                move_nested(Path(directory), remote)
            with self.assertRaises(Diagnostic):
                move_nested(Path(directory), remote)
            self.assertEqual(remote.calls, 1)
