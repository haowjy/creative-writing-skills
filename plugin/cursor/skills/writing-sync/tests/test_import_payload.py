import unittest
from drive_sync.conversion import render
from drive_sync.import_payload import import_html
from drive_sync.index import Diagnostic


class ImportTests(unittest.TestCase):
    def test_paragraph_boundaries_preserve_terminal_and_literal_newlines(self):
        from html.parser import HTMLParser
        from drive_sync.conversion import Rendering
        class Paragraphs(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = ''
            def handle_data(self, data):
                self.text += data
            def handle_endtag(self, tag):
                if tag == 'p':
                    self.text += '\n'
        for value in ('', 'one', 'one\n', 'one\n\n', '\n', 'one\ntwo\n',
                      '😀\u2028literal\u2029text\vhere\n'):
            with self.subTest(value=value):
                parser = Paragraphs()
                parser.feed(import_html(Rendering('text', value, ())).decode())
                self.assertEqual(parser.text, value + '\n')

    def test_escaped_text_styles_lists(self):
        source = '# Heading\n\n- **Bold 😀**\n- A & B\n'.encode()
        html = import_html(render(source, 'markdown')).decode()
        self.assertIn('Heading</h1>', html)
        self.assertEqual(html.count('<li style='), 2)
        self.assertIn('font-weight:bold', html)
        self.assertIn('A &amp; B', html)

    def test_literal_text_cannot_inject_html(self):
        html = import_html(render(b'<script>alert(1)</script>', 'text')).decode()
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_unsupported_input_fails(self):
        with self.assertRaises(Diagnostic):
            import_html(render(b'![image](local.png)', 'markdown'))
