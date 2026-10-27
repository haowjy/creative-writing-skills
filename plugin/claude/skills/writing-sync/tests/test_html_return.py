import unittest
from drive_sync.conversion import render
from drive_sync.return_conversion import return_candidate
from drive_sync.storage import digest
from drive_sync.index import Diagnostic


class HTMLReturnTests(unittest.TestCase):
    def test_pretty_printed_words_preserve_collapsed_source_whitespace(self):
        for separator in ('\r\n    ', '\n\t', '\r  ', '\t\t', '   '):
            with self.subTest(separator=repr(separator)):
                source = ('<p id="original">\r\n  Hello' + separator +
                          'reader 😀\r\n</p><!-- keep -->').encode()
                baseline = render(source, 'html').text
                self.assertEqual(self.patch(source, baseline.replace('reader', 'writer')),
                                 source.replace(b'reader', b'writer'))

    def test_collapsed_mapping_uses_whole_run_context_for_repeated_words(self):
        source = b'<p>Word   Word unique.</p><p>Word elsewhere.</p>'
        baseline = render(source, 'html').text
        self.assertEqual(self.patch(source, baseline.replace('Word Word', 'Word Edit')),
                         source.replace(b'Word unique', b'Edit unique'))

    def test_collapsed_whitespace_and_duplicate_context_stay_protected(self):
        source = b'<p>Hello\n  reader.</p>'
        with self.assertRaises(Diagnostic):
            self.patch(source, render(source, 'html').text.replace('Hello reader', 'Greetings'))
        source = b'<p>Hello\n reader.</p><p>Hello\n reader.</p>'
        with self.assertRaises(Diagnostic):
            self.patch(source, render(source, 'html').text.replace('reader', 'writer', 1))

    def patch(self, source, remote):
        return return_candidate(source,expected_source_hash=digest(source),format='html',baseline_text=render(source,'html').text,remote_text=remote).data
    def test_preserves_markup_metadata_comment(self):
        source=b'<!doctype html><html><head><title>Private</title></head><body>\r\n<p id="same">Hello world.</p><!-- private -->\r\n</body></html>'
        self.assertEqual(self.patch(source,'Hello reader.\n'),source.replace(b'world',b'reader'))
    def test_escapes_new_text(self):
        self.assertEqual(self.patch(b'<p>Word</p>','A & B\n'),b'<p>A &amp; B</p>')
    def test_edit_preserves_nonbreaking_space_entity(self):
        source = b'<p>Hello&nbsp;reader</p>'
        self.assertEqual(self.patch(source, 'Hello\u00a0writer\n'),
                         b'<p>Hello&nbsp;writer</p>')
    def test_repeated_text_blocks(self):
        with self.assertRaises(Diagnostic):
            self.patch(b'<p>Same</p><p>Same</p>','Different\nSame\n')

    def test_offsets_after_non_lf_separators_preserve_source_bytes(self):
        for separator in ('\r', '\r\n', '\u2028', '\u2029', '\v'):
            with self.subTest(separator=repr(separator)):
                source = ('<p>First</p>' + separator + '<p>Second word.</p>').encode()
                baseline = render(source, 'html').text
                self.assertEqual(self.patch(source, baseline.replace('word', 'edit')),
                                 source.replace(b'word', b'edit'))

    def test_multibyte_prefix_and_mixed_line_endings(self):
        source = '<p>😀 First</p>\r<p>Second</p>\n<p>Third word.</p>'.encode()
        baseline = render(source, 'html').text
        self.assertEqual(self.patch(source, baseline.replace('word', 'edit')),
                         source.replace(b'word', b'edit'))
