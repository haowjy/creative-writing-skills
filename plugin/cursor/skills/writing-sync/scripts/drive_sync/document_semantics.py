"""Pure document content fingerprints and inherited settings identity."""
import json
from hashlib import sha256
from .conversion import utf16
from .google import fingerprint


def semantic(text, styles):
    """Hash legacy style coverage without allocating a set per UTF-16 unit.

    The serialized bytes intentionally match the original fingerprint schema:
    changing them would strand pending journals. Merge intervals, then stream
    their integer coverage in bounded chunks instead of materializing that list.
    """
    spans = {}
    limit = 1 + utf16(text)
    for style in styles:
        end = min(style.end, limit)
        if style.start < end:
            spans.setdefault((style.kind, style.value), []).append((style.start, end))
    hasher = sha256()
    def emit(value):
        hasher.update(value.encode())
    encode = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'))
    emit('{"styles":[')
    first_style = True
    for key, intervals in sorted(spans.items()):
        merged = []
        for start, end in sorted(intervals):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        if not first_style:
            emit(',')
        first_style = False
        emit('[' + encode(key) + ',[')
        first_position = True
        for start, end in merged:
            for chunk_start in range(start, end, 4096):
                if not first_position:
                    emit(',')
                first_position = False
                emit(','.join(str(n) for n in range(chunk_start, min(chunk_start + 4096, end))))
        emit(']]')
    emit('],"text":' + encode(text) + '}')
    return hasher.hexdigest()


def document_settings(document):
    tabs=document.get('tabs',[])
    tab=tabs[0].get('documentTab',{}) if tabs else {}
    return fingerprint(dict(documentStyle=document.get('documentStyle',{}),namedStyles=document.get('namedStyles',{}),
                            tabNamedStyles=tab.get('namedStyles',{}),lists=tab.get('lists',{})))


