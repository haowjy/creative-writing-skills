"""Bounded EPUB package/spine reader. Never extracts or fetches archive URLs."""
from io import BytesIO
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
from zipfile import ZipFile, BadZipFile, ZIP_STORED

from .conversion import Finding, Rendering, Style, utf16
from .html_conversion import render_html
from .index import Diagnostic


def invalid(reason):
    raise Diagnostic('invalid_epub', reason, 'Repair the EPUB package before conversion; do not extract untrusted paths.')


class SafeTreeBuilder(ElementTree.TreeBuilder):
    """Reject DTDs after decoding, before processing their declarations.

    A byte substring check misses UTF-16 XML. XMLParser calls this target for
    every actual DOCTYPE, independent of the input encoding.
    """

    def doctype(self, name, pubid, system):
        invalid('DTD and entity declarations are unsupported.')


def xml(data):
    parser = ElementTree.XMLParser(target=SafeTreeBuilder())
    return ElementTree.fromstring(data, parser=parser)


def member_path(base, href):
    parsed = urlsplit(href)
    name = unquote(parsed.path)
    if parsed.scheme or parsed.netloc or '\\' in name or PurePosixPath(name).is_absolute():
        invalid('EPUB resource reference is not a safe local path.')
    parts = list(PurePosixPath(base).parent.parts)
    for part in PurePosixPath(name).parts:
        if part == '..':
            if not parts:
                invalid('EPUB resource escapes the archive.')
            parts.pop()
        elif part != '.':
            parts.append(part)
    return '/'.join(parts)


def package_findings(package, manifest):
    """Do not treat extracted chapter text as proof of package-level fidelity."""
    findings = []
    def add(code, reason):
        findings.append(Finding(code, reason,
            'Use explicit original-file storage or a reviewed format-aware conversion; do not silently flatten the EPUB.'))
    reserved = {'rendition': 'http://www.idpf.org/vocab/rendition/#',
                'media': 'http://www.idpf.org/epub/vocab/overlays/#'}
    prefixes = dict(reserved)
    declarations = package.get('prefix', '').split()
    if len(declarations) % 2:
        invalid('EPUB package vocabulary prefix declaration is malformed.')
    for key, uri in zip(declarations[::2], declarations[1::2]):
        if not key.endswith(':'):
            invalid('EPUB package vocabulary prefix declaration is malformed.')
        key = key[:-1]
        if key in reserved and uri != reserved[key]:
            add('epub_vocabulary', 'EPUB overrides a reserved rendering vocabulary prefix.')
        prefixes[key] = uri
    def canonical(value):
        prefix, separator, term = value.partition(':')
        if separator:
            for name, uri in reserved.items():
                if prefixes.get(prefix) == uri:
                    return name + ':' + term
        return value
    defaults = {'rendition:layout': 'reflowable', 'rendition:orientation': 'auto',
                'rendition:spread': 'auto', 'rendition:flow': 'auto'}
    for meta in package.findall('./{*}metadata/{*}meta'):
        prop = canonical(meta.get('property', ''))
        if prop.startswith('rendition:') and (prop not in defaults or (meta.text or '').strip() != defaults[prop]):
            add('epub_layout', 'EPUB rendition layout or presentation constraints are not represented in Docs.')
        if prop.startswith('media:'):
            add('epub_media_overlay', 'EPUB media overlay behavior is not represented in Docs.')
    for item in manifest.values():
        if item.get('media-overlay'):
            add('epub_media_overlay', 'EPUB synchronized narration is not represented in Docs.')
        properties = set(item.get('properties', '').split())
        if properties & {'scripted', 'remote-resources', 'mathml', 'svg'}:
            add('epub_resource_behavior', 'EPUB declares active, external or specialized rendering resources.')
    spine = package.find('./{*}spine')
    if spine is not None:
        if spine.get('page-progression-direction', 'default') not in ('default', 'ltr'):
            add('epub_reading_order', 'EPUB page progression cannot be preserved by the current Docs renderer.')
        for ref in spine.findall('./{*}itemref'):
            if ref.get('linear', 'yes') != 'yes':
                add('epub_reading_order', 'EPUB contains auxiliary non-linear reading content.')
            if {canonical(p) for p in ref.get('properties', '').split()} - {'rendition:layout-reflowable'}:
                add('epub_layout', 'EPUB spine presentation overrides are not represented in Docs.')
    return findings


