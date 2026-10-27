import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from drive_sync.initialization import initialization_plan
from drive_sync.index import Source,parse_index
from drive_sync.layout import plan_layout
from drive_sync.state import StateStore
from test_index import fixture
from test_sync_plan import Inventory


class InitializationTests(unittest.TestCase):
    def test_cyclic_links_do_not_prevent_identity_plan(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)
            (path/'a.md').write_text('[B](b.md)')
            (path/'b.md').write_text('[A](a.md)')
            sources=tuple(Source('notes',name,path/name,'markdown','google-doc') for name in ('a.md','b.md'))
            index=parse_index(fixture())
            layout=plan_layout(index,sources,{})
            plan=initialization_plan('index',layout,sources,StateStore(path/'state',index.id),Inventory())
            self.assertEqual([o.reason for o in plan.operations],['initialize_identity']*2)
            self.assertEqual([o.direction for o in plan.operations],['create']*2)

    def test_cyclic_initialize_populate_then_noop(self):
        from drive_sync.application import initialize_documents,preview_sync,combined_plan,apply_reviewed
        from drive_sync.planner import Authorization
        from drive_sync.storage import commit,Draft
        from drive_sync.state import read_json
        from fake_google import FakeGoogle
        with TemporaryDirectory() as directory:
            path=Path(directory)
            (path/'notes').mkdir()
            (path/'notes/a.md').write_text('[B](b.md)\n')
            (path/'notes/b.md').write_text('[A](a.md)\n')
            index=path/'index.yaml'
            commit(index,Draft(fixture()),None)
            remote=FakeGoogle()
            initial=initialize_documents(index,remote,home=path/'state')
            auth=Authorization(initial.digest,initial.index_id,frozenset(o.source_id for o in initial.operations),frozenset(['create']))
            result=initialize_documents(index,remote,auth,home=path/'state')
            self.assertEqual([f.status for f in result.files],['verified']*3)
            bindings=read_json(path/'state'/initial.index_id/'bindings.json')
            self.assertEqual(sum(bool(b.get('incomplete')) for b in bindings.values()),2)
            content=combined_plan(preview_sync(index,remote,home=path/'state'))
            self.assertEqual([o.direction for o in content.operations],['noop','push','push'])
            auth=Authorization(content.digest,content.index_id,frozenset(o.source_id for o in content.operations),frozenset(['push']))
            result=apply_reviewed(index,remote,auth,home=path/'state')
            self.assertEqual([f.status for f in result.files],['noop','verified','verified'])
            rerun=combined_plan(preview_sync(index,remote,home=path/'state'))
            self.assertEqual([o.direction for o in rerun.operations],['noop']*3)
            self.assertEqual(len(remote.files),3)

    def test_folder_only_does_not_create_source_docs(self):
        from drive_sync.application import initialize_folders
        from drive_sync.planner import Authorization
        from drive_sync.storage import commit,Draft
        from fake_google import FakeGoogle
        with TemporaryDirectory() as directory:
            path=Path(directory)
            (path/'notes/nested').mkdir(parents=True)
            (path/'notes/nested/a.md').write_text('text')
            index=path/'index.yaml'
            commit(index,Draft(fixture()),None)
            remote=FakeGoogle()
            plan=initialize_folders(index,remote,home=path/'state')
            auth=Authorization(plan.digest,plan.index_id,frozenset(o.source_id for o in plan.operations),frozenset(['create']))
            result=initialize_folders(index,remote,auth,home=path/'state')
            self.assertEqual(len(result.files),2)
            self.assertTrue(all(m['mimeType']=='application/vnd.google-apps.folder' for m in remote.files.values()))
