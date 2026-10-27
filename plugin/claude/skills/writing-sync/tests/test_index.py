import copy
from pathlib import Path
import tempfile
import unittest

from drive_sync.index import Diagnostic, matches, parse_index, resolve
from drive_sync.storage import Draft, Edit, commit, decode, edit_draft, load_index


def fixture():
    return dict(version=1, kind="drive-sync", id="590b7d30-bc08-45e3-aee3-f6bbfdac6342", auth="personal",
                roots={"notes": dict(path="notes", destination_name="Notes")},
                selection=dict(include=[dict(root="notes", path=".", glob="**/*")], files=[], exclude=[]),
                policy=dict(default_storage="google-doc", formats=["markdown", "text", "html", "epub"], overrides=[]))


class IndexTests(unittest.TestCase):
    def test_natural_order_ties_are_independent_of_directory_enumeration(self):
        from unittest.mock import patch
        names = ['a.md', 'A.md', '2.md', '02.md', '10.md', 'a2.md', 'a02.md']
        for name in names:
            (self.path / 'notes' / name).write_text(name)
        expected = ['02.md', '2.md', '10.md', 'a02.md', 'a2.md', 'A.md', 'a.md']
        for order in (names, list(reversed(names)), sorted(names)):
            with self.subTest(order=order), patch('drive_sync.index.os.walk',
                    return_value=iter([(str(self.path / 'notes'), [], order)])):
                self.assertEqual([s.relative_path for s in resolve(parse_index(fixture()), self.index)], expected)

    def test_failed_directory_scan_never_returns_partial_selection(self):
        import errno
        import os
        from unittest.mock import patch
        child = self.path / 'notes' / 'unreadable'
        child.mkdir()
        (child / 'hidden.md').write_text('must not silently omit')
        original = os.scandir
        for failure in (PermissionError, FileNotFoundError):
            def scan(path):
                if Path(path) == child:
                    raise failure(errno.EACCES, 'private OS diagnostic', str(child))
                return original(path)
            with self.subTest(failure=failure), patch('drive_sync.index.os.scandir', side_effect=scan):
                with self.assertRaises(Diagnostic) as caught:
                    resolve(parse_index(fixture()), self.index)
                self.assertEqual(caught.exception.code, 'source_scan_failed')
                self.assertEqual(caught.exception.source, str(child))
                self.assertEqual(caught.exception.operation, 'resolve-selection')
                self.assertNotIn('private OS diagnostic', str(caught.exception.as_dict()))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        (self.path / "notes").mkdir()
        (self.path / "notes/a.md").write_text("Hello")
        self.index = self.path / "index.yaml"

    def test_globs(self):
        for path in ("a.md", "x/a.md", "x/y/a.md"):
            self.assertTrue(matches(path, "**/*.md"))
        self.assertFalse(matches("x/a.md", "*.md"))
        self.assertTrue(matches("a/b", "a/**/b"))

    def test_resolve_relative_index_and_natural_order(self):
        (self.path / "notes/10.md").write_text("10")
        (self.path / "notes/2.md").write_text("2")
        sources = resolve(parse_index(fixture()), self.index)
        self.assertEqual([s.relative_path for s in sources], ["2.md", "10.md", "a.md"])

    def test_exclusion_beats_explicit(self):
        raw = fixture()
        raw["selection"]["files"] = [dict(root="notes", path="a.md")]
        raw["selection"]["exclude"] = [dict(root="notes", glob="a.md")]
        self.assertEqual(resolve(parse_index(raw), self.index), ())

    def test_conflicting_overrides(self):
        raw = fixture()
        raw["policy"]["overrides"] = [dict(root="notes", glob="**/*", storage=m) for m in ("original", "google-doc")]
        with self.assertRaises(Diagnostic):
            resolve(parse_index(raw), self.index)

    def test_unsupported_and_original(self):
        (self.path / "notes/data.bin").write_bytes(b"\x00")
        raw = fixture()
        with self.assertRaises(Diagnostic):
            resolve(parse_index(raw), self.index)
        raw["policy"]["default_storage"] = "original"
        self.assertEqual(len(resolve(parse_index(raw), self.index)), 2)

    def test_unsafe_paths_and_overlap(self):
        for value in ("../notes", "/notes", "a/../b"):
            raw = fixture()
            raw["selection"]["include"][0]["path"] = value
            with self.assertRaises(Diagnostic):
                parse_index(raw)
        raw = fixture()
        raw["roots"]["other"] = dict(path="notes", destination_name="Other")
        with self.assertRaises(Diagnostic):
            resolve(parse_index(raw), self.index)

    def test_symlink(self):
        (self.path / "notes/link.md").symlink_to(self.path / "notes/a.md")
        with self.assertRaises(Diagnostic):
            resolve(parse_index(fixture()), self.index)

    def test_compound_commit_and_stale_guard(self):
        loaded = commit(self.index, Draft(fixture()), None)
        draft = edit_draft(loaded, (Edit("set", ("auth",), "second"),))
        saved = commit(self.index, draft, loaded.digest)
        self.assertEqual(load_index(self.index).model.auth, "second")
        with self.assertRaises(Diagnostic):
            commit(self.index, Draft(fixture()), loaded.digest)
        self.assertEqual(load_index(self.index).digest, saved.digest)
        self.assertEqual(self.index.stat().st_mode & 0o777, 0o600)

    def test_yaml_rejects_tags_duplicates_cycles(self):
        for value in (b"!!python/object:foo {}", b"x: 1\nx: 2", b"x: &x [*x]"):
            with self.assertRaises(Diagnostic):
                decode(value)

    def test_unknown_fields_and_bool_version(self):
        for key, value in (("bad", 1), ("version", True)):
            raw = fixture()
            raw[key] = value
            with self.assertRaises(Diagnostic):
                parse_index(raw)

    def test_destination_parent_is_optional_drive_id(self):
        raw = fixture()
        raw["roots"]["notes"]["destination_parent"] = "1F3D4GWjbWumHn3HdECIHBVW0b2aBzIzL"
        self.assertEqual(parse_index(raw).roots[0].destination_parent, "1F3D4GWjbWumHn3HdECIHBVW0b2aBzIzL")
        raw["roots"]["notes"]["destination_parent"] = "not a folder"
        with self.assertRaises(Diagnostic):
            parse_index(raw)


if __name__ == "__main__":
    unittest.main()

class MalformedTypesTests(unittest.TestCase):
    def test_application_validation_has_typed_diagnostics(self):
        for field, value in [('roots', []), ('policy', []), ('auth', {}), ('selection', 'invalid')]:
            raw = fixture()
            raw[field] = value
            with self.assertRaises(Diagnostic):
                parse_index(raw)
        raw = fixture()
        raw['selection']['include'][0]['root'] = []
        with self.assertRaises(Diagnostic):
            parse_index(raw)

    def test_hardlinked_sources_are_not_independent(self):
        import os
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            (path/'notes').mkdir()
            (path/'notes'/'a.md').write_text('same bytes')
            os.link(path/'notes'/'a.md',path/'notes'/'b.md')
            with self.assertRaises(Diagnostic):
                resolve(parse_index(fixture()),path/'index.yaml')
