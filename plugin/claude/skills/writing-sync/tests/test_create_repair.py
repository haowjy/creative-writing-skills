from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from copy import deepcopy
from drive_sync.application import preview_sync, combined_plan, apply_reviewed, recover_sync
from drive_sync.create_repair import repair_created_layout, repair_created_content
from drive_sync.storage import Draft, commit
from drive_sync.index import Diagnostic
from drive_sync.google import DOC
from drive_sync.import_payload import import_html
from drive_sync.conversion import render
from fake_google import FakeGoogle
from live_integration import authorize
from test_index import fixture


class ImportFake(FakeGoogle):
    lost = False
    applied = True
    def create(self, name, mime, source_id, operation_id, parent=None, data=None, import_mime=None):
        super().create(name, mime, source_id, operation_id, parent=parent)
        file_id = self.calls[-1][1]
        if data is not None:
            assert mime == DOC and data == import_html(render(b'Hello\n', 'text'))
            self.bodies[file_id] = 'Hello\n'
            self.files[file_id]['name'] = 'stripped'
    def metadata_guard(self, file_id):
        return self.metadata(file_id), self.files[file_id]['version']
    def update_layout(self, file_id, *, name, parent, before, etag):
        assert before == self.metadata(file_id) and etag == self.files[file_id]['version']
        self.calls.append(('layout', file_id))
        if self.applied:
            self.files[file_id].update(name=name, parents=[parent], version=str(int(etag) + 1))
        if self.lost:
            raise TimeoutError('lost response')


