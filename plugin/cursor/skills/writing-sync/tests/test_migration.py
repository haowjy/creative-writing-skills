from dataclasses import asdict, replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from drive_sync.index import Source, parse_index
from drive_sync.layout import plan_layout
from drive_sync.planner import LocalSnapshot, RemoteSnapshot, Baseline, Operation, SyncPlan, Authorization
from drive_sync.state import StateStore,write_json,read_json
from drive_sync.storage import digest
from drive_sync.original_effects import OriginalEffects
from drive_sync.executor import apply_sync
from drive_sync.sync_plan import file_plan
from test_index import fixture
from test_original_effects import Remote


class MigrationTests(unittest.TestCase):
    def test_replacement_retains_old_binding_and_object(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)
            source_path=path/'a.txt'
            source_path.write_bytes(b'local')
            index=parse_index(fixture())
            sources=(Source('notes','a.txt',source_path,'text','original'),)
            layout=plan_layout(index,sources,{})
            sid=layout.files[0].source_id
            store=StateStore(path/'state',index.id)
            remote=Remote()
            remote.files['old-doc']=dict(id='old-doc',name='a.txt',mimeType='application/vnd.google-apps.document',parents=['folder'],appProperties={'source':sid,'operation':'old'})
            old_remote=RemoteSnapshot('old-doc','old-hash','old-structure','old-rev')
            local=LocalSnapshot(sid,'notes/a.txt',digest(b'local'),digest(b'local'),'original')
            base=Baseline(replace(local,storage='google-doc'),old_remote)
            write_json(store.path/'bindings.json',{layout.folders[0].id:{'remote_id':'folder'},sid:dict(kind='file',storage='google-doc',remote_id='old-doc',baseline=asdict(base),source_blob=store.save_blob(b'local'))})
            operation=Operation(sid,'create','reviewed_replace_storage','',local,old_remote,base)
            plan=SyncPlan(index.id,'index',(operation,))
            class Effects(OriginalEffects):
                def refresh_plan(self, incoming):
                    self.expected_digest='index'
                    return plan
            effects=Effects(layout,sources,store,remote,lambda:'index')
            import drive_sync.original_effects as module
            original_observe=module.observe_file
            def observed(adapter,file_id,storage):
                return old_remote if file_id=='old-doc' else original_observe(adapter,file_id,storage)
            with patch.object(module,'observe_file',side_effect=observed):
                result=apply_sync(plan,Authorization(plan.digest,index.id,frozenset([sid]),frozenset(['create'])),store,effects)
            self.assertEqual(result.files[0].status,'verified')
            self.assertIn('old-doc',remote.files)
            binding=read_json(store.path/'bindings.json')[sid]
            self.assertEqual(binding['retained_bindings'][0]['remote_id'],'old-doc')
            self.assertEqual(binding['remote_id'],'remote')
            self.assertEqual(file_plan('index',layout,sources,store,remote).operations[0].direction,'noop')
