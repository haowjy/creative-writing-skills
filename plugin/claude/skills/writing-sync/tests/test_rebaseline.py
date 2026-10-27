from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from drive_sync.rebaseline import plan_rebaseline,apply_rebaseline
from drive_sync.state import StateStore,write_json,read_json
from drive_sync.storage import commit,Draft
from test_index import fixture
from drive_sync.index import Diagnostic


class RebaselineTests(unittest.TestCase):
    def test_agreeing_originals_repair_without_remote_writes(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)
            (path/'notes').mkdir()
            source=path/'notes/a.txt'
            source.write_bytes(b'same')
            raw=fixture()
            raw['policy']['default_storage']='original'
            index=path/'index.yaml'
            loaded=commit(index,Draft(raw),None)
            store=StateStore(path/'state',loaded.model.id)
            identity={'account':'fake','client':'fake'}
            store.bind_account(identity)
            sid='source'
            write_json(store.path/'bindings.json',{sid:dict(kind='file',path=str(source),storage='original',remote_id='remote',name='a.txt',parent='folder')})
            class Remote:
                def __init__(self):self.identity=identity
                def metadata(self,_):return dict(id='remote',name='a.txt',parents=['folder'],mimeType='text/plain',version='1',appProperties={'source':sid})
                def read_original(self,_):return b'same',self.metadata(_)
            remote=Remote()
            plan=plan_rebaseline(index,store,remote,sid)
            self.assertTrue(apply_rebaseline(index,store,remote,sid,plan.digest)['rebaselined'])
            self.assertIn('baseline',read_json(store.path/'bindings.json')[sid])
            source.write_bytes(b'different')
            with self.assertRaises(Diagnostic):plan_rebaseline(index,store,remote,sid)

    def test_raced_comparison_cannot_repair_binding(self):
        for race in ('source', 'remote', 'index'):
            with self.subTest(race=race), TemporaryDirectory() as directory:
                path = Path(directory)
                (path / 'notes').mkdir()
                source = path / 'notes/a.txt'
                source.write_bytes(b'same')
                raw = fixture()
                raw['policy']['default_storage'] = 'original'
                index = path / 'index.yaml'
                loaded = commit(index, Draft(raw), None)
                store = StateStore(path / 'state', loaded.model.id)
                identity = {'account': 'fake', 'client': 'fake'}
                store.bind_account(identity)
                sid = 'source'
                write_json(store.path / 'bindings.json', {sid: dict(kind='file', path=str(source),
                    storage='original', remote_id='remote', name='a.txt', parent='folder')})
                class Remote:
                    changed = False
                    armed = False
                    identity = {'account': 'fake', 'client': 'fake'}
                    def metadata(self, file_id):
                        return dict(id=file_id, name='moved.txt' if self.changed else 'a.txt',
                            parents=['folder'], mimeType='text/plain', version='2' if self.changed else '1',
                            appProperties={'source': sid})
                    def read_original(self, file_id):
                        if self.armed:
                            self.armed = False
                            if race == 'source':
                                source.write_bytes(b'concurrent')
                            elif race == 'remote':
                                self.changed = True
                            else:
                                index.write_bytes(index.read_bytes() + b'\n# concurrent edit\n')
                        return b'same', self.metadata(file_id)
                remote = Remote()
                plan = plan_rebaseline(index, store, remote, sid)
                before = (store.path / 'bindings.json').read_bytes()
                remote.armed = True
                with self.assertRaises(Diagnostic) as caught:
                    apply_rebaseline(index, store, remote, sid, plan.digest)
                self.assertEqual(caught.exception.code, 'rebaseline_' + race + '_race')
                self.assertEqual((store.path / 'bindings.json').read_bytes(), before)
                self.assertFalse((store.path / 'record-transition.json').exists())