class RepairTests(TestCase):
    def test_repair_cancellation_before_write_emits_progress_without_attempt(self):
        import threading
        for kind, service in (('layout', repair_created_layout), ('content', repair_created_content)):
            with self.subTest(kind=kind), TemporaryDirectory() as directory:
                root = Path(directory)
                index, remote, operation = self.fixture(root)
                if kind == 'content':
                    file_id = next(k for k, v in remote.files.items() if v['name'] == 'stripped')
                    remote.files[file_id]['name'] = 'a.txt'
                    remote.bodies[file_id] = 'Hello'
                events = []
                plan = service(index, remote, operation, home=root / 'state', progress=events.append)
                self.assertEqual(events, [])
                remote.calls.clear()
                token = threading.Event()
                token.set()
                result = service(index, remote, operation, plan.digest, home=root / 'state',
                                 cancellation=token, progress=events.append)
                self.assertTrue(result.cancelled)
                self.assertEqual(events, list(result.files))
                self.assertEqual(result.files[0].reason, 'repair_cancelled')
                self.assertEqual(remote.calls, [])
                self.assertEqual(list((root / 'state').rglob(kind + '.json')), [])
                token.clear()
                result = service(index, remote, operation, plan.digest, home=root / 'state', cancellation=token)
                self.assertEqual(result.files[0].status, 'verified')

    def test_cancellation_during_write_still_reconciles_and_reports(self):
        import threading
        for kind, service in (('layout', repair_created_layout), ('content', repair_created_content)):
            with self.subTest(kind=kind), TemporaryDirectory() as directory:
                root = Path(directory)
                index, remote, operation = self.fixture(root)
                if kind == 'content':
                    file_id = next(k for k, v in remote.files.items() if v['name'] == 'stripped')
                    remote.files[file_id]['name'] = 'a.txt'
                    remote.bodies[file_id] = 'Hello'
                plan = service(index, remote, operation, home=root / 'state')
                token = threading.Event()
                method = 'update_layout' if kind == 'layout' else 'update_document'
                update = getattr(remote, method)
                def interrupted(*args, **kwargs):
                    value = update(*args, **kwargs)
                    token.set()
                    return value
                setattr(remote, method, interrupted)
                events = []
                result = service(index, remote, operation, plan.digest, home=root / 'state',
                                 cancellation=token, progress=events.append)
                self.assertTrue(result.cancelled)
                self.assertEqual(result.files[0].status, 'verified')
                self.assertEqual(events, list(result.files))

    def test_content_repair_and_lost_response_preserve_evidence(self):
        import json
        for applied in (True, False):
            with self.subTest(applied=applied), TemporaryDirectory() as directory:
                root = Path(directory)
                index, remote, operation = self.fixture(root)
                file_id = next(k for k, v in remote.files.items() if v['name'] == 'stripped')
                remote.files[file_id]['name'] = 'a.txt'
                remote.bodies[file_id] = 'Hello'  # Imported source LF was lost.
                plan = repair_created_content(index, remote, operation, home=root / 'state')
                self.assertEqual(plan.before_text, 'Hello')
                self.assertEqual(plan.batch['writeControl']['requiredRevisionId'], remote.files[file_id]['version'])
                remote.calls.clear()
                update = remote.update_document
                def lost(observed, batch):
                    if applied:
                        update(observed, batch)
                    else:
                        remote.calls.append(('update', file_id))
                    raise TimeoutError('uncertain content response')
                remote.update_document = lost
                result = repair_created_content(index, remote, operation, plan.digest, home=root / 'state')
                self.assertEqual(result.files[0].status, 'verified' if applied else 'pending')
                record = json.loads(next((root / 'state').rglob('content.json')).read_text())
                self.assertEqual(record['plan']['before_text'], 'Hello')
                self.assertIn('observed_before', record)
                calls = list(remote.calls)
                with self.assertRaises(Diagnostic):
                    repair_created_content(index, remote, operation, plan.digest, home=root / 'state')
                self.assertEqual(remote.calls, calls)
                self.assertEqual((root / 'notes/a.txt').read_bytes(), b'Hello\n')

    def test_content_repair_requires_new_review_after_remote_edit(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index, remote, operation = self.fixture(root)
            file_id = next(k for k, v in remote.files.items() if v['name'] == 'stripped')
            remote.bodies[file_id] = 'Hello'
            plan = repair_created_content(index, remote, operation, home=root / 'state')
            remote.bodies[file_id] = 'Another remote edit'
            remote.calls.clear()
            with self.assertRaises(Diagnostic) as caught:
                repair_created_content(index, remote, operation, plan.digest, home=root / 'state')
            self.assertEqual(caught.exception.code, 'stale_repair')
            self.assertEqual(remote.calls, [])

    def test_cli_preview_apply_and_missing_approval(self):
        from contextlib import nullcontext, redirect_stdout, redirect_stderr
        from io import StringIO
        from unittest.mock import patch
        from drive_sync.cli import main
        import json
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index, remote, operation = self.fixture(root)
            args = ['--index', str(index), 'state', 'repair-created-layout',
                    '--operation', operation, '--state-home', str(root / 'state')]
            with patch('drive_sync.auth.authorized_session', return_value=nullcontext(object())) as login, \
                    patch('drive_sync.google.GoogleDrive', return_value=remote):
                with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                    main(args + ['--apply'])
                login.assert_not_called()
                with redirect_stdout(StringIO()) as out:
                    self.assertEqual(main(args), 0)
                plan = json.loads(out.getvalue())
                def cancel_before_call(call):
                    import threading
                    token = threading.Event()
                    token.set()
                    return call(token)
                with patch('drive_sync.cli.cancellable', side_effect=cancel_before_call), redirect_stdout(StringIO()) as out:
                    self.assertEqual(main(args + ['--apply', '--plan-digest', plan['digest']]), 130)
                self.assertTrue(json.loads(out.getvalue())['cancelled'])
                with redirect_stdout(StringIO()) as out:
                    self.assertEqual(main(args + ['--apply', '--plan-digest', plan['digest']]), 0)
                self.assertEqual(json.loads(out.getvalue())['files'][0]['status'], 'verified')

    def test_annotations_duplicates_and_source_changes_block_repair(self):
        for change in ('comment', 'duplicate', 'source'):
            with self.subTest(change=change), TemporaryDirectory() as directory:
                root = Path(directory)
                index, remote, operation = self.fixture(root)
                plan = repair_created_layout(index, remote, operation, home=root / 'state')
                remote.calls.clear()
                if change == 'comment':
                    observe = remote.observe_document
                    from drive_sync.google import DocumentObservation
                    def commented(file_id):
                        value = observe(file_id)
                        return DocumentObservation(value.metadata, value.document, ({'id': 'comment'},))
                    remote.observe_document = commented
                elif change == 'duplicate':
                    remote.files['duplicate'] = deepcopy(remote.files[plan.remote_id])
                    remote.files['duplicate']['id'] = 'duplicate'
                else:
                    (root / 'notes/a.txt').write_bytes(b'Changed locally\n')
                with self.assertRaises(Diagnostic):
                    repair_created_layout(index, remote, operation, plan.digest, home=root / 'state')
                self.assertEqual(remote.calls, [])

    def fixture(self, root):
        (root / 'notes').mkdir()
        (root / 'notes/a.txt').write_bytes(b'Hello\n')
        index = root / 'index.yaml'
        commit(index, Draft(fixture()), None)
        remote = ImportFake()
        plan = combined_plan(preview_sync(index, remote, home=root / 'state'))
        result = apply_reviewed(index, remote, authorize(plan), home=root / 'state')
        item = result.files[-1]
        self.assertEqual(item.reason, 'remote_layout_mismatch')
        return index, remote, item.operation_id

    def test_success_and_lost_response_verify_without_recreate(self):
        for lost in (False, True):
            with self.subTest(lost=lost), TemporaryDirectory() as directory:
                root = Path(directory)
                index, remote, operation = self.fixture(root)
                plan = repair_created_layout(index, remote, operation, home=root / 'state')
                remote.calls.clear()
                remote.lost = lost
                result = repair_created_layout(index, remote, operation, plan.digest, home=root / 'state')
                self.assertEqual(result.files[0].status, 'verified')
                self.assertEqual(remote.calls, [('layout', plan.remote_id)])
                self.assertTrue(all(o.direction == 'noop' for o in combined_plan(preview_sync(index, remote, home=root / 'state')).operations))

    def test_unapplied_uncertain_write_is_not_replayed(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index, remote, operation = self.fixture(root)
            plan = repair_created_layout(index, remote, operation, home=root / 'state')
            remote.calls.clear()
            remote.applied = False
            remote.lost = True
            self.assertEqual(repair_created_layout(index, remote, operation, plan.digest, home=root / 'state').files[0].status, 'pending')
            with self.assertRaises(Diagnostic) as caught:
                repair_created_layout(index, remote, operation, plan.digest, home=root / 'state')
            self.assertEqual(caught.exception.code, 'repair_already_attempted')
            self.assertEqual(remote.calls, [('layout', plan.remote_id)])
            self.assertEqual(recover_sync(index, remote, home=root / 'state').files[0].status, 'pending')

    def test_changed_content_or_stale_digest_never_writes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index, remote, operation = self.fixture(root)
            plan = repair_created_layout(index, remote, operation, home=root / 'state')
            remote.calls.clear()
            with self.assertRaises(Diagnostic):
                repair_created_layout(index, remote, operation, 'wrong-digest', home=root / 'state')
            remote.bodies[plan.remote_id] = 'Unexpected edit\n'
            with self.assertRaises(Diagnostic) as caught:
                repair_created_layout(index, remote, operation, plan.digest, home=root / 'state')
            self.assertEqual(caught.exception.code, 'repair_content_mismatch')
            self.assertEqual(remote.calls, [])
