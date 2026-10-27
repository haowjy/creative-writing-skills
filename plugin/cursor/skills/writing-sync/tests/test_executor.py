from dataclasses import replace
from pathlib import Path
import tempfile
import threading
import unittest

from drive_sync.executor import Prepared, Observation, apply_sync, recover
from drive_sync.index import Diagnostic
from drive_sync.planner import LocalSnapshot, SyncPlan, Authorization, classify
from drive_sync.state import StateStore

ID = '590b7d30-bc08-45e3-aee3-f6bbfdac6342'


class FakeEffects:
    def __init__(self):
        self.objects = {}
        self.calls = 0
        self.fail_response = False
        self.read_failure = False
        self.duplicate = False
        self.stale = False

    def refresh_plan(self, plan):
        return replace(plan, index_digest='new') if self.stale else plan

    def prepare(self, operation):
        return Prepared(operation.source_id, None, 'desired', b'payload', {'source': operation.source_id})

    def guard(self, operation):
        pass

    def mutate(self, operation, prepared, intent):
        self.calls += 1
        self.objects[intent.id] = Observation(prepared.outcome_hash, {'remote_id': 'synthetic-' + intent.id})
        if self.fail_response:
            raise TimeoutError('lost response')

    def observe(self, intent, prepared):
        if self.read_failure:
            raise TimeoutError('read unavailable')
        values = (self.objects[intent.id],) if intent.id in self.objects else ()
        return values * 2 if self.duplicate else values


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = StateStore(Path(self.temp.name), ID)
        ops = tuple(classify(s, LocalSnapshot(s, s + '.md', 'hash', 'render', 'google-doc'), None, None, ownership_checked=True) for s in ('a', 'b'))
        self.plan = SyncPlan(ID, 'index', ops)
        self.auth = Authorization(self.plan.digest, ID, frozenset({'a', 'b'}), frozenset({'create'}))
        self.effects = FakeEffects()

    def test_lost_response_verified_without_retry(self):
        self.effects.fail_response = True
        result = apply_sync(self.plan, self.auth, self.store, self.effects)
        self.assertEqual([f.status for f in result.files], ['verified', 'verified'])
        self.assertEqual(self.effects.calls, 2)
        self.assertEqual(self.store.pending(), ())

    def test_prepare_diagnostic_includes_operation_context(self):
        def prepare(operation):
            raise Diagnostic('unsupported_content', 'A table cannot be represented.',
                             'Select original storage or simplify the table.',
                             destination='parent/new.md')
        self.effects.prepare = prepare
        result = apply_sync(self.plan, self.auth, self.store, self.effects)
        first = result.files[0]
        self.assertEqual(first.source, 'a.md')
        self.assertEqual(first.destination, 'parent/new.md')
        self.assertEqual(first.operation, 'create')
        self.assertEqual(first.detail, 'A table cannot be represented.')
        self.assertEqual(self.effects.calls, 0)

    def test_pending_write_keeps_safe_http_diagnostic(self):
        def mutate(operation, prepared, intent):
            raise Diagnostic('remote_http', 'Google returned HTTP 400.',
                             'Reconcile before retrying.')
        self.effects.mutate = mutate
        result = apply_sync(self.plan, self.auth, self.store, self.effects)
        self.assertTrue(all(f.status == 'pending' for f in result.files))
        self.assertEqual(result.files[0].detail, 'remote_http: Google returned HTTP 400.')
        self.assertEqual(len(self.store.pending()), 2)

    def test_recovery_retains_safe_diagnostic_and_destination(self):
        original = self.effects.prepare
        def prepare(operation):
            value = original(operation)
            return replace(value, binding={'path': operation.local.path,
                                          'name': operation.local.path, 'parent': 'folder-id'})
        def observe(intent, prepared):
            raise Diagnostic('annotations_unreadable', 'Comments could not be inspected.',
                             'Restore access, then run state recover.')
        self.effects.prepare = prepare
        self.effects.observe = observe
        apply_sync(self.plan, self.auth, self.store, self.effects)
        result = recover(self.store, self.effects)
        first = next(f for f in result.files if f.source_id == 'a')
        self.assertEqual(first.reason, 'annotations_unreadable')
        self.assertEqual(first.source, 'a.md')
        self.assertEqual(first.destination, 'folder-id/a.md')
        self.assertEqual(first.operation, 'create')
        self.assertIn('state recover', first.action)
        self.assertEqual(self.effects.calls, 2)

    def test_lost_read_recovery_never_mutates(self):
        self.effects.read_failure = True
        result = apply_sync(self.plan, self.auth, self.store, self.effects)
        self.assertEqual([f.status for f in result.files], ['pending', 'pending'])
        self.assertFalse((self.store.path / 'bindings.json').exists())
        self.effects.read_failure = False
        result = recover(self.store, self.effects)
        self.assertEqual([f.status for f in result.files], ['verified', 'verified'])
        self.assertEqual(self.effects.calls, 2)

    def test_duplicate_match_stays_pending(self):
        self.effects.duplicate = True
        result = apply_sync(self.plan, self.auth, self.store, self.effects)
        self.assertEqual([f.reason for f in result.files], ['ambiguous_identity'] * 2)
        apply_sync(self.plan, self.auth, self.store, self.effects)
        self.assertEqual(self.effects.calls, 2)

    def test_stale_and_unauthorized_do_not_write(self):
        self.effects.stale = True
        with self.assertRaises(Diagnostic):
            apply_sync(self.plan, self.auth, self.store, self.effects)
        self.effects.stale = False
        with self.assertRaises(Diagnostic):
            apply_sync(self.plan, replace(self.auth, plan_digest='other'), self.store, self.effects)
        self.assertEqual(self.effects.calls, 0)

    def test_cancellation_keeps_completed_file_verified(self):
        cancellation = threading.Event()
        result = apply_sync(self.plan, self.auth, self.store, self.effects,
                            cancellation=cancellation, progress=lambda _: cancellation.set())
        self.assertTrue(result.cancelled)
        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.files[0].status, 'verified')

    def test_missing_preparation_does_not_retry(self):
        self.store.begin('a', 'create', None, 'desired')
        result = recover(self.store, self.effects)
        self.assertEqual(result.files[0].reason, 'missing_preparation')
        self.assertEqual(self.effects.calls, 0)

    def test_cancellation_during_write_still_reconciles(self):
        cancellation=threading.Event()
        original=self.effects.mutate
        def mutate(operation,prepared,intent):
            original(operation,prepared,intent)
            cancellation.set()
        self.effects.mutate=mutate
        result=apply_sync(self.plan,self.auth,self.store,self.effects,cancellation=cancellation)
        self.assertTrue(result.cancelled)
        self.assertEqual([f.status for f in result.files],['verified'])
        self.assertEqual(self.store.pending(),())
