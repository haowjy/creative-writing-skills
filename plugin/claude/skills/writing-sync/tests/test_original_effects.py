from pathlib import Path
import tempfile
import unittest
from drive_sync.index import Source, parse_index
from drive_sync.layout import plan_layout
from drive_sync.state import StateStore, write_json
from drive_sync.sync_plan import file_plan
from drive_sync.original_effects import OriginalEffects
from drive_sync.executor import apply_sync
from drive_sync.planner import Authorization
from test_index import fixture


class Remote:
    def __init__(self):
        self.identity = {'account':'synthetic-account', 'client':'synthetic-client'}
        self.files = {}
        self.data = {}
    def inventory(self, operation_id=None):
        return tuple(m for m in self.files.values() if operation_id is None or m['appProperties']['operation'] == operation_id)
    def metadata(self, file_id):
        return dict(self.files[file_id])
    def create(self, name, mime, source_id, operation_id, parent=None, data=None, import_mime=None):
        self.files['remote'] = dict(id='remote', name=name, mimeType=mime, parents=[parent], version='1',
                                    appProperties=dict(source=source_id, operation=operation_id))
        self.data['remote'] = data
    def read_original(self, file_id):
        return self.data[file_id], self.metadata(file_id)
    def original_etag(self, file_id):
        return self.files[file_id]['version']
    def update_original(self, file_id, data, etag):
        assert etag == self.files[file_id]['version']
        self.data[file_id] = data
        self.files[file_id]['version'] = str(int(etag) + 1)


class OriginalWorkflowTests(unittest.TestCase):
    def test_create_push_pull_conflict_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            source_path = path / 'a.txt'
            source_path.write_bytes(b'first')
            index = parse_index(fixture())
            sources = (Source('notes', 'a.txt', source_path, 'text', 'original'),)
            layout = plan_layout(index, sources, {})
            store = StateStore(path / 'state', index.id)
            write_json(store.path / 'bindings.json', {layout.folders[0].id: {'remote_id':'folder'}})
            remote = Remote()
            effects = OriginalEffects(layout, sources, store, remote, lambda:'index')
            def sync(expected):
                plan = file_plan('index', layout, sources, store, remote)
                self.assertEqual(plan.operations[0].direction, expected)
                auth = Authorization(plan.digest, index.id, frozenset([layout.files[0].source_id]), frozenset(['create','push','pull']))
                return apply_sync(plan, auth, store, effects)
            self.assertEqual(sync('create').files[0].status, 'verified')
            sync('noop')
            source_path.write_bytes(b'local edit')
            self.assertEqual(sync('push').files[0].status, 'verified')
            self.assertEqual(remote.data['remote'], b'local edit')
            remote.update_original('remote', b'remote edit', remote.original_etag('remote'))
            self.assertEqual(sync('pull').files[0].status, 'verified')
            self.assertEqual(source_path.read_bytes(), b'remote edit')
            sync('noop')
            source_path.write_bytes(b'local conflict')
            remote.update_original('remote', b'remote conflict', remote.original_etag('remote'))
            self.assertEqual(sync('conflict').files[0].status, 'conflict')
