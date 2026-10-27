"""Google-only paragraph spacing, separate from source-format semantics.

Raw document snapshots still include these fields for races/conflicts. Only a
new preparation with an explicit overlay may exclude them from content equality.
Legacy journals retain their original, stricter semantic verification.
"""
from copy import deepcopy
from difflib import SequenceMatcher
import math

from .conversion import utf16
from .index import Diagnostic

FIELDS = ('spaceAbove', 'spaceBelow', 'lineSpacing', 'spacingMode')


def fail(reason):
    raise Diagnostic('presentation_mapping_conflict', reason,
        'Review the paragraph changes and Google spacing; no unverified presentation may be discarded.')


def spacing(style):
    result = {}
    for field in FIELDS:
        if field not in style:
            continue
        value = style[field]
        if field == 'spacingMode':
            if value == 'SPACING_MODE_UNSPECIFIED':
                continue
            if value not in ('NEVER_COLLAPSE', 'COLLAPSE_LISTS'):
                fail('Unknown paragraph spacing mode.')
            result[field] = value
            continue
        if field in ('spaceAbove', 'spaceBelow'):
            if (not isinstance(value, dict) or set(value) - {'magnitude', 'unit'}
                    or value.get('unit') != 'PT'):
                fail('Paragraph spacing is not a supported point dimension.')
            value = value.get('magnitude', 0)
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            fail('Invalid paragraph spacing magnitude.')
        result[field] = (dict(magnitude=float(value), unit='PT')
                         if field in ('spaceAbove', 'spaceBelow') else float(value))
    return result


def paragraphs(document):
    tabs = document.get('tabs', [])
    if len(tabs) != 1 or tabs[0].get('childTabs'):
        fail('Presentation mapping requires one content tab.')
    result = []
    for block in tabs[0].get('documentTab', {}).get('body', {}).get('content', []):
        if 'paragraph' not in block:
            continue  # read_document rejects unsupported structures first.
        paragraph = block['paragraph']
        text = ''.join(e.get('textRun', {}).get('content', '') for e in paragraph.get('elements', []))
        result.append(dict(start=block['startIndex'], end=block['endIndex'], text=text,
                           style=spacing(paragraph.get('paragraphStyle', {}))))
    return result


def capture(document):
    return [{k: row[k] for k in ('start', 'end', 'style')} for row in paragraphs(document)]


def content_styles(styles):
    """Only call after capture/map validates the actual spacing values."""
    return tuple(s for s in styles if not (
        s.kind == 'unrepresentable' and any(s.value.startswith('paragraph:' + f + ':') for f in FIELDS)))


def map_spacing(document, desired_text):
    old = paragraphs(document)
    if not any(row['style'] for row in old):
        return None  # Preserve legacy verification/request shape when absent.
    # Split on LF only: Unicode separators are literal prose, not paragraphs.
    new = [line + '\n' for line in (desired_text + '\n').split('\n')[:-1]]
    if len(old) > 2048 or len(new) > 2048:
        fail('Paragraph presentation mapping exceeds the 2048-paragraph bound.')
    if sum(len(r['text']) for r in old) + len(desired_text) > 4_000_000:
        fail('Paragraph presentation mapping exceeds its text bound.')
    old_text = [r['text'] for r in old]
    styles = [r['style'] for r in old]
    if all(s == styles[0] for s in styles):
        mapped = [styles[0]] * len(new)
    else:
        # Repeated identical text with different presentation has no reliable
        # identity after editing. Never silently pick one occurrence's style.
        seen = {}
        for text, style in zip(old_text, styles):
            if text in seen and seen[text] != style and old_text != new:
                fail('Repeated paragraphs have ambiguous presentation identity.')
            seen[text] = style
        mapped = []
        for kind, a, b, c, d in SequenceMatcher(None, old_text, new, autojunk=False).get_opcodes():
            if kind == 'equal':
                mapped.extend(styles[a:b])
            elif kind == 'delete':
                continue
            else:
                candidates = styles[a:b] if kind == 'replace' else styles[max(0, a-1):min(len(styles), a+1)]
                if not candidates or any(s != candidates[0] for s in candidates):
                    fail('Changed paragraphs do not have an unambiguous spacing assignment.')
                mapped.extend([candidates[0]] * (d-c))
    result, cursor = [], 1
    for text, style in zip(new, mapped):
        end = cursor + utf16(text)
        result.append(dict(start=cursor, end=end, style=deepcopy(style)))
        cursor = end
    if len(result) != len(new):
        fail('Incomplete paragraph presentation assignment.')
    return result


def restore_requests(overlay, tab_id):
    if overlay is None:
        return []
    return [{'updateParagraphStyle': {
        'range': dict(tabId=tab_id, startIndex=row['start'], endIndex=row['end']),
        'paragraphStyle': row['style'], 'fields': ','.join(FIELDS)}} for row in overlay]
