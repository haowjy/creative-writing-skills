"""EPUB text-return patches retain unrelated archive members byte-for-byte."""
from copy import copy
from datetime import datetime, timezone
from difflib import SequenceMatcher
from io import BytesIO
import re
from zipfile import ZipFile

from .conversion import render
from .epub_conversion import xml, member_path
from .html_return import patch_html
from .index import Diagnostic


def conflict(reason):
    raise Diagnostic('epub_return_conflict', reason, 'Review the original package and remote edits; no original replacement occurred.')


def patch_epub(source: bytes, baseline_text: str, remote_text: str, *, modified: str | None = None) -> bytes:
    original = render(source,'epub')  # Validate archive before reading its members.
    if not original.supported or original.text != baseline_text:
        conflict('EPUB reading model does not match its saved baseline.')
    with ZipFile(BytesIO(source)) as archive:
        container = xml(archive.read('META-INF/container.xml'))
        package_path = member_path('container.xml',container.findall('.//{*}rootfile')[0].attrib['full-path'])
        package = xml(archive.read(package_path))
        manifest = {i.attrib['id']:i.attrib for i in package.findall('./{*}manifest/{*}item')}
        members = []
        position = 0
        for ref in package.findall('./{*}spine/{*}itemref'):
            name = member_path(package_path,manifest[ref.attrib['idref']]['href'])
            text = render(archive.read(name),'html').text
            members.append((position,position+len(text),name,text))
            position += len(text)
        edits = {}
        for tag,a,b,c,d in SequenceMatcher(None,baseline_text,remote_text,autojunk=False).get_opcodes():
            if tag == 'equal':
                continue
            owners = [(start,name,text) for start,end,name,text in members if start <= a <= b <= end]
            if len(owners) != 1:
                conflict('Remote changes cross spine resources or ambiguous boundaries.')
            start,name,text = owners[0]
            if baseline_text.count(text) != 1:
                conflict('Repeated spine content has ambiguous correspondence.')
            edits.setdefault(name,[]).append((a-start,b-start,remote_text[c:d]))
        changes = {}
        for _,_,name,text in members:
            if name not in edits:
                continue
            changed = text
            for a,b,value in sorted(edits[name],reverse=True):
                changed = changed[:a]+value+changed[b:]
            changes[name] = patch_html(archive.read(name),text,changed)
        raw_package = archive.read(package_path)
        # Change only the text of the already validated modification metadata.
        pattern = rb'(<(?:[\w.-]+:)?meta\b[^>]*\bproperty=[\"\']dcterms:modified[\"\'][^>]*>)([^<]*)(</(?:[\w.-]+:)?meta\s*>)'
        matches = list(re.finditer(pattern,raw_package))
        if len(matches) != 1:
            conflict('A unique dcterms:modified metadata field is required for safe package update.')
        stamp = modified or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',stamp):
            conflict('Invalid modification timestamp.')
        match = matches[0]
        changes[package_path] = raw_package[:match.start(2)]+stamp.encode()+raw_package[match.end(2):]
        target = BytesIO()
        with ZipFile(target,'w') as output:
            output.comment = archive.comment
            for entry in archive.infolist():
                # ZipFile mutates ZipInfo offsets and sizes while writing. Never
                # reuse the input archive's records: later read-back needs them.
                output.writestr(copy(entry),changes.get(entry.filename,archive.read(entry.filename)))
        result = target.getvalue()
        verified = render(result,'epub')
        if not verified.supported or verified.text != remote_text:
            conflict('Patched package failed readable-content verification.')
        with ZipFile(BytesIO(result)) as check:
            for name in archive.namelist():
                if name not in changes and check.read(name) != archive.read(name):
                    conflict('An unrelated package resource changed.')
        return result
