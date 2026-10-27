from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from drive_sync.application import initialize_folders, resolve_reviewed
from drive_sync.state import StateStore
from drive_sync.storage import Draft, commit
from test_folder_layout_probe import LayoutRemote
from test_index import fixture
from test_scoping import authorize


class LayoutGuardTests(unittest.TestCase):
    def fixture(self, root):
        (root / 'notes/nested').mkdir(parents=True)
        (root / 'notes/nested/a.txt').write_text('Synthetic.\n')
        index = root / 'index.yaml'
        raw = fixture()
        commit(index, Draft(raw), None)
        remote = LayoutRemote()
        plan = initialize_folders(index, remote, home=root / 'state')
        initialize_folders(index, remote, authorize(plan), home=root / 'state')
        folder = next(m for m in remote.files.values() if m['name'] == 'nested')
        folder.update(name='moved', version='2')
        remote.calls.clear()
        return index, raw, remote, folder

    def test_identity_and_version_races_before_prepare_cannot_write(self):
        for change in ('source', 'id', 'mime', 'version'):
            with self.subTest(change=change), TemporaryDirectory() as directory:
                root = Path(directory)
                index, raw, remote, folder = self.fixture(root)
                sid = folder['appProperties']['source']
                plan = resolve_reviewed(index, remote, sid, 'restore-layout', home=root / 'state')
                guard = remote.metadata_guard
                def changed(file_id):
                    metadata, etag = guard(file_id)
                    if change == 'source':
                        metadata['appProperties']['source'] = 'another-source'
                    elif change == 'id':
                        metadata['id'] = 'another-object'
                    elif change == 'mime':
                        metadata['mimeType'] = 'text/plain'
                    else:
                        metadata['version'] = '3'
                    return metadata, etag
                remote.metadata_guard = changed
                store = StateStore(root / 'state', raw['id'])
                before = (store.path / 'bindings.json').read_bytes()
                result = resolve_reviewed(index, remote, sid, 'restore-layout', authorize(plan), home=root / 'state')
                self.assertEqual(result.files[0].status, 'conflict', result)
                self.assertEqual(remote.calls, [])
                self.assertEqual((store.path / 'bindings.json').read_bytes(), before)
                self.assertEqual(store.pending(), ())

    def test_file_readback_metadata_race_retains_pending_repair(self):
        from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index, raw, remote, folder = self.fixture(root)
            folder['name'] = 'nested'
            plan = initialize_documents(index, remote, home=root / 'state')
            initialize_documents(index, remote, authorize(plan), home=root / 'state')
            plan = combined_plan(preview_sync(index, remote, home=root / 'state'))
            apply_reviewed(index, remote, authorize(plan), home=root / 'state')
            document = next(m for m in remote.files.values() if m['name'] == 'a.txt')
            document['name'] = 'renamed.txt'
            sid = document['appProperties']['source']
            plan = resolve_reviewed(index, remote, sid, 'restore-layout', home=root / 'state')
            update, observe = remote.update_layout, remote.observe_document
            def race(file_id):
                value = observe(file_id)
                remote.files[file_id]['version'] = str(int(remote.files[file_id]['version']) + 1)
                return value
            def mutate(file_id, **kwargs):
                update(file_id, **kwargs)
                remote.observe_document = race
            remote.update_layout = mutate
            store = StateStore(root / 'state', raw['id'])
            before = (store.path / 'bindings.json').read_bytes()
            result = resolve_reviewed(index, remote, sid, 'restore-layout', authorize(plan), home=root / 'state')
            self.assertEqual(result.files[0].status, 'pending')
            self.assertEqual(result.files[0].reason, 'remote_race')
            self.assertEqual((store.path / 'bindings.json').read_bytes(), before)

    def test_wrong_readback_identity_does_not_verify_layout_or_advance_binding(self):
        for change in ('source', 'mime', 'id'):
            with self.subTest(change=change), TemporaryDirectory() as directory:
                root = Path(directory)
                index, raw, remote, folder = self.fixture(root)
                sid = folder['appProperties']['source']
                plan = resolve_reviewed(index, remote, sid, 'restore-layout', home=root / 'state')
                update = remote.update_layout
                def mutate(file_id, **kwargs):
                    update(file_id, **kwargs)
                    if change == 'source':
                        remote.files[file_id]['appProperties']['source'] = 'another-source'
                    elif change == 'mime':
                        remote.files[file_id]['mimeType'] = 'text/plain'
                    else:
                        remote.files[file_id]['id'] = 'another-object'
                remote.update_layout = mutate
                store = StateStore(root / 'state', raw['id'])
                before = (store.path / 'bindings.json').read_bytes()
                result = resolve_reviewed(index, remote, sid, 'restore-layout', authorize(plan), home=root / 'state')
                self.assertEqual(result.files[0].status, 'pending')
                self.assertEqual(result.files[0].reason, 'layout_identity_mismatch')
                self.assertEqual(result.files[0].destination, folder['id'] if change != 'id' else next(iter(store.pending())).remote_id)
                self.assertEqual(len(remote.calls), 1)
                self.assertEqual((store.path / 'bindings.json').read_bytes(), before)
                self.assertEqual(len(store.pending()), 1)
