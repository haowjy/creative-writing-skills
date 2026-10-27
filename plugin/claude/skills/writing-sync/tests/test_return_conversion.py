import unittest
from drive_sync.conversion import render
from drive_sync.index import Diagnostic
from drive_sync.return_conversion import return_candidate
from drive_sync.storage import digest


class ReturnTests(unittest.TestCase):
    def candidate(self, source, remote, format='markdown'):
        return return_candidate(source, expected_source_hash=digest(source), format=format,
                                baseline_text=render(source, format).text, remote_text=remote)

    def test_preserves_frontmatter_and_comments_bytes(self):
        source = b'---\r\ntitle: "Unchanged" # yaml comment\r\n---\r\n\r\nHello world.<!-- secret -->\r\n'
        candidate = self.candidate(source, 'Hello everyone.\n')
        self.assertEqual(candidate.data, source.replace(b'world', b'everyone'))

    def test_unicode_change(self):
        source = 'Hello 😀 friend.\n'.encode()
        self.assertEqual(self.candidate(source, 'Hello 😀 reader.\n').data, 'Hello 😀 reader.\n'.encode())

    def test_repeated_text_is_not_guessed(self):
        source = b'Same.\n\nSame.\n'
        with self.assertRaises(Diagnostic):
            self.candidate(source, 'Changed.\nSame.\n')

    def test_cross_comment_blocked(self):
        source = b'Before<!-- hidden -->after.\n'
        with self.assertRaises(Diagnostic):
            self.candidate(source, 'Different.\n')

    def test_remote_syntax_not_interpreted_silently(self):
        with self.assertRaises(Diagnostic):
            self.candidate(b'Hello world.\n', '**Hello** world.\n')

    def test_text_crlf_preserved(self):
        self.assertEqual(self.candidate(b'Hello\r\nworld\r\n', 'Hello\nreader\n', 'text').data, b'Hello\r\nreader\r\n')

    def test_stale_baseline_blocks(self):
        with self.assertRaises(Diagnostic):
            return_candidate(b'local', expected_source_hash='old', format='text', baseline_text='old', remote_text='remote')

    def test_text_edit_inside_emphasis_preserves_delimiters(self):
        source=b'Hello **bold world** and *soft words*.\n'
        self.assertEqual(self.candidate(source,'Hello bold friend and soft words.\n').data,
                         b'Hello **bold friend** and *soft words*.\n')

    def test_link_label_preserves_original_link_syntax(self):
        source=b'Visit [Example](https://example.com).\n'
        self.assertEqual(self.candidate(source,'Visit Website.\n').data,
                         b'Visit [Website](https://example.com).\n')

    def test_heading_text_edits_preserve_original_syntax(self):
        for source in (b'# Heading words\n', b'### Heading words ###\r\n',
                       b'Heading words\n=============\n', b'Heading words\r\n-------------\r\n',
                       b'## **Heading** words<!-- retained -->\n'):
            with self.subTest(source=source):
                rendered = render(source, 'markdown')
                self.assertEqual(self.candidate(source, rendered.text.replace('words', 'text')).data,
                                 source.replace(b'words', b'text'))

    def test_repeated_heading_text_remains_ambiguous(self):
        source = b'# Same heading\n\n# Same heading\n'
        with self.assertRaises(Diagnostic):
            self.candidate(source, render(source, 'markdown').text.replace('Same', 'Changed', 1))

    def test_flat_list_text_preserves_markers_and_inline_source(self):
        for source in (b'- First words\n- Second item\n',
                       b'* First words\r\n* Second item\r\n',
                       b'+ First words\n+ Second item\n',
                       b'1. First words\n2. Second item\n',
                       b'1) First words\n2) Second item\n',
                       b'- **First** words<!-- retained -->\n- Second item\n'):
            with self.subTest(source=source):
                baseline = render(source, 'markdown').text
                self.assertEqual(self.candidate(source, baseline.replace('words', 'text')).data,
                                 source.replace(b'words', b'text'))

    def test_repeated_list_text_remains_ambiguous(self):
        source = b'- Same words\n- Same words\n'
        baseline = render(source, 'markdown').text
        with self.assertRaises(Diagnostic):
            self.candidate(source, baseline.replace('Same', 'Changed', 1))

    def test_unicode_separators_do_not_shift_markdown_source_offsets(self):
        for separator in ('\u2028', '\u2029', '\v'):
            for content in ('Second words.', '# Second words', '- Second words'):
                with self.subTest(separator=repr(separator), content=content):
                    source = ('First' + separator + 'part.\n\n' + content + '\n').encode()
                    baseline = render(source, 'markdown').text
                    self.assertEqual(self.candidate(source, baseline.replace('words', 'text')).data,
                                     source.replace(b'words', b'text'))

    def test_bare_cr_and_mixed_markdown_endings_keep_offsets(self):
        source = b'First paragraph.\r\r# Second words\r\n\r\n- Third item\n'
        baseline = render(source, 'markdown').text
        self.assertEqual(self.candidate(source, baseline.replace('words', 'text')).data,
                         source.replace(b'words', b'text'))
