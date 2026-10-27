"""Format-aware readable model with explicit unsupported-subset findings."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from markdown_it import MarkdownIt
from ruamel.yaml import YAML

from .index import Diagnostic


def comment_only(text: str) -> bool:
    remaining = text.strip()
    found = False
    while remaining:
        if not remaining.startswith('<!--'):
            return False
        end = remaining.find('-->', 4)
        if end < 0:
            return False
        found = True
        remaining = remaining[end + 3:].strip()
    return found


def utf16(text: str) -> int:
    return len(text.encode('utf-16-le')) // 2


@dataclass(frozen=True)
class Style:
    start: int
    end: int
    kind: str
    value: str = ''


@dataclass(frozen=True)
class Finding:
    code: str
    reason: str
    action: str


@dataclass(frozen=True)
class Rendering:
    format: str
    text: str
    styles: tuple[Style, ...]
    findings: tuple[Finding, ...] = ()
    source_prefix: str = ''
    version: str = '1'

    @property
    def fingerprint(self):
        return sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()

    @property
    def supported(self):
        return not self.findings


def render(data: bytes, format: str) -> Rendering:
    from .conversion_process import _IN_WORKER, execute
    if not _IN_WORKER:
        from base64 import b64encode
        result = execute('render', {'data': b64encode(data).decode('ascii'), 'format': format})
        return Rendering(result['format'], result['text'], tuple(Style(**s) for s in result['styles']),
                         tuple(Finding(**f) for f in result['findings']), result['source_prefix'], result['version'])
    if format == 'epub':
        from .epub_conversion import render_epub
        return render_epub(data)
    if format == 'html':
        from .html_conversion import render_html
        return render_html(data)
    if format not in ('markdown', 'text'):
        return Rendering(format, '', (), (Finding('converter_pending', f'{format} converter has not passed its capability gate.', 'Use original storage until this format implementation is available.'),))
    try:
        text = data.decode('utf-8')
        if '\x00' in text:
            raise ValueError()
    except (ValueError, UnicodeError):
        raise Diagnostic('invalid_text', 'Expected UTF-8 text without NUL.', 'Correct the encoding or use original storage.') from None
    if format == 'text':
        return Rendering(format, text.replace('\r\n', '\n').replace('\r', '\n'), ())
    prefix = ''
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == '---':
        end = next((i for i in range(1, len(lines)) if lines[i].strip() in ('---', '...')), None)
        if end is None:
            raise Diagnostic('invalid_frontmatter', 'Frontmatter is unclosed.', 'Close the leading YAML mapping.')
        try:
            value = YAML(typ='safe').load(''.join(lines[1:end]))
            if not isinstance(value, dict):
                raise ValueError()
        except Exception:
            raise Diagnostic('invalid_frontmatter', 'Frontmatter must be a safe YAML mapping.', 'Repair frontmatter before conversion.') from None
        prefix, text = ''.join(lines[:end + 1]), ''.join(lines[end + 1:])
    parser = MarkdownIt('commonmark').enable('table')
    tokens = parser.parse(text)
    output: list[str] = []
    styles: list[Style] = []
    findings: list[Finding] = []
    position = 1  # Google Docs UTF-16 body indices start at 1.
    block_start = 1
    list_stack: list[str] = []
    def append(value):
        nonlocal position
        output.append(value)
        position += utf16(value)
    def unsupported(code, reason, action):
        item = Finding(code, reason, action)
        if item not in findings:
            findings.append(item)
    def inline(children):
        stack: list[tuple[str, int, str]] = []
        for token in children or []:
            kind = token.type
            if kind == 'text':
                append(token.content)
            elif kind in ('softbreak', 'hardbreak'):
                append('\n')
            elif kind in ('em_open', 'strong_open', 'link_open'):
                value = token.attrGet('href') or ''
                stack.append((kind[:-5], position, value))
                if kind == 'link_open' and not value.startswith(('https://', 'http://', 'mailto:')):
                    unsupported('link_mapping_required', 'A local or fragment link needs destination provenance.', 'Resolve the selected target binding before applying conversion.')
            elif kind in ('em_close', 'strong_close', 'link_close'):
                style, start, value = stack.pop()
                styles.append(Style(start, position, style, value))
            elif kind == 'code_inline':
                start = position
                append(token.content)
                styles.append(Style(start, position, 'code'))
            elif kind == 'html_inline' and comment_only(token.content):
                pass
            else:
                unsupported('unsupported_inline', f'Inline element {kind} requires a supported renderer.', 'Review this element; do not silently discard it.')
    for token in tokens:
        kind = token.type
        if kind in ('heading_open', 'paragraph_open'):
            block_start = position
        elif kind == 'inline':
            inline(token.children)
        elif kind in ('paragraph_close', 'heading_close'):
            append('\n')
            if kind == 'heading_close':
                styles.append(Style(block_start, position, 'heading', token.tag[1:]))
        elif kind in ('bullet_list_open', 'ordered_list_open'):
            list_stack.append('bullet' if kind == 'bullet_list_open' else 'number')
        elif kind in ('bullet_list_close', 'ordered_list_close'):
            list_stack.pop()
        elif kind == 'list_item_open':
            block_start = position
            if len(list_stack) > 1:
                unsupported('nested_list_pending', 'Nested list indentation is not rendered yet.', 'Review the list; conversion cannot be applied yet.')
        elif kind == 'list_item_close':
            styles.append(Style(block_start, position, list_stack[-1]))
        elif kind in ('fence', 'code_block'):
            start = position
            append(token.content)
            if not token.content.endswith('\n'):
                append('\n')
            styles.append(Style(start, position, 'code'))
        elif kind == 'html_block' and comment_only(token.content):
            pass
        else:
            unsupported('unsupported_block', f'Block element {kind} requires a supported renderer.', 'Review this element; conversion cannot be applied until supported.')
    return Rendering(format, ''.join(output), tuple(styles), tuple(findings), prefix)


def docs_requests(rendering: Rendering, *, tab_id: str, revision: str, old_end: int) -> dict:
    """Build one revision-guarded batch; caller enforces size and annotations."""
    if not rendering.supported:
        raise Diagnostic('conversion_blocked', 'Rendering contains unresolved findings.', 'Review conversion diagnostics before applying.')
    if not revision or not tab_id or old_end < 2:
        raise Diagnostic('invalid_observation', 'Missing revision, tab or body boundary.', 'Read a fresh complete Google document.')
    requests = []
    if old_end > 2:
        requests.append({'deleteContentRange': {'range': {'tabId': tab_id, 'startIndex': 1, 'endIndex': old_end - 1}}})
    if rendering.text:
        requests.append({'insertText': {'location': {'tabId': tab_id, 'index': 1}, 'text': rendering.text}})
    if rendering.text:
        whole = dict(tabId=tab_id, startIndex=1, endIndex=1 + utf16(rendering.text))
        requests.extend([
            {'deleteParagraphBullets': {'range': whole}},
            {'updateParagraphStyle': {'range': whole, 'paragraphStyle': {'namedStyleType':'NORMAL_TEXT'}, 'fields':'namedStyleType'}},
            {'updateTextStyle': {'range': whole, 'textStyle': {}, 'fields':'*'}},
        ])
    for style in rendering.styles:
        if style.start == style.end:
            continue
        range = dict(tabId=tab_id, startIndex=style.start, endIndex=style.end)
        if style.kind == 'heading':
            requests.append({'updateParagraphStyle': {'range': range, 'paragraphStyle': {'namedStyleType': 'HEADING_' + style.value}, 'fields': 'namedStyleType'}})
        elif style.kind in ('bullet', 'number'):
            requests.append({'createParagraphBullets': {'range': range, 'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE' if style.kind == 'bullet' else 'NUMBERED_DECIMAL_ALPHA_ROMAN'}})
        else:
            value = {'em': {'italic': True}, 'strong': {'bold': True}, 'code': {'weightedFontFamily': {'fontFamily': 'Courier New'}}, 'link': {'link': {'url': style.value}}}[style.kind]
            requests.append({'updateTextStyle': {'range': range, 'textStyle': value, 'fields': ','.join(value)}})
    return {'writeControl': {'requiredRevisionId': revision}, 'requests': requests}
