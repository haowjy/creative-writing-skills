"""Canonical supported Google document content, excluding volatile revision data."""
from dataclasses import dataclass
from .conversion import Rendering, Style, utf16
from .google import DocumentObservation, fingerprint
from .index import Diagnostic
from .planner import RemoteSnapshot

LINK_COLOR = {'color': {'rgbColor': {'red': 0.06666667, 'green': 0.33333334, 'blue': 0.8}}}
LIST_INDENTS = {'indentFirstLine': {'magnitude': 18, 'unit': 'PT'},
                'indentStart': {'magnitude': 36, 'unit': 'PT'}}
# Exact transparent, zero-width/padding defaults observed on HTML imports.
# Keep nondefault fields protected, and retain raw values in snapshot hashes.
IMPORT_BORDER = {'color': {}, 'dashStyle': 'SOLID',
                 'padding': {'unit': 'PT'}, 'width': {'unit': 'PT'}}
IMPORT_BORDERS = frozenset(('borderBetween', 'borderBottom', 'borderLeft', 'borderRight', 'borderTop'))


@dataclass(frozen=True)
class DocumentModel:
    text: str
    styles: tuple[Style, ...]
    tab_id: str
    end_index: int
    snapshot: RemoteSnapshot


def reject(reason):
    raise Diagnostic('unsupported_remote_structure', reason,
                     'Review the Google document; do not flatten unsupported content or discard extra tabs.')


