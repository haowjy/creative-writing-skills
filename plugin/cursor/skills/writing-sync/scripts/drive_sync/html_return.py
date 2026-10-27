"""Literal HTML source patches; tags, attributes, comments and entities stay intact."""
from html.parser import HTMLParser
from html import escape
from difflib import SequenceMatcher
from dataclasses import dataclass
import re

from .conversion import render
from .index import Diagnostic


def conflict(reason):
    raise Diagnostic('html_return_conflict', reason, 'Review the original and remote text; no source replacement was performed.')


@dataclass(frozen=True)
class TextRun:
    start: int
    end: int
    text: str


def runs(data: bytes):
    text = data.decode('utf-8')
    # HTMLParser positions count LF only, not str.splitlines() boundaries
    # such as bare CR, vertical tab or Unicode paragraph separators.
    offsets = [0] + [index + 1 for index, char in enumerate(text) if char == '\n']
    result = []
    class Parser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.hidden = 0
            self.last_character = 0
            self.last_byte = 0
        def handle_starttag(self, tag, attrs):
            if tag in ('head','style','script'):
                self.hidden += 1
        def handle_endtag(self, tag):
            if tag in ('head','style','script'):
                self.hidden -= 1
        def handle_data(self, value):
            if self.hidden or not value.strip():
                return
            line, col = self.getpos()
            start = offsets[line - 1] + col
            if text[start:start+len(value)] != value:
                conflict('Parser/source position mismatch.')
            byte_start = self.last_byte + len(text[self.last_character:start].encode())
            self.last_character, self.last_byte = start, byte_start
            result.append(TextRun(byte_start, byte_start + len(value.encode()), value))
    parser = Parser()
    parser.feed(text)
    parser.close()
    return tuple(result)


def mapped_runs(source: bytes, baseline_text: str):
    """Map literal runs, or words inside a uniquely located collapsed run.

    Collapsible whitespace remains source-owned: fallback mappings cover only
    nonwhitespace spans, never an indentation or original line-ending sequence.
    """
    mapped = []
    for run in runs(source):
        if baseline_text.count(run.text) == 1:
            start = baseline_text.index(run.text)
            mapped.append((start, start + len(run.text), run))
            continue
        collapsed = re.sub(r'[ \t\r\n\f]+', ' ', run.text)
        candidates = {value for value in (collapsed, collapsed.lstrip(' '))
                      if value and baseline_text.count(value) == 1}
        # Prefer the full rendered run; leading whitespace is suppressed at
        # paragraph starts by the forward HTML reader.
        normalized = collapsed if collapsed in candidates else next(iter(candidates), None)
        if normalized is None:
            continue
        start = baseline_text.index(normalized)
        cursor = 0 if not normalized.startswith(' ') else 1
        previous_char, previous_byte = 0, run.start
        for word in re.finditer(r'[^ \t\r\n\f]+', run.text):
            byte_start = previous_byte + len(run.text[previous_char:word.start()].encode())
            value = word.group()
            mapped.append((start + cursor, start + cursor + len(value),
                           TextRun(byte_start, byte_start + len(value.encode()), value)))
            cursor += len(value) + 1
            previous_char, previous_byte = word.start(), byte_start
    return mapped


def patch_html(source: bytes, baseline_text: str, remote_text: str) -> bytes:
    original = render(source,'html')
    if not original.supported or original.text != baseline_text:
        conflict('HTML rendering does not match the saved baseline.')
    mapped = mapped_runs(source, baseline_text)
    edits = {}
    for tag,a,b,c,d in SequenceMatcher(None,baseline_text,remote_text,autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        owners = [(start,run) for start,end,run in mapped if start <= a <= b <= end]
        if len(owners) != 1:
            conflict('Edit crosses an entity, tag or ambiguous text run.')
        start,run = owners[0]
        edits.setdefault(run,[]).append((a-start,b-start,remote_text[c:d]))
    ordered = sorted(edits,key=lambda r:r.start)
    for left,right in zip(ordered,ordered[1:]):
        if b'<!--' in source[left.end:right.start]:
            conflict('Changes span a protected HTML comment.')
    result = source
    for run in reversed(ordered):
        value = run.text
        for a,b,new in sorted(edits[run],reverse=True):
            value = value[:a]+new+value[b:]
        result = result[:run.start]+escape(value,quote=False).encode()+result[run.end:]
    verified = render(result,'html')
    if not verified.supported or verified.text != remote_text:
        conflict('Patched HTML does not reproduce the desired readable text.')
    return result
