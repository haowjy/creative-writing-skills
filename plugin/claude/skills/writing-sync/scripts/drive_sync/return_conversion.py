"""Original-source return candidates, validated by a forward render.

Remote edits are compared with the saved remote baseline. Supported Markdown
changes patch exact source byte runs; hidden comments/frontmatter are not rebuilt
from a Google export. Ambiguous or structural edits require explicit review.
"""
from __future__ import annotations
from dataclasses import dataclass
from difflib import SequenceMatcher
import re
from markdown_it import MarkdownIt

from .conversion import render
from .index import Diagnostic
from .storage import digest


@dataclass(frozen=True)
class Candidate:
    data: bytes
    source_hash: str
    candidate_hash: str
    changed_runs: int


def conflict(reason):
    raise Diagnostic('return_mapping_conflict', reason,
                     'Review local/base/remote versions and reconcile manually; the original was not replaced.')


@dataclass(frozen=True)
class Run:
    start: int
    end: int
    text: str


def plain_runs(source: bytes) -> tuple[Run, ...]:
    """Uniquely located literal inline runs; markup remains outside the patches."""
    rendering = render(source, 'markdown')
    text = source.decode('utf-8')
    prefix = rendering.source_prefix
    body = text[len(prefix):]
    base = len(prefix.encode())
    # Match markdown-it's CR/LF normalization while retaining source byte
    # positions. Unicode separators are content, not parser line boundaries.
    offsets = [base] + [base + match.end() for match in re.finditer(rb'\r\n?|\n', source[base:])]
    if offsets[-1] != len(source):
        offsets.append(len(source))
    tokens = MarkdownIt('commonmark').parse(body)
    runs = []
    containers = []
    for i, token in enumerate(tokens):
        if token.nesting == 1:
            containers.append(token.type)
        elif token.nesting == -1:
            containers.pop()
        if token.type != 'inline' or i == 0 or tokens[i-1].type not in ('paragraph_open', 'heading_open'):
            continue
        allowed = {'text','html_inline','em_open','em_close','strong_open','strong_close',
                   'link_open','link_close','code_inline'}
        if any(c.type not in allowed for c in token.children or []):
            continue
        start, end = token.map
        region = source[offsets[start]:offsets[end]].rstrip(b'\r\n')
        if tokens[i-1].type == 'heading_open' or containers.count('list_item_open') == 1:
            # The AST identified heading/list syntax. Only map a unique
            # literal content span inside it, never its delimiters or indent.
            if not token.content or region.count(token.content.encode()) != 1:
                continue
        elif region.decode() != token.content:
            continue
        for child in token.children or []:
            if child.type not in ('text','code_inline') or not child.content:
                continue
            raw = child.content.encode()
            if region.count(raw) != 1:
                continue
            relative = region.index(raw)
            if relative and region[relative - 1:relative] == b'\\':
                continue
            cursor = offsets[start] + relative
            runs.append(Run(cursor, cursor + len(raw), child.content))
    return tuple(runs)


def return_candidate(source: bytes, *, expected_source_hash: str, format: str,
                     baseline_text: str, remote_text: str) -> Candidate:
    from .conversion_process import _IN_WORKER, execute
    if not _IN_WORKER:
        from base64 import b64encode, b64decode
        result = execute('return', dict(source=b64encode(source).decode('ascii'),
                         expected_source_hash=expected_source_hash, format=format,
                         baseline_text=baseline_text, remote_text=remote_text))
        return Candidate(b64decode(result['data'], validate=True), result['source_hash'],
                         result['candidate_hash'], result['changed_runs'])
    if digest(source) != expected_source_hash:
        conflict('Local source changed after the baseline snapshot.')
    original = render(source, format)
    if not original.supported:
        conflict('The source contains unsupported conversion structures.')
    if original.text != baseline_text:
        conflict('Saved remote text does not correspond to this source rendering.')
    if remote_text == baseline_text:
        return Candidate(source, expected_source_hash, expected_source_hash, 0)
    if format == 'text':
        # Preserve a uniform original newline convention; mixed forms need review.
        text = source.decode('utf-8')
        if '\r' in text.replace('\r\n', '') or ('\r\n' in text and '\n' in text.replace('\r\n', '')):
            conflict('Mixed or unsupported source newline conventions.')
        candidate = remote_text.replace('\n', '\r\n').encode() if '\r\n' in text else remote_text.encode()
        render(candidate, 'text')  # Encoding and control-character validation.
        return Candidate(candidate, expected_source_hash, digest(candidate), 1)
    if format == 'epub':
        from .epub_return import patch_epub
        candidate = patch_epub(source, baseline_text, remote_text)
        return Candidate(candidate, expected_source_hash, digest(candidate), 1)
    if format == 'html':
        from .html_return import patch_html
        candidate = patch_html(source, baseline_text, remote_text)
        return Candidate(candidate, expected_source_hash, digest(candidate), 1)
    if format != 'markdown':
        conflict('This format needs its own source-preserving patcher.')
    mapped = []
    for run in plain_runs(source):
        # Refuse ambiguous repeated text rather than choosing a convenient match.
        if baseline_text.count(run.text) != 1:
            continue
        start = baseline_text.index(run.text)
        mapped.append((start, start + len(run.text), run))
    edits = {}
    for tag, a, b, c, d in SequenceMatcher(None, baseline_text, remote_text, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        owners = [(start, end, run) for start, end, run in mapped if start <= a <= b <= end]
        if len(owners) != 1:
            conflict('Remote edit crosses protected source structure or lacks a unique source run.')
        start, end, run = owners[0]
        edits.setdefault(run, []).append((a - start, b - start, remote_text[c:d]))
    ordered = sorted(edits, key=lambda run: run.start)
    for left, right in zip(ordered, ordered[1:]):
        if b'<!--' in source[left.end:right.start]:
            conflict('Edits on both sides of a protected comment have ambiguous correspondence.')
    result = source
    for run in sorted(edits, key=lambda r: r.start, reverse=True):
        replacement = run.text
        for a, b, text in sorted(edits[run], reverse=True):
            replacement = replacement[:a] + text + replacement[b:]
        result = result[:run.start] + replacement.encode() + result[run.end:]
    rendered = render(result, 'markdown')
    if not rendered.supported or rendered.text != remote_text:
        conflict('The return edit changes Markdown syntax or cannot reproduce the Google text.')
    # Reparse patch regions so newly introduced invisible syntax cannot sneak in.
    if len(plain_runs(result)) != len(plain_runs(source)):
        conflict('The return edit changes protected source structure.')
    return Candidate(result, expected_source_hash, digest(result), len(edits))
