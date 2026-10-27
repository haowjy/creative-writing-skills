import unittest
from drive_sync.conversion import render, docs_requests, utf16
from drive_sync.index import Diagnostic


class ConversionTests(unittest.TestCase):
    def test_frontmatter_comments_unicode_styles(self):
        result = render('---\r\ntitle: Secret\r\n---\r\n# Hi 😀\n\nA **bold** and *soft* word.<!-- private -->\n'.encode(), 'markdown')
        self.assertTrue(result.supported)
        self.assertNotIn('Secret', result.text)
        self.assertNotIn('private', result.text)
        self.assertTrue(result.source_prefix.startswith('---\r\n'))
        bold = next(s for s in result.styles if s.kind == 'strong')
        encoded = result.text.encode('utf-16-le')
        self.assertEqual(encoded[(bold.start-1)*2:(bold.end-1)*2].decode('utf-16-le'), 'bold')
        self.assertEqual(utf16('😀'), 2)

    def test_literal_text(self):
        result = render(b'*not italic*\r\n# not heading', 'text')
        self.assertEqual(result.styles, ())
        self.assertEqual(result.text, '*not italic*\n# not heading')

    def test_block_unsupported_not_silent(self):
        for value in (b'![image](image.png)', b'<script>alert(1)</script>', b'| a | b |\n|---|---|\n|c|d|'):
            result = render(value, 'markdown')
            self.assertFalse(result.supported)
            with self.assertRaises(Diagnostic):
                docs_requests(result, tab_id='t', revision='r', old_end=2)

    def test_links_lists_code(self):
        result = render(b'- [Example](https://example.com)\n- `code`\n', 'markdown')
        self.assertTrue(result.supported)
        self.assertEqual(sum(s.kind == 'bullet' for s in result.styles), 2)
        self.assertFalse(render(b'[Local](a.md)', 'markdown').supported)

    def test_numbered_list_uses_docs_not_slides_preset(self):
        result = render(b'1. One\n2. Two\n', 'markdown')
        batch = docs_requests(result, tab_id='tab', revision='r', old_end=2)
        presets = [r['createParagraphBullets']['bulletPreset']
                   for r in batch['requests'] if 'createParagraphBullets' in r]
        self.assertEqual(presets, ['NUMBERED_DECIMAL_ALPHA_ROMAN'] * 2)

    def test_required_revision_and_utf16_ranges(self):
        result = render('**😀**'.encode(), 'markdown')
        batch = docs_requests(result, tab_id='tab', revision='fresh', old_end=5)
        self.assertEqual(batch['writeControl'], {'requiredRevisionId': 'fresh'})
        style = next(r['updateTextStyle'] for r in batch['requests'] if 'updateTextStyle' in r and r['updateTextStyle']['textStyle'].get('bold'))
        self.assertEqual(style['range'], dict(tabId='tab', startIndex=1, endIndex=3))

    def test_formats_still_gated(self):
        with self.assertRaises(Diagnostic):
            render(b'anything', 'epub')
        self.assertTrue(render(b'<p>Readable HTML</p>', 'html').supported)

    def test_comment_wrapped_html_is_not_silently_omitted(self):
        result = render(b'<!-- hidden -->\n<div>Visible content</div>\n<!-- hidden -->\n', 'markdown')
        self.assertFalse(result.supported)
        self.assertTrue(render(b'<!-- one -->\n<!-- two -->\n\nHello\n','markdown').supported)
