from pathlib import Path
import unittest
from drive_sync.index import parse_index, Source
from drive_sync.layout import plan_layout, rebind_identity
from drive_sync.index import Diagnostic
from test_index import fixture


class LayoutTests(unittest.TestCase):
    def test_parent_first_full_names_stable_ids(self):
        index = parse_index(fixture())
        sources = tuple(Source('notes', p, Path('/external') / p, 'markdown', 'google-doc')
                        for p in ('nested/deep/a.md', 'nested/deep/a.txt'))
        identities = {}
        layout = plan_layout(index, sources, identities)
        self.assertEqual([f.relative_path for f in layout.folders], ['.', 'nested', 'nested/deep'])
        self.assertEqual([f.name for f in layout.files], ['a.md', 'a.txt'])
        self.assertEqual(layout, plan_layout(index, sources, identities))
        self.assertEqual(len(set(identities.values())), 5)
        self.assertEqual(layout.destination_parents, ())

    def test_destination_parent_is_root_only(self):
        raw = fixture()
        raw['roots']['notes']['destination_parent'] = 'granted-folder'
        layout = plan_layout(parse_index(raw), (Source('notes', 'a.md', Path('/external/a.md'), 'markdown', 'google-doc'),), {})
        self.assertEqual(layout.destination_parents, (('notes', 'granted-folder'),))
        self.assertIsNone(layout.folders[0].parent_id)

    def test_empty_selection_no_folders_and_retains_identity(self):
        identities = {'old': '590b7d30-bc08-45e3-aee3-f6bbfdac6342'}
        self.assertEqual(plan_layout(parse_index(fixture()), (), identities).folders, ())
        self.assertIn('old', identities)

    def test_rebind_preserves_uuid(self):
        identities = {'file:notes:a.md': '590b7d30-bc08-45e3-aee3-f6bbfdac6342'}
        result = rebind_identity(identities, old_root='notes', old_path='a.md', new_root='notes', new_path='b.md')
        self.assertEqual(result['file:notes:b.md'], identities['file:notes:a.md'])
        with self.assertRaises(Diagnostic):
            rebind_identity(result, old_root='notes', old_path='a.md', new_root='notes', new_path='b.md')
