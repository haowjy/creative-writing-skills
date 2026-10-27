from dataclasses import replace
import unittest
from drive_sync.planner import LocalSnapshot, RemoteSnapshot, Baseline, SyncPlan, classify
from drive_sync.resolution import resolution_plan
from drive_sync.index import Diagnostic


class ResolutionTests(unittest.TestCase):
    def plan(self):
        local=LocalSnapshot('source','a.txt','base','base','original')
        remote=RemoteSnapshot('remote','base','layout','revision')
        op=classify('source',replace(local,content_hash='local'),replace(remote,content_hash='remote'),Baseline(local,remote))
        return SyncPlan('index','digest',(op,))
    def test_choices_change_digest_and_direction_without_changing_baseline(self):
        plan=self.plan()
        for choice,direction in [('keep-local','push'),('accept-remote','pull')]:
            resolved=resolution_plan(plan,'source',choice)
            self.assertEqual(resolved.operations[0].direction,direction)
            self.assertEqual(resolved.operations[0].baseline,plan.operations[0].baseline)
            self.assertNotEqual(resolved.digest,plan.digest)
    def test_does_not_bypass_missing_state_or_annotations(self):
        plan=self.plan()
        with self.assertRaises(Diagnostic):
            resolution_plan(replace(plan,operations=(replace(plan.operations[0],reason='missing_baseline'),)),'source','keep-local')
        with self.assertRaises(Diagnostic):
            resolution_plan(replace(plan,operations=(replace(plan.operations[0],remote=replace(plan.operations[0].remote,comments=True)),)),'source','keep-local')

    def test_storage_replacement_is_explicit_create_not_overwrite(self):
        plan=self.plan()
        old=plan.operations[0]
        changed=replace(old,reason='storage_changed',local=replace(old.local,storage='google-doc'))
        resolved=resolution_plan(replace(plan,operations=(changed,)),'source','replace-storage')
        self.assertEqual(resolved.operations[0].direction,'create')
        self.assertEqual(resolved.operations[0].remote,changed.remote)
        self.assertEqual(resolved.operations[0].reason,'reviewed_replace_storage')
