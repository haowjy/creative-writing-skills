from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from drive_sync.index import Diagnostic
from drive_sync.planner import Authorization, Baseline, LocalSnapshot, RemoteSnapshot, SyncPlan, classify
from drive_sync.state import StateStore, read_json

ID = '590b7d30-bc08-45e3-aee3-f6bbfdac6342'


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.local = LocalSnapshot('s', 'a.md', 'local-base', 'render-base', 'google-doc')
        self.remote = RemoteSnapshot('r', 'remote-base', 'layout', 'rev1')
        self.base = Baseline(self.local, self.remote)

    def test_change_matrix(self):
        for lc, rc, expected in [(False, False, 'noop'), (True, False, 'push'), (False, True, 'pull'), (True, True, 'conflict')]:
            local = replace(self.local, content_hash='changed') if lc else self.local
            remote = replace(self.remote, content_hash='changed') if rc else self.remote
            self.assertEqual(classify('s', local, remote, self.base).direction, expected)

    def test_creation_requires_ownership_observation(self):
        self.assertEqual(classify('s', self.local, None, None).direction, 'conflict')
        self.assertEqual(classify('s', self.local, None, None, ownership_checked=True).direction, 'create')
        self.assertEqual(classify('s', self.local, self.remote, None).reason, 'missing_baseline')

    def test_missing_and_pending(self):
        for local, remote in [(None, self.remote), (self.local, None)]:
            self.assertEqual(classify('s', local, remote, self.base).direction, 'conflict')
        self.assertEqual(classify('s', self.local, self.remote, self.base, pending=True).direction, 'conflict')

    def test_annotations_and_extra_tabs(self):
        local = replace(self.local, rendering_hash='new-renderer')
        for remote in [replace(self.remote, annotations_readable=False), replace(self.remote, comments=True), replace(self.remote, suggestions=True), replace(self.remote, content_tabs=2)]:
            self.assertEqual(classify('s', local, remote, self.base).direction, 'conflict')

    def test_moved_and_storage(self):
        for local in [replace(self.local, path='b.md'), replace(self.local, storage='original')]:
            self.assertEqual(classify('s', local, self.remote, self.base).direction, 'conflict')
        self.assertEqual(classify('s', self.local, replace(self.remote, structure_hash='moved'), self.base).direction, 'conflict')

    def test_revision_only_is_not_content_change(self):
        self.assertEqual(classify('s', self.local, replace(self.remote, revision='rev2'), self.base).direction, 'noop')

    def test_authorization_is_bound_to_plan_and_scope(self):
        op = classify('s', replace(self.local, content_hash='new'), self.remote, self.base)
        plan = SyncPlan(ID, 'index-hash', (op,))
        auth = Authorization(plan.digest, ID, frozenset({'s'}), frozenset({'push'}))
        self.assertTrue(auth.permits(plan, op))
        self.assertFalse(auth.permits(replace(plan, index_digest='changed'), op))
        self.assertFalse(replace(auth, directions=frozenset({'pull'})).permits(plan, op))


class StateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.store = StateStore(self.home / 'state', ID)

    def test_private_blob_roundtrip_and_corruption(self):
        key = self.store.save_blob(b'private source')
        self.assertEqual(self.store.load_blob(key), b'private source')
        self.assertEqual((self.store.blobs / key).stat().st_mode & 0o777, 0o600)
        (self.store.blobs / key).write_bytes(b'changed')
        with self.assertRaises(Diagnostic):
            self.store.load_blob(key)

    def test_claims_isolate_indexes(self):
        self.store.claim((self.home / 'project',))
        other = StateStore(self.home / 'state', '690b7d30-bc08-45e3-aee3-f6bbfdac6342')
        with self.assertRaises(Diagnostic):
            other.claim((self.home / 'project' / 'file.md',))
        other.claim((self.home / 'different',))

    def test_unverified_does_not_advance_baseline(self):
        intent = self.store.begin('source', 'push', 'old', 'new', 'remote')
        with self.assertRaises(Diagnostic):
            self.store.verify(intent, 'mixed', {})
        self.assertFalse((self.store.path / 'bindings.json').exists())
        with self.assertRaises(Diagnostic):
            self.store.begin('source', 'push', 'old', 'new', 'remote')
        self.store.verify(intent, 'new', {'remote': 'remote'})
        self.assertEqual(self.store.pending(), ())

    def test_crash_after_binding_before_journal_has_recovery_marker(self):
        import drive_sync.state as state
        intent = self.store.begin('source', 'push', 'old', 'new', 'remote')
        original = state.write_json
        def fail_journal(path, value):
            if path.parent == self.store.journals:
                raise OSError('simulated crash')
            original(path, value)
        with patch.object(state, 'write_json', side_effect=fail_journal), self.assertRaises(OSError):
            self.store.verify(intent, 'new', {'remote': 'remote'})
        self.assertEqual(len(self.store.pending()), 1)
        self.assertEqual(read_json(self.store.path / 'bindings.json')['source']['verified_operation'], intent.id)
        self.store.verify(intent, 'new', {'remote': 'remote'})
        self.assertEqual(self.store.pending(), ())

    def test_symlink_state_rejected(self):
        (self.home / 'alias').symlink_to(self.home / 'state')
        with self.assertRaises(Diagnostic):
            StateStore(self.home / 'alias', ID)

    def test_account_binding_is_stable_and_legacy_state_blocks(self):
        identity = {'account':'account', 'client':'client'}
        self.store.bind_account(identity)
        self.store.bind_account(identity)
        with self.assertRaises(Diagnostic):
            self.store.bind_account({'account':'other', 'client':'client'})
        other = StateStore(self.home / 'other-state', ID)
        other.begin('source','create',None,'desired')
        with self.assertRaises(Diagnostic):
            other.bind_account(identity)

    def test_journal_malformed_status_blocks_recovery(self):
        from drive_sync.state import write_json
        intent=self.store.begin('source','create',None,'desired')
        path=self.store.journals/(intent.id+'.json')
        value=read_json(path)
        value['status']='unknown'
        write_json(path,value)
        with self.assertRaises(Diagnostic) as caught:
            self.store.pending()
        self.assertEqual(caught.exception.code,'corrupt_journal')

    def test_hardlink_claim_across_indexes_is_rejected(self):
        import os
        one=self.home/'one.md'
        two=self.home/'two.md'
        one.write_text('content')
        os.link(one,two)
        self.store.claim((one,))
        other=StateStore(self.home/'state','690b7d30-bc08-45e3-aee3-f6bbfdac6342')
        with self.assertRaises(Diagnostic):
            other.claim((two,))

    def test_interrupted_record_transition_rolls_forward(self):
        from drive_sync.state import write_json
        write_json(self.store.path/'identities.json',{'old':'id'})
        write_json(self.store.path/'bindings.json',{'id':{'old':True}})
        write_json(self.store.path/'record-transition.json',{
            'identities.json':{'before':{'old':'id'},'after':{'new':'id'}},
            'bindings.json':{'before':{'id':{'old':True}},'after':{'id':{'new':True}}}})
        write_json(self.store.path/'identities.json',{'new':'id'})
        with self.store.lock():
            self.assertEqual(read_json(self.store.path/'bindings.json'),{'id':{'new':True}})
        self.assertFalse((self.store.path/'record-transition.json').exists())
