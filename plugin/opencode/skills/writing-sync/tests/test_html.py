import unittest
from drive_sync.conversion import render


class HTMLTests(unittest.TestCase):
    def test_unicode_spaces_are_not_collapsed(self):
        result = render('<p>A&nbsp;&nbsp;B\u2003C</p>'.encode(), 'html')
        self.assertTrue(result.supported)
        self.assertEqual(result.text, 'A\u00a0\u00a0B\u2003C\n')

    def test_inline_code_collapses_but_pre_preserves_whitespace(self):
        inline = render(b'<p><code>A  B\r\nC</code></p>', 'html')
        pre = render(b'<pre>A  B\r\nC</pre>', 'html')
        self.assertEqual(inline.text, 'A B C\n')
        self.assertEqual(pre.text, 'A  B\nC\n')

    def test_unrepresented_semantic_attributes_block(self):
        for value in (b'<ol start="5"><li>Fifth</li></ol>',
                      b'<ol reversed><li>Last</li></ol>',
                      b'<p dir="rtl">Reading order</p>',
                      b'<p lang="fr">Bonjour</p>'):
            with self.subTest(value=value):
                result = render(value, 'html')
                self.assertFalse(result.supported)
                self.assertIn('html_presentation', {f.code for f in result.findings})

    def test_semantic_reading_and_styles(self):
        result = render(b'<!doctype html><html><head><title>Metadata</title></head><body><h1>Heading</h1><p>A <strong>bold</strong> word.</p></body></html>', 'html')
        self.assertTrue(result.supported, result.findings)
        self.assertEqual(result.text, 'Heading\nA bold word.\n')
        self.assertEqual({s.kind for s in result.styles}, {'heading', 'strong'})

    def test_comments_not_visible(self):
        self.assertEqual(render(b'<p>Hello<!-- private --> world</p>', 'html').text, 'Hello world\n')

    def test_css_scripts_assets_blocked(self):
        for source in (b'<script>fetch("secret")</script>', b'<p style="display:none">hidden</p>', b'<img src="https://example.com/private">', b'<table><tr><td>cell</td></tr></table>'):
            self.assertFalse(render(source, 'html').supported)

    def test_unicode_entity_and_external_link(self):
        result = render('<p>😀 &amp; <a href="https://example.com">link</a></p>'.encode(), 'html')
        self.assertTrue(result.supported)
        link = next(s for s in result.styles if s.kind == 'link')
        self.assertEqual(link.start, 6)

    def test_unbalanced_blocked(self):
        self.assertFalse(render(b'<p>unclosed', 'html').supported)
