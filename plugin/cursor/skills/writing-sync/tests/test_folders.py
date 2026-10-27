from pathlib import Path
import tempfile
import unittest
from drive_sync.index import Source, parse_index
from drive_sync.layout import plan_layout
from drive_sync.folders import folder_plan, FolderEffects
from drive_sync.executor import apply_sync, recover
from drive_sync.planner import Authorization
from drive_sync.state import StateStore
from test_index import fixture


class Remote:
    def __init__(self):
        self.files = []
        self.creates = 0

    def inventory(self, operation_id=None):
        return tuple(f for f in self.files if operation_id is None or f['appProperties']['operation'] == operation_id)

    def create(self, name, mime, source_id, operation_id, parent=None):
        self.creates += 1
        self.files.append(dict(id=str(self.creates), name=name, mimeType=mime,
                              parents=[parent] if parent else ['drive-root'],
                              appProperties=dict(source=source_id, operation=operation_id)))
        raise TimeoutError('lost create response')


class FolderTests(unittest.TestCase):
    def test_nested_creation_lost_response_noop_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            index = parse_index(fixture())
            store = StateStore(Path(directory), index.id)
            layout = plan_layout(index, (Source('notes', 'a/b/note.md', Path('/external/note.md'), 'markdown', 'google-doc'),), {})
            remote = Remote()
            plan = folder_plan(layout, store, remote, 'digest')
            auth = Authorization(plan.digest, index.id, frozenset(f.id for f in layout.folders), frozenset({'create'}))
            effects = FolderEffects(layout, store, remote, lambda: 'digest')
            result = apply_sync(plan, auth, store, effects)
            self.assertEqual([f.status for f in result.files], ['verified'] * 3)
            self.assertEqual(remote.creates, 3)
            self.assertEqual(remote.files[1]['parents'], ['1'])
            self.assertEqual(remote.files[2]['parents'], ['2'])
            self.assertEqual([o.direction for o in folder_plan(layout, store, remote, 'digest').operations], ['noop'] * 3)
            self.assertEqual(recover(store, effects).files, ())

    def test_state_loss_does_not_adopt(self):
        with tempfile.TemporaryDirectory() as directory:
            index = parse_index(fixture())
            store = StateStore(Path(directory), index.id)
            layout = plan_layout(index, (Source('notes', 'a.md', Path('/external/a.md'), 'markdown', 'google-doc'),), {})
            remote = Remote()
            remote.files.append(dict(id='existing', appProperties={'source': layout.folders[0].id, 'operation': 'prior'}))
            self.assertEqual(folder_plan(layout, store, remote, 'digest').operations[0].reason, 'missing_folder_state')

    def test_granted_destination_parent_is_used_for_root_create(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = fixture()
            raw['roots']['notes']['destination_parent'] = 'granted-folder'
            index = parse_index(raw)
            store = StateStore(Path(directory), index.id)
            layout = plan_layout(index, (Source('notes', 'nested/note.md', Path('/external/note.md'), 'markdown', 'google-doc'),), {})
            remote = Remote()
            plan = folder_plan(layout, store, remote, 'digest')
            auth = Authorization(plan.digest, index.id, frozenset(f.id for f in layout.folders), frozenset({'create'}))
            result = apply_sync(plan, auth, store, FolderEffects(layout, store, remote, lambda: 'digest'))
            self.assertEqual([f.status for f in result.files], ['verified'] * 2)
            self.assertEqual(remote.files[0]['parents'], ['granted-folder'])
            self.assertEqual(remote.files[1]['parents'], ['1'])
            self.assertEqual([o.direction for o in folder_plan(layout, store, remote, 'digest').operations], ['noop'] * 2)
