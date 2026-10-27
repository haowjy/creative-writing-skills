"""Offline checks for the exact opt-in styled integration fixtures."""
from io import BytesIO
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from drive_sync.conversion import render
from drive_sync.return_conversion import return_candidate
from drive_sync.storage import digest
from live_styled_formats import seed_styled, styled_sources


class StyledFormatTests(unittest.TestCase):
    def test_word_return_retains_styles_and_source_structure(self):
        for name, source in styled_sources().items():
            with self.subTest(name=name):
                format = 'epub' if name.endswith('.epub') else 'html'
                before = render(source, format)
                self.assertTrue(before.supported)
                self.assertTrue({'heading', 'strong', 'em', 'link', 'bullet'}
                                <= {s.kind for s in before.styles})
                candidate = return_candidate(
                    source, expected_source_hash=digest(source), format=format,
                    baseline_text=before.text, remote_text=before.text.replace('bold', 'brave'))
                if format == 'html':
                    expected = source.replace(b'<strong>bold</strong>', b'<strong>brave</strong>')
                    self.assertEqual(candidate.data, expected)
                else:
                    with ZipFile(BytesIO(source)) as old, ZipFile(BytesIO(candidate.data)) as new:
                        self.assertEqual(old.namelist(), new.namelist())
                        changed = {n for n in old.namelist() if old.read(n) != new.read(n)}
                        self.assertEqual(changed, {'OEBPS/z.xhtml', 'OEBPS/book.opf'})
                        self.assertEqual(new.read('OEBPS/z.xhtml'), old.read('OEBPS/z.xhtml').replace(
                            b'<strong>bold</strong>', b'<strong>brave</strong>'))
                after = render(candidate.data, format)
                self.assertTrue(after.supported)
                self.assertEqual(after.text, before.text.replace('bold', 'brave'))
                self.assertEqual({s.kind for s in after.styles}, {s.kind for s in before.styles})
                end = before.text.index('bold') + len('bold')
                expected_styles = tuple(replace(s, start=s.start + (s.start >= end),
                                                end=s.end + (s.end >= end))
                                        for s in before.styles)
                self.assertEqual(after.styles, expected_styles)

    def test_seed_never_overwrites_an_existing_fixture(self):
        with TemporaryDirectory() as directory:
            run = Path(directory) / 'fixture'
            seed_styled(run)
            before = {p: p.read_bytes() for p in run.rglob('*') if p.is_file()}
            with self.assertRaises(FileExistsError):
                seed_styled(run)
            self.assertEqual(before, {p: p.read_bytes() for p in run.rglob('*') if p.is_file()})
