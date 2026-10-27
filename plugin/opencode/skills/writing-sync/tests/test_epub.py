from io import BytesIO
from copy import copy
from zipfile import ZipFile
import unittest
from drive_sync.conversion import render
from drive_sync.index import Diagnostic


def book(extra=None):
    stream = BytesIO()
    with ZipFile(stream, 'w') as z:
        z.writestr('mimetype', 'application/epub+zip')
        z.writestr('META-INF/container.xml', '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/book.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr('OEBPS/book.opf', '<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" version="3.0" unique-identifier="book-id"><metadata><dc:identifier id="book-id">urn:uuid:6bbf1b47-e210-4235-8b63-74d23710a951</dc:identifier><dc:title>Test book</dc:title><dc:language>en</dc:language><meta property="dcterms:modified">2020-01-01T00:00:00Z</meta></metadata><manifest><item id="a" href="a.xhtml" media-type="application/xhtml+xml"/><item id="z" href="z.xhtml" media-type="application/xhtml+xml"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/></manifest><spine><itemref idref="z"/><itemref idref="a"/></spine></package>')
        z.writestr('OEBPS/a.xhtml', '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Second chapter</title></head><body><p>Second</p></body></html>')
        z.writestr('OEBPS/z.xhtml', '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>First chapter</title></head><body><p>First</p></body></html>')
        z.writestr('OEBPS/nav.xhtml', '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Contents</title></head><body><nav epub:type="toc"><h1>Contents</h1><ol><li><a href="z.xhtml">First chapter</a></li><li><a href="a.xhtml">Second chapter</a></li></ol></nav></body></html>')
        if extra:
            z.writestr(extra, 'unsafe')
    return stream.getvalue()


class EPUBTests(unittest.TestCase):
    def test_encoded_dtd_rejected_inside_container(self):
        markup = ('<!DOCTYPE container [<!ENTITY location "OEBPS/book.opf">]>'
                  '<container><rootfiles><rootfile full-path="&location;"/>'
                  '</rootfiles></container>')
        for encoding in ('utf-8', 'utf-16', 'utf-16-be', 'utf-16-le'):
            with self.subTest(encoding=encoding):
                target = BytesIO()
                with ZipFile(BytesIO(book())) as source, ZipFile(target, 'w') as out:
                    for item in source.infolist():
                        data = source.read(item.filename)
                        if item.filename == 'META-INF/container.xml':
                            data = markup.encode(encoding)
                        out.writestr(item, data)
                with self.assertRaises(Diagnostic) as caught:
                    render(target.getvalue(), 'epub')
                self.assertIn('DTD', caught.exception.reason)

    def test_literal_doctype_in_xml_comment_is_not_a_declaration(self):
        from drive_sync.epub_conversion import xml
        result = xml(b'<root><!-- literal <!DOCTYPE text> --><child/></root>')
        self.assertEqual(result.tag, 'root')

    def test_utf16_container_without_dtd_remains_readable(self):
        target = BytesIO()
        with ZipFile(BytesIO(book())) as source, ZipFile(target, 'w') as out:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename == 'META-INF/container.xml':
                    data = data.decode('utf-8').encode('utf-16')
                out.writestr(item, data)
        self.assertEqual(render(target.getvalue(), 'epub').text, 'First\nSecond\n')

    def test_invalid_package_metadata_and_resource_references(self):
        mutations = (
            (b'version="3.0"', b'version="3.3"'),
            (b'<dc:title>Test book</dc:title>', b''),
            (b'unique-identifier="book-id"', b'unique-identifier="missing"'),
            (b'property="dcterms:modified"', b'property="other"'),
            (b'href="a.xhtml"', b'href="missing.xhtml"'),
        )
        for old, new in mutations:
            with self.subTest(mutation=old):
                target = BytesIO()
                with ZipFile(BytesIO(book())) as source, ZipFile(target, 'w') as out:
                    for item in source.infolist():
                        data = source.read(item.filename)
                        if item.filename.endswith('.opf'):
                            self.assertIn(old, data)
                            data = data.replace(old, new)
                        out.writestr(item, data)
                with self.assertRaises(Diagnostic) as caught:
                    render(target.getvalue(), 'epub')
                self.assertEqual(caught.exception.code, 'invalid_epub')

    def test_spine_not_filename_order(self):
        result = render(book(), 'epub')
        self.assertTrue(result.supported)
        self.assertEqual(result.text, 'First\nSecond\n')

    def test_archive_traversal_and_encryption(self):
        for extra in ('../escape', 'META-INF/encryption.xml'):
            with self.assertRaises(Diagnostic):
                render(book(extra), 'epub')

    def test_package_fidelity_declarations_are_not_silently_ignored(self):
        mutations = (
            (b'</metadata>', b'<meta property="rendition:layout">pre-paginated</meta></metadata>', 'epub_layout'),
            (b'<itemref idref="z"', b'<itemref properties="rendition:layout-pre-paginated" idref="z"', 'epub_layout'),
            (b'<item id="z"', b'<item media-overlay="narration" id="z"', 'epub_media_overlay'),
            (b'<item id="z"', b'<item properties="scripted" id="z"', 'epub_resource_behavior'),
            (b'<spine>', b'<spine page-progression-direction="rtl">', 'epub_reading_order'),
            (b'<itemref idref="z"', b'<itemref linear="no" idref="z"', 'epub_reading_order'),
        )
        for old, new, code in mutations:
            with self.subTest(code=code, change=new):
                result = render(self.mutate_package(old, new), 'epub')
                self.assertFalse(result.supported)
                self.assertIn(code, {f.code for f in result.findings})
                self.assertEqual(result.text, 'First\nSecond\n')

    def test_explicit_default_layout_remains_supported(self):
        data = self.mutate_package(b'</metadata>', b'<meta property="rendition:layout">reflowable</meta></metadata>')
        self.assertTrue(render(data, 'epub').supported)

    @staticmethod
    def mutate_package(old, new):
        target = BytesIO()
        with ZipFile(BytesIO(book())) as source, ZipFile(target, 'w') as out:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename.endswith('.opf'):
                    data = data.replace(old, new)
                out.writestr(copy(item), data)
        return target.getvalue()

    def test_rendition_alias_cannot_bypass_fidelity_check(self):
        from drive_sync.epub_conversion import package_findings, xml
        package = xml(b'<package prefix="r: http://www.idpf.org/vocab/rendition/#"><metadata><meta property="r:layout">pre-paginated</meta></metadata><spine/></package>')
        self.assertIn('epub_layout', {f.code for f in package_findings(package, {})})
