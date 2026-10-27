from pathlib import Path
import tempfile
import unittest
from dataclasses import asdict
from drive_sync.index import Source, parse_index, Diagnostic
from drive_sync.layout import plan_layout
from drive_sync.planner import Baseline, LocalSnapshot, RemoteSnapshot
from drive_sync.state import StateStore,write_json,read_json
from drive_sync.storage import commit,Draft,digest
from drive_sync.rebind import plan_rebind,apply_rebind
from test_index import fixture


class RebindTests(unittest.TestCase):
    def test_direct_service_rejects_wrong_account_before_source_or_inventory_reads(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / 'index.yaml'
            loaded = commit(index, Draft(fixture()), None)
            store = StateStore(root / 'state', loaded.model.id)
            original = {'account': 'original', 'client': 'client'}
            store.bind_account(original)
            for identity in (None, {'account': 'other', 'client': 'client'},
                             {'account': 'original', 'client': 'other'}):
                remote = SimpleNamespace(identity=identity, index_id=loaded.model.id)
                with self.subTest(identity=identity), patch('drive_sync.rebind.resolve', side_effect=AssertionError('Source access before account validation')):
                    with self.assertRaises(Diagnostic) as caught:
                        plan_rebind(index, store, 'source', 'notes', 'new.md', remote)
                    self.assertIn(caught.exception.code, ('unverified_account', 'wrong_account'))
                    with self.assertRaises(Diagnostic):
                        apply_rebind(SimpleNamespace(source_id='source'), index, store,
                                     'reviewed-digest', 'notes', 'new.md', remote)
                self.assertEqual(read_json(store.path / 'account.json'), original)
            remote = SimpleNamespace(identity=original, index_id='different-index')
            with self.assertRaises(Diagnostic) as caught:
                plan_rebind(index, store, 'source', 'notes', 'new.md', remote)
            self.assertEqual(caught.exception.code, 'wrong_state')

    def test_cli_rebind_missing_approval_does_not_start_oauth(self):
        from drive_sync.cli import main
        from unittest.mock import patch
        from contextlib import redirect_stderr
        from io import StringIO
        with patch('drive_sync.auth.authorized_session', side_effect=AssertionError('OAuth must not start')), \
                redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            main(['--index', '/synthetic/index.yaml', 'source', 'rebind', '--source', 'source',
                  '--root', 'notes', '--path', 'new.md', '--apply'])

    def test_rebind_preserves_remote_and_baseline_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            (path/'notes').mkdir()
            old=path/'notes/a.txt'
            old.write_bytes(b'base')
            raw=fixture()
            raw['policy']['default_storage']='original'
            index=path/'index.yaml'
            loaded=commit(index,Draft(raw),None)
            source=Source('notes','a.txt',old,'text','original')
            identities={}
            layout=plan_layout(loaded.model,(source,),identities)
            sid=layout.files[0].source_id
            store=StateStore(path/'state',loaded.model.id)
            store.bind_account({'account': 'fake-account', 'client': 'fake-client'})
            base=Baseline(LocalSnapshot(sid,'notes/a.txt',digest(b'base'),digest(b'base'),'original'),RemoteSnapshot('remote','remotehash','structure','r'))
            write_json(store.path/'identities.json',identities)
            write_json(store.path/'bindings.json',{layout.folders[0].id:{'remote_id':'folder'},sid:dict(kind='file',storage='original',path=str(old),remote_id='remote',baseline=asdict(base),name='a.txt',parent='folder')})
            new = path/'notes/b.txt'
            new.write_bytes(old.read_bytes())
            before_ids = (store.path/'identities.json').read_bytes()
            before_bindings = (store.path/'bindings.json').read_bytes()
            with self.assertRaises(Diagnostic) as caught:
                plan_rebind(index,store,sid,'notes','b.txt')
            self.assertEqual(caught.exception.code, 'rebind_old_path_present')
            self.assertEqual((store.path/'identities.json').read_bytes(), before_ids)
            self.assertEqual((store.path/'bindings.json').read_bytes(), before_bindings)
            self.assertEqual(old.read_bytes(), new.read_bytes())
            new.unlink()
            old.rename(new)
            plan=plan_rebind(index,store,sid,'notes','b.txt')
            old.write_bytes(b'reappeared during review')
            with self.assertRaises(Diagnostic) as caught:
                apply_rebind(plan,index,store,plan.digest,'notes','b.txt')
            self.assertEqual(caught.exception.code, 'rebind_old_path_present')
            self.assertEqual(old.read_bytes(), b'reappeared during review')
            self.assertEqual((store.path/'identities.json').read_bytes(), before_ids)
            self.assertEqual((store.path/'bindings.json').read_bytes(), before_bindings)
            old.unlink()
            old.symlink_to(path/'missing-target')
            with self.assertRaises(Diagnostic):
                apply_rebind(plan,index,store,plan.digest,'notes','b.txt')
            old.unlink()
            result=apply_rebind(plan,index,store,plan.digest,'notes','b.txt')
            self.assertTrue(result['rebound'])
            binding=read_json(store.path/'bindings.json')[sid]
            self.assertEqual(binding['remote_id'],'remote')
            self.assertEqual(binding['baseline']['local']['content_hash'],digest(b'base'))
            self.assertTrue(binding['layout_pending'])
            self.assertEqual(read_json(store.path/'identities.json')['file:notes:b.txt'],sid)
            # A preview-allocated identity may be discarded only after checking
            # that it never acquired a binding, pending write or remote object.
            (path/'notes/b.txt').rename(path/'notes/c.txt')
            current=read_json(store.path/'identities.json')
            import uuid
            placeholder=str(uuid.uuid4())
            current['file:notes:c.txt']=placeholder
            write_json(store.path/'identities.json',current)
            class Remote:
                identity = {'account': 'fake-account', 'client': 'fake-client'}
                def inventory(self):
                    return ()
            next_plan=plan_rebind(index,store,sid,'notes','c.txt',Remote())
            apply_rebind(next_plan,index,store,next_plan.digest,'notes','c.txt',Remote())
            self.assertEqual(read_json(store.path/'identities.json')['file:notes:c.txt'],sid)
