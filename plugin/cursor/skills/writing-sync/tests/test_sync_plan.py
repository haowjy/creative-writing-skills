from pathlib import Path
import tempfile
import unittest
from drive_sync.index import Source, parse_index
from drive_sync.layout import plan_layout
from drive_sync.sync_plan import file_plan
from drive_sync.state import StateStore
from test_index import fixture


class Inventory:
    def __init__(self, files=()):
        self.files = files
    def inventory(self):
        return self.files


class FilePlanTests(unittest.TestCase):
    def test_new_selected_source_and_missing_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            source_path = path / 'a.md'
            source_path.write_text('Readable source.\n')
            index = parse_index(fixture())
            sources = (Source('notes', 'a.md', source_path, 'markdown', 'google-doc'),)
            layout = plan_layout(index, sources, {})
            store = StateStore(path / 'state', index.id)
            plan = file_plan('index', layout, sources, store, Inventory())
            self.assertEqual(plan.operations[0].direction, 'create')
            existing = dict(id='remote', appProperties={'source': layout.files[0].source_id})
            plan = file_plan('index', layout, sources, store, Inventory((existing,)))
            self.assertEqual(plan.operations[0].reason, 'missing_baseline')

    def test_conversion_findings_are_plan_conflicts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            source_path = path / 'a.md'
            source_path.write_text('![unsupported image](local.png)')
            index = parse_index(fixture())
            sources = (Source('notes', 'a.md', source_path, 'markdown', 'google-doc'),)
            plan = file_plan('index', plan_layout(index, sources, {}), sources,
                             StateStore(path / 'state', index.id), Inventory())
            self.assertEqual(plan.operations[0].reason, 'conversion_blocked')

    def test_storage_change_observes_existing_representation_before_conflicting(self):
        from dataclasses import asdict
        from drive_sync.planner import Baseline,LocalSnapshot,RemoteSnapshot
        from drive_sync.state import write_json
        from drive_sync.storage import digest
        from drive_sync.google import fingerprint
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            file=path/'a.txt'
            file.write_bytes(b'original')
            index=parse_index(fixture())
            sources=(Source('notes','a.txt',file,'text','google-doc'),)
            layout=plan_layout(index,sources,{})
            sid=layout.files[0].source_id
            store=StateStore(path/'state',index.id)
            metadata=dict(id='remote',name='a.txt',parents=['folder'],mimeType='text/plain',version='1',appProperties={'source':sid})
            remote_snapshot=RemoteSnapshot('remote',digest(b'original'),fingerprint(dict(name='a.txt',parents=['folder'],mime='text/plain')),'1',True,False,False,0)
            base=Baseline(LocalSnapshot(sid,'notes/a.txt',digest(b'original'),digest(b'original'),'original'),remote_snapshot)
            write_json(store.path/'bindings.json',{sid:{'baseline':asdict(base)}})
            class Remote(Inventory):
                def read_original(self, file_id):
                    return b'original',metadata
            plan=file_plan('index',layout,sources,store,Remote((metadata,)))
            self.assertEqual(plan.operations[0].reason,'storage_changed')