def read_document(observation: DocumentObservation) -> DocumentModel:
    document = observation.document
    tabs = document.get('tabs', [])
    if len(tabs) != 1 or tabs[0].get('childTabs'):
        reject('Exactly one content tab is required.')
    tab = tabs[0]
    tab_id = tab.get('documentTab', {})
    if any(tab_id.get(k) for k in ('headers', 'footers', 'footnotes', 'positionedObjects', 'inlineObjects')):
        reject('Headers, footnotes or embedded objects require dedicated conversion support.')
    content = tab_id.get('body', {}).get('content', [])
    text_parts = []
    cursor = 1
    styles = []
    for block in content:
        if 'sectionBreak' in block:
            if block.get('startIndex', 0) != 0:
                reject('Additional section breaks cannot be represented.')
            continue
        paragraph = block.get('paragraph')
        if paragraph is None:
            reject('Nonparagraph document structures require a dedicated adapter.')
        for element in paragraph.get('elements', []):
            run = element.get('textRun')
            if run is None:
                reject('A paragraph contains a nontext element.')
            start = element.get('startIndex')
            value = run.get('content', '')
            end = element.get('endIndex')
            if start != cursor or end != start + utf16(value):
                reject('Document text indices are discontinuous.')
            text_parts.append(value)
            cursor = end
            style = run.get('textStyle', {})
            # Observed automatic decoration of links created by updateTextStyle.
            # Match the whole default pair; never discard arbitrary link colors.
            default_link = (set(style.get('link', {})) == {'url'}
                            and style.get('underline') is True
                            and style.get('foregroundColor') == LINK_COLOR)
            emphasis_end = end - 1 if value.endswith('\n') else end
            for field, kind in (('bold', 'strong'), ('italic', 'em')):
                if style.get(field):
                    styles.append(Style(start, emphasis_end, kind))
            for field in ('underline', 'strikethrough', 'smallCaps'):
                if field == 'underline' and default_link:
                    continue
                if style.get(field):
                    styles.append(Style(start, end, 'unrepresentable', field))
            if style.get('baselineOffset', 'NORMAL') != 'NORMAL':
                styles.append(Style(start, end, 'unrepresentable', 'baselineOffset'))
            family = style.get('weightedFontFamily', {}).get('fontFamily')
            if family in ('Courier New', 'monospace'):
                styles.append(Style(start, end, 'code'))
            supported_fields={'bold','italic','link','weightedFontFamily','underline','strikethrough','smallCaps','baselineOffset'}
            for field,value in style.items():
                if field == 'foregroundColor' and default_link:
                    continue
                if field not in supported_fields:
                    styles.append(Style(start,end,'unrepresentable',field+':'+fingerprint(value)))
            if family and family not in ('Courier New','monospace'):
                styles.append(Style(start,end,'unrepresentable','font:'+family))
            link = style.get('link')
            if link:
                if style.get('underline') is False:
                    styles.append(Style(start, end, 'unrepresentable', 'link-underline-disabled'))
                if set(link) != {'url'}:
                    reject('An internal Google link lacks local-source provenance.')
                styles.append(Style(start, end, 'link', link['url']))
        pstyle = paragraph.get('paragraphStyle', {})
        named = pstyle.get('namedStyleType', 'NORMAL_TEXT')
        # ParagraphStyle inherits fields from named styles. Only heading identity
        # and named style type are represented here; explicit layout fields must
        # not disappear during a source-format return.
        # https://developers.google.com/workspace/docs/api/reference/rest/v1/documents#ParagraphStyle
        for field, value in pstyle.items():
            if field in IMPORT_BORDERS and value == IMPORT_BORDER:
                continue
            if field == 'shading' and value == {'backgroundColor': {}}:
                continue
            # Docs returns this explicit default even for a new empty Doc;
            # direction does not inherit (unlike alignment/spacing fields).
            if field == 'direction' and value == 'LEFT_TO_RIGHT':
                continue
            if (paragraph.get('bullet') and paragraph['bullet'].get('nestingLevel', 0) == 0
                    and field in LIST_INDENTS and value == LIST_INDENTS[field]):
                continue
            if field not in ('headingId', 'namedStyleType'):
                styles.append(Style(block['startIndex'], block['endIndex'],
                                    'unrepresentable', 'paragraph:' + field + ':' + fingerprint(value)))
        if paragraph.get('bullet'):
            bullet = paragraph['bullet']
            levels = tab_id.get('lists', {}).get(bullet.get('listId'), {}).get('listProperties', {}).get('nestingLevels', [])
            level = bullet.get('nestingLevel', 0)
            if level != 0 or not levels:
                reject('Nested or unknown list formatting requires a dedicated adapter.')
            glyph = levels[0].get('glyphType', 'GLYPH_TYPE_UNSPECIFIED')
            level_style = levels[0]
            for field, value in level_style.items():
                defaults = dict(LIST_INDENTS, bulletAlignment='START', textStyle={'underline': False})
                if field in defaults and value != defaults[field]:
                    styles.append(Style(block['startIndex'], block['endIndex'],
                                        'unrepresentable', 'list-style:' + field + ':' + fingerprint(value)))
            if glyph == 'GLYPH_TYPE_UNSPECIFIED' and (
                    level_style.get('glyphSymbol', '\u25cf') != '\u25cf'
                    or level_style.get('glyphFormat', '%0') != '%0'):
                styles.append(Style(block['startIndex'], block['endIndex'],
                                    'unrepresentable', 'list-symbol:' + fingerprint(level_style)))
            kind = 'number' if glyph == 'DECIMAL' else 'bullet'
            if glyph not in ('DECIMAL', 'GLYPH_TYPE_UNSPECIFIED'):
                styles.append(Style(block['startIndex'], block['endIndex'],
                                    'unrepresentable', 'list-glyph:' + glyph))
            if glyph == 'DECIMAL' and (levels[0].get('startNumber', 1) != 1
                                      or levels[0].get('glyphFormat', '%0.') != '%0.'):
                styles.append(Style(block['startIndex'], block['endIndex'],
                                    'unrepresentable', 'list-numbering:' + fingerprint(levels[0])))
            styles.append(Style(block['startIndex'], block['endIndex'], kind))
        if named not in ('NORMAL_TEXT', 'HEADING_1', 'HEADING_2', 'HEADING_3', 'HEADING_4', 'HEADING_5', 'HEADING_6'):
            styles.append(Style(block['startIndex'], block['endIndex'], 'unrepresentable', named))
        if named.startswith('HEADING_'):
            styles.append(Style(block['startIndex'], block['endIndex'], 'heading', named.removeprefix('HEADING_')))
    text = ''.join(text_parts)
    if not content or not text.endswith('\n'):
        reject('Document lacks a final paragraph boundary.')
    # One final LF belongs to the Docs container; the inserted source LF, if any,
    # is the preceding character. Never strip all trailing whitespace.
    text = text[:-1]
    metadata = observation.metadata
    # Keep all relevant style fields for remote-change detection, including styles
    # not yet expressible in Rendering. Never treat unmodeled formatting as absent.
    canonical = dict(body=tab_id.get('body'), lists=tab_id.get('lists', {}),
                     namedStyles=tab_id.get('namedStyles', {}), rootNamedStyles=document.get('namedStyles',{}), documentStyle=document.get('documentStyle', {}))
    snapshot = RemoteSnapshot(metadata['id'], fingerprint(canonical),
        fingerprint(dict(name=metadata.get('name'), parents=metadata.get('parents', []), tab=tab.get('tabProperties'))),
        observation.revision, True, bool(observation.comments), observation.suggestions, 1)
    return DocumentModel(text, tuple(styles), tab['tabProperties']['tabId'], content[-1]['endIndex'], snapshot)
