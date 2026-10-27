"""Representative supported HTML/XHTML styles; synthetic fixtures only."""
from copy import copy
from dataclasses import asdict
from io import BytesIO
from pathlib import Path
import uuid
from zipfile import ZipFile

from drive_sync.application import preview_sync, combined_plan
from drive_sync.conversion import render
from drive_sync.document_model import read_document
from drive_sync.google import DOC
from drive_sync.native_effects import semantic
from drive_sync.state import write_json
from drive_sync.storage import Draft, commit
from test_epub import book
from test_index import fixture


def styled_sources():
    body = ('<h1>Chapter one</h1><p id="intro">First <strong>bold</strong> and '
            '<em>quiet</em> words. <a href="https://example.com/">Reference</a>.</p>'
            '<ul><li>Alpha item</li><li>Beta item</li></ul><!-- retained craft note -->')
    html = ('<!DOCTYPE html>\r\n<html><head><title>Protected title</title></head><body>'
            + body + '</body></html>').encode()
    result = BytesIO()
    with ZipFile(BytesIO(book())) as source, ZipFile(result, 'w') as target:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename == 'OEBPS/z.xhtml':
                data = data.replace(b'<p>First</p>', body.encode())
            target.writestr(copy(entry), data)
    return {'styled.html': html, 'styled.epub': result.getvalue()}


def seed_styled(run):
    sources = styled_sources()
    for name, data in sources.items():
        model = render(data, 'epub' if name.endswith('.epub') else 'html')
        assert model.supported, model.findings
        assert {'heading', 'strong', 'em', 'link', 'bullet'} <= {s.kind for s in model.styles}, model.styles
    run.mkdir(mode=0o700)
    (run / 'notes').mkdir()
    for name, data in sources.items():
        (run / 'notes' / name).write_bytes(data)
    raw = fixture()
    raw['id'] = str(uuid.uuid4())
    raw['roots']['notes']['destination_name'] = 'Drive Sync styled disposable ' + raw['id']
    commit(run / 'index.yaml', Draft(raw), None)


def verify_styled(run, remote):
    before = styled_sources()
    html = (run / 'notes/styled.html').read_bytes()
    assert html == before['styled.html'].replace(b'<strong>bold</strong>', b'<strong>brave</strong>')
    with ZipFile(BytesIO(before['styled.epub'])) as original, ZipFile(run / 'notes/styled.epub') as returned:
        assert original.namelist() == returned.namelist()
        changed = [name for name in original.namelist() if original.read(name) != returned.read(name)]
        assert set(changed) == {'OEBPS/z.xhtml', 'OEBPS/book.opf'}, changed
        assert returned.read('OEBPS/z.xhtml') == original.read('OEBPS/z.xhtml').replace(b'<strong>bold</strong>', b'<strong>brave</strong>')
    inventory = remote.inventory()
    docs = [m for m in inventory if m['mimeType'] == DOC]
    assert len(inventory) == 3 and {m['name'] for m in docs} == set(before)
    evidence = []
    for item in docs:
        model = read_document(remote.observe_document(item['id']))
        local = render((run / 'notes' / item['name']).read_bytes(), 'epub' if item['name'].endswith('.epub') else 'html')
        assert local.supported and semantic(model.text, model.styles) == semantic(local.text, local.styles)
        evidence.append(dict(name=item['name'], remote_id=item['id'], text=model.text, styles=[asdict(s) for s in model.styles]))
    final = combined_plan(preview_sync(run / 'index.yaml', remote, home=run / 'state'))
    assert len(final.operations) == 3 and all(o.direction == 'noop' for o in final.operations)
    write_json(run / 'styled-verification.json', dict(verified=True, files=evidence,
               changed_epub_members=changed, html_exact_bytes=True, final_plan=asdict(final)))
    print('PASS: styled HTML/EPUB word edits returned with markup/members retained; remote styles match; all no-op.')
