from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from copy import copy
import unittest
from drive_sync.epub_return import patch_epub
from test_epub import book


class EPUBReturnTests(unittest.TestCase):
    def test_wrapped_xhtml_text_return_preserves_member_whitespace(self):
        stream = BytesIO()
        with ZipFile(BytesIO(book())) as original, ZipFile(stream, 'w') as target:
            for entry in original.infolist():
                data = original.read(entry.filename)
                if entry.filename == 'OEBPS/z.xhtml':
                    data = data.replace(b'<p>First</p>', b'<p>First\r\n    chapter</p>')
                target.writestr(copy(entry), data)
        source = stream.getvalue()
        result = patch_epub(source, 'First chapter\nSecond\n', 'Changed chapter\nSecond\n',
                            modified='2026-09-15T00:00:00Z')
        with ZipFile(BytesIO(source)) as before, ZipFile(BytesIO(result)) as after:
            self.assertEqual(after.read('OEBPS/z.xhtml'),
                             before.read('OEBPS/z.xhtml').replace(b'<p>First', b'<p>Changed'))
            for name in before.namelist():
                if name not in ('OEBPS/z.xhtml', 'OEBPS/book.opf'):
                    self.assertEqual(before.read(name), after.read(name))

    def test_preserves_other_members_and_updates_modified(self):
        source=book()
        result=patch_epub(source,'First\nSecond\n','Changed\nSecond\n',modified='2026-09-15T00:00:00Z')
        with ZipFile(BytesIO(source)) as before, ZipFile(BytesIO(result)) as after:
            self.assertEqual(before.namelist(), after.namelist())
            for name in before.namelist():
                if name not in ('OEBPS/z.xhtml', 'OEBPS/book.opf'):
                    self.assertEqual(before.read(name), after.read(name), name)
            self.assertEqual(before.getinfo('mimetype').compress_type, after.getinfo('mimetype').compress_type)
            self.assertIn(b'Changed',after.read('OEBPS/z.xhtml'))
            self.assertIn(b'2026-09-15T00:00:00Z',after.read('OEBPS/book.opf'))

    def test_length_changes_preserve_later_compressed_resources(self):
        stream = BytesIO()
        with ZipFile(BytesIO(book())) as original, ZipFile(stream, 'w') as target:
            target.comment = b'Archive preservation fixture'
            for entry in original.infolist():
                info = copy(entry)
                if info.filename != 'mimetype':
                    info.compress_type = ZIP_DEFLATED
                    info.comment = b'Member metadata'
                target.writestr(info, original.read(entry.filename))
        source = stream.getvalue()
        for replacement in ('X', 'A much longer sentence with 😀 and & signs'):
            with self.subTest(replacement=replacement):
                result = patch_epub(source, 'First\nSecond\n', replacement + '\nSecond\n',
                                    modified='2026-09-15T00:00:00Z')
                with ZipFile(BytesIO(source)) as before, ZipFile(BytesIO(result)) as after:
                    self.assertEqual(before.comment, after.comment)
                    self.assertEqual(before.namelist(), after.namelist())
                    self.assertIsNone(after.testzip())
                    for old in before.infolist():
                        new = after.getinfo(old.filename)
                        for field in ('date_time', 'compress_type', 'comment', 'extra', 'external_attr'):
                            self.assertEqual(getattr(old, field), getattr(new, field))
                        if old.filename not in ('OEBPS/z.xhtml', 'OEBPS/book.opf'):
                            self.assertEqual(before.read(old), after.read(new))

    def test_fixed_layout_return_is_blocked(self):
        from test_epub import EPUBTests
        from drive_sync.index import Diagnostic
        source = EPUBTests.mutate_package(b'</metadata>',
            b'<meta property="rendition:layout">pre-paginated</meta></metadata>')
        with self.assertRaises(Diagnostic) as caught:
            patch_epub(source, 'First\nSecond\n', 'Changed\nSecond\n')
        self.assertEqual(caught.exception.code, 'epub_return_conflict')