def render_epub(data: bytes) -> Rendering:
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            names = [e.filename for e in entries]
            if not entries or len(entries) > 1000 or len(names) != len(set(names)):
                invalid('EPUB has empty, duplicate or excessive entries.')
            if sum(e.file_size for e in entries) > 20_000_000 or any(e.flag_bits & 1 for e in entries):
                invalid('EPUB is encrypted or exceeds expanded-size limits.')
            if any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts or '\\' in n for n in names):
                invalid('EPUB contains unsafe archive paths.')
            if 'META-INF/encryption.xml' in names or 'META-INF/signatures.xml' in names:
                invalid('Encrypted or signed EPUB requires a specialized preservation workflow.')
            if entries[0].filename != 'mimetype' or entries[0].compress_type != ZIP_STORED or entries[0].extra:
                invalid('EPUB mimetype must be the first uncompressed entry without extra fields.')
            if archive.read('mimetype') != b'application/epub+zip':
                invalid('EPUB mimetype is missing or incorrect.')
            container = xml(archive.read('META-INF/container.xml'))
            roots = container.findall('.//{*}rootfile')
            if len(roots) != 1:
                invalid('Exactly one EPUB rendition is currently supported.')
            package_path = member_path('container.xml', roots[0].attrib['full-path'])
            package = xml(archive.read(package_path))
            # EPUB 3.3 section 5.4 retains the package version value 3.0.
            # https://www.w3.org/TR/epub-33/#sec-package-elem
            if package.tag != '{http://www.idpf.org/2007/opf}package' or package.get('version') != '3.0':
                invalid('An EPUB 3 package with the OPF namespace is required.')
            metadata = package.find('./{*}metadata')
            if metadata is None:
                invalid('EPUB metadata is missing.')
            required = ('identifier','title','language')
            for name in required:
                values = metadata.findall('{http://purl.org/dc/elements/1.1/}' + name)
                if not values or any(not (v.text or '').strip() for v in values):
                    invalid('EPUB is missing required nonempty Dublin Core metadata.')
            unique = package.get('unique-identifier')
            if not unique or not any(item.get('id') == unique for item in metadata.findall('{http://purl.org/dc/elements/1.1/}identifier')):
                invalid('EPUB unique-identifier does not identify a metadata identifier.')
            modified = [item for item in metadata.findall('{*}meta') if item.get('property') == 'dcterms:modified']
            if len(modified) != 1:
                invalid('EPUB requires exactly one modification timestamp.')
            manifest = {}
            for item in package.findall('./{*}manifest/{*}item'):
                key = item.attrib['id']
                if key in manifest:
                    invalid('EPUB manifest contains duplicate IDs.')
                manifest[key] = item.attrib
            for item in manifest.values():
                if member_path(package_path,item['href']) not in names:
                    invalid('EPUB manifest references a missing resource.')
            text, styles, findings = '', [], package_findings(package, manifest)
            spine = package.findall('./{*}spine/{*}itemref')
            if not spine:
                invalid('EPUB has no reading spine.')
            for itemref in spine:
                item = manifest[itemref.attrib['idref']]
                if item.get('media-type') != 'application/xhtml+xml':
                    invalid('Spine contains a non-XHTML resource.')
                member = member_path(package_path, item['href'])
                raw = archive.read(member)
                xml(raw)  # Enforce well-formed XHTML, without DTD/entities.
                result = render_html(raw)
                offset = utf16(text)
                styles.extend(Style(s.start + offset, s.end + offset, s.kind, s.value) for s in result.styles)
                text += result.text
                findings.extend(result.findings)
            # Package metadata and unrelated members must survive a future pull;
            # this renderer does not claim export reconstruction is lossless.
            return Rendering('epub', text, tuple(styles), tuple(dict.fromkeys(findings)))
    except Diagnostic:
        raise
    except (BadZipFile, KeyError, ValueError, ElementTree.ParseError, RuntimeError):
        invalid('EPUB package or resource references are invalid.')
