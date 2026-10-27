from pathlib import Path
import tempfile
import unittest
from drive_sync.application import preview_sync, combined_plan, apply_reviewed
from drive_sync.storage import commit, Draft
from drive_sync.planner import Authorization
from test_index import fixture
from test_original_effects import Remote


class ApplicationTests(unittest.TestCase):
    def test_combined_nested_original_workflow(self):
        class FullRemote(Remote):
            def metadata_guard(self,file_id):
                return self.metadata(file_id), self.files[file_id]['version']
            def update_layout(self,file_id,*,name,parent,before,etag):
                assert self.files[file_id]['version']==etag
                self.files[file_id].update(name=name,parents=[parent],version=str(int(etag)+1))
            def create(self, name, mime, source_id, operation_id, parent=None, data=None, import_mime=None):
                file_id = str(len(self.files) + 1)
                self.files[file_id] = dict(id=file_id, name=name, mimeType=mime, parents=[parent] if parent else ['drive-root'], version='1',
                    appProperties=dict(source=source_id, operation=operation_id))
                self.data[file_id] = data
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path/'notes'/'nested').mkdir(parents=True)
            (path/'notes'/'nested'/'a.txt').write_bytes(b'bytes')
            raw = fixture()
            raw['policy']['default_storage'] = 'original'
            index = path/'index.yaml'
            commit(index, Draft(raw), None)
            remote = FullRemote()
            preview = preview_sync(index, remote, home=path/'state')
            plan = combined_plan(preview)
            self.assertEqual([o.direction for o in plan.operations], ['create']*3)
            authorization = Authorization(plan.digest,plan.index_id,frozenset(o.source_id for o in plan.operations),frozenset(['create','push','pull']))
            result = apply_reviewed(index,remote,authorization,home=path/'state')
            self.assertEqual([f.status for f in result.files], ['verified']*3)
            self.assertEqual([o.direction for o in combined_plan(preview_sync(index,remote,home=path/'state')).operations], ['noop']*3)
            # Explicit keep-local resolves only the selected content conflict.
            from drive_sync.application import resolve_reviewed
            file_id = next(k for k,v in remote.files.items() if v['name']=='a.txt')
            (path/'notes'/'nested'/'a.txt').write_bytes(b'local conflict')
            remote.update_original(file_id,b'remote conflict',remote.original_etag(file_id))
            source_id = plan.operations[-1].source_id
            resolution = resolve_reviewed(index,remote,source_id,'keep-local',home=path/'state')
            auth = Authorization(resolution.digest,resolution.index_id,frozenset([source_id]),frozenset(['push']))
            result = resolve_reviewed(index,remote,source_id,'keep-local',auth,home=path/'state')
            self.assertEqual(result.files[0].status,'verified')
            self.assertEqual(remote.data[file_id],b'local conflict')
            remote.files[file_id]['name']='unexpected-name'
            resolution=resolve_reviewed(index,remote,source_id,'restore-layout',home=path/'state')
            auth=Authorization(resolution.digest,resolution.index_id,frozenset([source_id]),frozenset(['push']))
            result=resolve_reviewed(index,remote,source_id,'restore-layout',auth,home=path/'state')
            self.assertEqual(result.files[0].status,'verified')
            self.assertEqual(remote.files[file_id]['name'],'a.txt')
            self.assertEqual(remote.data[file_id],b'local conflict')
            folder_id=next(k for k,v in remote.files.items() if v['name']=='nested')
            folder_source=remote.files[folder_id]['appProperties']['source']
            remote.files[folder_id]['name']='renamed-folder'
            resolution=resolve_reviewed(index,remote,folder_source,'restore-layout',home=path/'state')
            auth=Authorization(resolution.digest,resolution.index_id,frozenset([folder_source]),frozenset(['push']))
            result=resolve_reviewed(index,remote,folder_source,'restore-layout',auth,home=path/'state')
            self.assertEqual(result.files[0].status,'verified')
            self.assertEqual(remote.files[folder_id]['name'],'nested')
            # Losing the entire state namespace must not allocate new UUIDs and
            # duplicate every remote object on the next preview.
            import shutil
            from drive_sync.index import Diagnostic
            shutil.rmtree(path/'state'/plan.index_id)
            with self.assertRaises(Diagnostic) as caught:
                preview_sync(index,remote,home=path/'state')
            self.assertEqual(caught.exception.code,'missing_state')
