from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from drive_sync.missing import missing_plan,acknowledge_missing
from drive_sync.state import StateStore,write_json,read_json
from drive_sync.storage import Draft, commit
from drive_sync.index import Diagnostic
from test_index import fixture


class MissingTests(unittest.TestCase):
    def test_cli_round_trip_uses_typed_plan_without_oauth(self):
        from contextlib import redirect_stdout
        from io import StringIO
        import json
        from drive_sync.cli import main
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index = self.index(root)
            store = StateStore(root / 'state', fixture()['id'])
            write_json(store.path / 'bindings.json', {'source': dict(
                kind='file', path=str(root / 'missing.md'), remote_id='remote')})
            args = ['--index', str(index), 'state', 'acknowledge-missing',
                    '--source', 'source', '--state-home', str(root / 'state')]
            with patch('drive_sync.auth.authorized_session', side_effect=AssertionError('OAuth unnecessary')):
                with redirect_stdout(StringIO()) as output:
                    self.assertEqual(main(args), 0)
                preview = json.loads(output.getvalue())
                self.assertEqual(preview['plan']['root_path'], str(root))
                with redirect_stdout(StringIO()) as output:
                    self.assertEqual(main(args + ['--apply', '--plan-digest', preview['digest']]), 0)
                self.assertFalse(json.loads(output.getvalue())['remote_deleted'])

    def test_root_unavailable_replaced_or_index_changed_blocks_apply(self):
        for change in ('unavailable', 'replaced', 'index'):
            with self.subTest(change=change), TemporaryDirectory() as directory:
                base = Path(directory)
                root = base / 'notes'
                root.mkdir()
                index = base / 'index.yaml'
                commit(index, Draft(fixture()), None)
                store = StateStore(base / 'state', fixture()['id'])
                write_json(store.path / 'bindings.json', {'source': dict(
                    kind='file', path=str(root / 'missing.md'), remote_id='remote')})
                plan = missing_plan(index, store, 'source')
                before = (store.path / 'bindings.json').read_bytes()
                if change == 'index':
                    index.write_bytes(index.read_bytes() + b'\n# concurrent edit\n')
                else:
                    root.rename(base / 'old-notes')
                    if change == 'replaced':
                        root.mkdir()
                with self.assertRaises(Diagnostic) as caught:
                    acknowledge_missing(index, store, 'source', plan.digest)
                expected = 'missing_root' if change == 'unavailable' else 'stale_acknowledgment'
                self.assertEqual(caught.exception.code, expected)
                self.assertEqual((store.path / 'bindings.json').read_bytes(), before)

    def test_outside_bound_path_cannot_be_acknowledged(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'notes').mkdir()
            index = base / 'index.yaml'
            commit(index, Draft(fixture()), None)
            store = StateStore(base / 'state', fixture()['id'])
            write_json(store.path / 'bindings.json', {'source': dict(
                kind='file', path=str(base / 'elsewhere/missing.md'), remote_id='remote')})
            with self.assertRaises(Diagnostic) as caught:
                missing_plan(index, store, 'source')
            self.assertEqual(caught.exception.code, 'missing_source_root')

    def index(self, root):
        raw = fixture()
        raw['roots']['notes']['path'] = str(root)
        path = root / 'index.yaml'
        commit(path, Draft(raw), None)
        return path

    def test_acknowledgment_retains_binding_and_baseline(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)
            index = self.index(path)
            store=StateStore(path/'state',fixture()['id'])
            binding=dict(kind='file',path=str(path/'missing.md'),remote_id='remote',baseline={'protected':'baseline'})
            write_json(store.path/'bindings.json',{'source':binding})
            plan=missing_plan(index, store,'source')
            result=acknowledge_missing(index, store,'source',plan.digest)
            self.assertFalse(result['remote_deleted'])
            actual=read_json(store.path/'bindings.json')['source']
            self.assertEqual(actual['baseline'],binding['baseline'])
            self.assertEqual(actual['remote_id'],'remote')
            (path/'missing.md').write_text('returned')
            with self.assertRaises(Diagnostic):missing_plan(index, store,'source')

    def test_unreadable_path_is_not_acknowledged_as_absent(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index = self.index(root)
            store = StateStore(root / 'state', fixture()['id'])
            source = root / 'missing.md'
            write_json(store.path / 'bindings.json', {'source': dict(kind='file', path=str(source), remote_id='remote')})
            plan = missing_plan(index, store, 'source')
            before = (store.path / 'bindings.json').read_bytes()
            original_lstat = Path.lstat
            def guarded(path, *args, **kwargs):
                if path == source:
                    raise PermissionError('private filesystem error')
                return original_lstat(path, *args, **kwargs)
            with patch.object(Path, 'lstat', guarded):
                with self.assertRaises(Diagnostic) as caught:
                    acknowledge_missing(index, store, 'source', plan.digest)
            self.assertEqual(caught.exception.code, 'source_presence_unreadable')
            self.assertNotIn('private filesystem error', str(caught.exception.as_dict()))
            self.assertEqual((store.path / 'bindings.json').read_bytes(), before)

    def test_dangling_symlink_still_occupies_source_path(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index = self.index(root)
            store = StateStore(root / 'state', fixture()['id'])
            source = root / 'missing.md'
            source.symlink_to(root / 'absent-target')
            write_json(store.path / 'bindings.json', {'source': dict(kind='file', path=str(source), remote_id='remote')})
            with self.assertRaises(Diagnostic) as caught:
                missing_plan(index, store, 'source')
            self.assertEqual(caught.exception.code, 'source_present')
