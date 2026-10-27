from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest

from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
from drive_sync.batch_resume import resume_batches
from drive_sync.batch_repair import repair_batches
from drive_sync.index import Diagnostic
from drive_sync.state import StateStore, read_json
from drive_sync.storage import Draft, commit
from fake_google import FakeGoogle
from live_integration import authorize
from test_index import fixture


class BatchApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'notes').mkdir()
        self.source = self.root / 'notes/a.txt'
        self.source.write_text('Initial.\n')
        self.index = self.root / 'index.yaml'
        self.raw = fixture()
        commit(self.index, Draft(self.raw), None)
        self.remote = FakeGoogle()
        plan = initialize_documents(self.index, self.remote, home=self.root / 'state')
        initialize_documents(self.index, self.remote, authorize(plan), home=self.root / 'state')
        self.apply()
        self.remote.calls.clear()
        self.large = 'x' * 1_010_000 + '\n'
        self.source.write_text(self.large)

    def apply(self, cancellation=None):
        plan = combined_plan(preview_sync(self.index, self.remote, home=self.root / 'state'))
        return apply_reviewed(self.index, self.remote, authorize(plan), home=self.root / 'state', cancellation=cancellation)

    def test_large_push_completes_and_reruns_noop(self):
        result = self.apply()
        self.assertTrue(all(f.status in ('verified', 'noop') for f in result.files), result)
        self.assertGreater(len(self.remote.calls), 1)
        self.assertIn(self.large, self.remote.bodies.values())
        self.assertTrue(all(o.direction == 'noop' for o in combined_plan(preview_sync(self.index, self.remote, home=self.root / 'state')).operations))

    def test_cancel_then_exact_reviewed_resume(self):
        token = threading.Event()
        update = self.remote.update_document
        def update_and_cancel(observation, batch):
            response = update(observation, batch)
            token.set()
            return response
        self.remote.update_document = update_and_cancel
        result = self.apply(token)
        self.assertTrue(result.cancelled)
        self.assertEqual(len(self.remote.calls), 1)
        store = StateStore(self.root / 'state', self.raw['id'])
        intent = store.pending()[0]
        self.source.write_text('An intervening local edit.\n')
        with self.assertRaises(Diagnostic) as caught:
            resume_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        self.assertEqual(caught.exception.code, 'stale_batch_source')
        self.assertEqual(len(self.remote.calls), 1)
        self.source.write_text(self.large)
        plan = resume_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        self.assertEqual(plan.completed_batches, 1)
        with self.assertRaises(Diagnostic):
            resume_batches(self.index, self.remote, intent.id, 'wrong', home=self.root / 'state')
        self.assertEqual(len(self.remote.calls), 1)
        self.remote.update_document = update
        result = resume_batches(self.index, self.remote, intent.id, plan.digest, home=self.root / 'state')
        self.assertEqual(result.files[0].status, 'verified', result)
        self.assertEqual(store.pending(), ())
        self.assertIn(self.large, self.remote.bodies.values())

    def interrupt_second_batch(self, *, applied=False):
        update = self.remote.update_document
        attempts = []
        def uncertain(observation, batch):
            attempts.append(batch)
            if len(attempts) == 2:
                if applied:
                    update(observation, batch)
                raise TimeoutError('synthetic lost response')
            return update(observation, batch)
        self.remote.update_document = uncertain
        result = self.apply()
        self.assertTrue(any(f.status == 'pending' for f in result.files), result)
        store = StateStore(self.root / 'state', self.raw['id'])
        intent = store.pending()[0]
        path = store.journals / (intent.id + '.batches') / 'sequence.json'
        self.assertEqual(len(read_json(path)['verified']), 1)
        self.remote.update_document = update
        return store, intent, path

    def test_reviewed_unchanged_intermediate_attempt_retains_evidence_and_resumes(self):
        store, intent, path = self.interrupt_second_batch()
        before = path.read_bytes()
        writes = len(self.remote.calls)
        plan = resume_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        self.assertTrue(plan.close_unchanged_attempt)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(self.remote.calls), writes)
        with self.assertRaises(Diagnostic):
            resume_batches(self.index, self.remote, intent.id, 'wrong', home=self.root / 'state')
        self.assertEqual(path.read_bytes(), before)
        result = resume_batches(self.index, self.remote, intent.id, plan.digest, home=self.root / 'state')
        self.assertEqual(result.files[0].status, 'verified', result)
        archives = list(path.parent.glob('unchanged-*.json'))
        self.assertEqual(len(archives), 1)
        archive = read_json(archives[0])
        self.assertEqual(archive['authorized_digest'], plan.digest)
        self.assertEqual(archive['sequence']['inflight']['segment'], 1)
        self.assertIsNone(archive['sequence']['inflight']['receipt_revision'])
        self.assertEqual(archive['observation'], archive['sequence']['inflight']['before'])
        self.assertEqual(store.pending(), ())
        self.assertIn(self.large, self.remote.bodies.values())
        self.assertTrue(all(o.direction == 'noop' for o in combined_plan(
            preview_sync(self.index, self.remote, home=self.root / 'state')).operations))

    def test_applied_lost_intermediate_response_cannot_be_closed_as_unchanged(self):
        store, intent, path = self.interrupt_second_batch(applied=True)
        before = path.read_bytes()
        writes = len(self.remote.calls)
        with self.assertRaises(Diagnostic):
            resume_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(self.remote.calls), writes)
        self.assertEqual(len(store.pending()), 1)

    def test_unchanged_attempt_remote_race_invalidates_review(self):
        _, intent, path = self.interrupt_second_batch()
        plan = resume_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        self.remote.files[intent.remote_id]['version'] = 'intervening-edit'
        before = path.read_bytes()
        writes = len(self.remote.calls)
        with self.assertRaises(Diagnostic):
            resume_batches(self.index, self.remote, intent.id, plan.digest, home=self.root / 'state')
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(self.remote.calls), writes)

    def test_cancelled_resume_preserves_uncertain_attempt_and_emits_progress(self):
        _, intent, path = self.interrupt_second_batch()
        events = []
        plan = resume_batches(self.index, self.remote, intent.id, home=self.root / 'state', progress=events.append)
        self.assertEqual(events, [])
        before = path.read_bytes()
        calls = list(self.remote.calls)
        token = threading.Event()
        token.set()
        result = resume_batches(self.index, self.remote, intent.id, plan.digest,
                                home=self.root / 'state', cancellation=token, progress=events.append)
        self.assertTrue(result.cancelled)
        self.assertEqual(events, list(result.files))
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.remote.calls, calls)
        self.assertEqual(list(path.parent.glob('unchanged-*.json')), [])

    def test_reviewed_replacement_repairs_applied_lost_intermediate_batch(self):
        store, intent, original = self.interrupt_second_batch(applied=True)
        original_bytes = original.read_bytes()
        writes = len(self.remote.calls)
        plan = repair_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        self.assertNotEqual(plan.before_text, plan.desired_text)
        self.assertEqual(plan.desired_text, self.large)
        self.assertEqual(len(self.remote.calls), writes)
        with self.assertRaises(Diagnostic):
            repair_batches(self.index, self.remote, intent.id, 'wrong', home=self.root / 'state')
        self.assertEqual(len(self.remote.calls), writes)
        result = repair_batches(self.index, self.remote, intent.id, plan.digest, home=self.root / 'state')
        self.assertEqual(result.files[0].status, 'verified', result)
        self.assertEqual(original.read_bytes(), original_bytes)
        attempts = list((store.journals / (intent.id + '.batch-repairs')).glob('*.json'))
        self.assertEqual(len(attempts), 1)
        from drive_sync.google import fingerprint
        self.assertEqual(fingerprint(read_json(attempts[0])['plan']['observation']), fingerprint(plan.observation))
        self.assertEqual(store.pending(), ())
        self.assertIn(self.large, self.remote.bodies.values())
        self.assertTrue(all(o.direction == 'noop' for o in combined_plan(
            preview_sync(self.index, self.remote, home=self.root / 'state')).operations))

    def test_interrupted_repair_retains_baseline_and_requires_new_review(self):
        store, intent, _ = self.interrupt_second_batch(applied=True)
        bindings = (store.path / 'bindings.json').read_bytes()
        plan = repair_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        update = self.remote.update_document
        def lost(observation, batch):
            update(observation, batch)
            raise TimeoutError('lost repair response')
        self.remote.update_document = lost
        result = repair_batches(self.index, self.remote, intent.id, plan.digest, home=self.root / 'state')
        self.assertEqual(result.files[0].status, 'pending')
        self.assertEqual((store.path / 'bindings.json').read_bytes(), bindings)
        writes = len(self.remote.calls)
        self.remote.update_document = update
        with self.assertRaises(Diagnostic) as caught:
            repair_batches(self.index, self.remote, intent.id, plan.digest, home=self.root / 'state')
        self.assertEqual(caught.exception.code, 'stale_batch_repair')
        self.assertEqual(len(self.remote.calls), writes)
        new = repair_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        result = repair_batches(self.index, self.remote, intent.id, new.digest, home=self.root / 'state')
        self.assertEqual(result.files[0].status, 'verified', result)
        self.assertEqual(len(list((store.journals / (intent.id + '.batch-repairs')).glob('*.json'))), 2)

    def test_batch_repair_remote_race_and_annotations_block_without_writes(self):
        from dataclasses import replace
        _, intent, _ = self.interrupt_second_batch(applied=True)
        plan = repair_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        self.remote.files[intent.remote_id]['version'] = 'intervening-edit'
        writes = len(self.remote.calls)
        with self.assertRaises(Diagnostic):
            repair_batches(self.index, self.remote, intent.id, plan.digest, home=self.root / 'state')
        observe = self.remote.observe_document
        self.remote.observe_document = lambda file_id: replace(observe(file_id), comments=({'id': 'native-comment'},))
        with self.assertRaises(Diagnostic) as caught:
            repair_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        self.assertEqual(caught.exception.code, 'annotations_protected')
        self.assertEqual(len(self.remote.calls), writes)

    def test_batch_repair_cancellation_and_progress_are_service_contracts(self):
        store, intent, _ = self.interrupt_second_batch(applied=True)
        plan = repair_batches(self.index, self.remote, intent.id, home=self.root / 'state')
        token = threading.Event()
        token.set()
        events = []
        writes = len(self.remote.calls)
        result = repair_batches(self.index, self.remote, intent.id, plan.digest,
                                home=self.root / 'state', cancellation=token, progress=events.append)
        self.assertTrue(result.cancelled)
        self.assertEqual(events, list(result.files))
        self.assertEqual(len(self.remote.calls), writes)
        self.assertFalse((store.journals / (intent.id + '.batch-repairs')).exists())
        self.source.write_text('Intervening local edit.\n')
        with self.assertRaises(Diagnostic) as caught:
            repair_batches(self.index, self.remote, intent.id, plan.digest, home=self.root / 'state')
        self.assertEqual(caught.exception.code, 'stale_batch_source')
        self.assertEqual(len(self.remote.calls), writes)

    def test_batch_repair_cli_translation_and_early_approval_guard(self):
        from contextlib import nullcontext, redirect_stdout, redirect_stderr
        from io import StringIO
        from unittest.mock import patch
        import json
        from drive_sync.cli import main
        _, intent, _ = self.interrupt_second_batch(applied=True)
        args = ['--index', str(self.index), 'state', 'repair-batches', '--operation', intent.id,
                '--state-home', str(self.root / 'state')]
        with patch('drive_sync.auth.authorized_session', return_value=nullcontext(object())) as login, \
                patch('drive_sync.google.GoogleDrive', return_value=self.remote):
            with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                main(args + ['--apply'])
            login.assert_not_called()
            with redirect_stdout(StringIO()) as out:
                self.assertEqual(main(args), 0)
            plan = json.loads(out.getvalue())
            with redirect_stdout(StringIO()) as out:
                self.assertEqual(main(args + ['--apply', '--plan-digest', plan['digest']]), 0)
            self.assertEqual(json.loads(out.getvalue())['files'][0]['status'], 'verified')
