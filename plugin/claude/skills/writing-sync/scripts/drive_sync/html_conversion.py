"""Non-executing HTML reader with explicit formatting/asset capability findings."""
from html.parser import HTMLParser
import re
from .conversion import Finding, Rendering, Style, utf16
from .index import Diagnostic


class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self.styles = []
        self.findings = []
        self.stack = []
        self.position = 1
        self.hidden = 0
        self.lists = []

    def finding(self, code, reason):
        item = Finding(code, reason, 'Review this structure before enabling conversion; do not silently discard it.')
        if item not in self.findings:
            self.findings.append(item)

    def append(self, text):
        if text:
            self.output.append(text)
            self.position += utf16(text)

    def newline(self):
        if self.output and not self.output[-1].endswith('\n'):
            self.append('\n')

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'):
            self.finding('html_active_or_css', 'Scripts or stylesheet content cannot be represented safely in Docs.')
        if tag in ('head', 'script', 'style'):
            self.hidden += 1
        if tag in ('p', 'div', 'section', 'article', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'pre'):
            self.newline()
        if tag in ('ul', 'ol'):
            self.lists.append(tag)
            if len(self.lists) > 1:
                self.finding('html_nested_list', 'Nested HTML lists need indentation support.')
        if tag == 'br':
            self.append('\n')
            return
        if tag in ('meta', 'link'):
            if tag == 'link':
                self.finding('html_external_resource', 'Linked resources are not fetched.')
            return
        if tag in ('img', 'hr', 'input', 'source'):
            self.finding('html_asset', f'HTML {tag} requires an asset or layout adapter.')
            return
        allowed = {'html','body','head','title','p','div','section','article','span','strong','b','em','i','code','pre','a','ul','ol','li','h1','h2','h3','h4','h5','h6','script','style'}
        if tag not in allowed:
            self.finding('html_structure', f'HTML {tag} is not yet represented by the readable model.')
        # IDs and namespace declarations survive in the original source.
        # Unrepresented reading-order/numbering/visibility attributes must not
        # silently pass a conversion capability check.
        safe_attrs = {'id', 'xmlns', 'xmlns:epub'}
        if tag == 'a':
            safe_attrs |= {'href', 'title'}
        if any(k not in safe_attrs for k in attrs):
            self.finding('html_presentation', 'HTML attributes affecting presentation or semantics require explicit fidelity review.')
        if tag == 'a' and not (attrs.get('href') or '').startswith(('https://', 'http://', 'mailto:')):
            self.finding('link_mapping_required', 'Local HTML links require reversible destination provenance.')
        self.stack.append((tag, self.position, attrs))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1][0] == tag:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1][0] != tag:
            self.finding('html_unbalanced', 'HTML uses implicit or mismatched element closures.')
            return
        _, start, attrs = self.stack.pop()
        if tag in ('head', 'script', 'style'):
            self.hidden -= 1
        kind = {'strong':'strong','b':'strong','em':'em','i':'em','code':'code','pre':'code','a':'link'}.get(tag)
        value = attrs.get('href', '') if kind == 'link' else ''
        if tag in ('h1','h2','h3','h4','h5','h6'):
            kind, value = 'heading', tag[1:]
        if tag == 'li' and self.lists:
            kind = 'bullet' if self.lists[-1] == 'ul' else 'number'
        if tag in ('p','div','section','article','li','pre','h1','h2','h3','h4','h5','h6'):
            self.newline()
        if kind and self.position > start:
            self.styles.append(Style(start, self.position, kind, value))
        if tag in ('ul', 'ol') and self.lists:
            self.lists.pop()

    def handle_data(self, text):
        if self.hidden:
            return
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        if not any(tag == 'pre' for tag, _, _ in self.stack):
            # Unicode spaces are not collapsible document whitespace.
            # https://www.w3.org/TR/css-text-3/#white-space-processing
            text = re.sub(r'[ \t\n\f]+', ' ', text)
            if not self.output or self.output[-1].endswith(('\n', ' ')):
                text = text.lstrip(' ')
        self.append(text)


def render_html(data: bytes) -> Rendering:
    try:
        text = data.decode('utf-8')
        if '\x00' in text:
            raise ValueError()
    except (ValueError, UnicodeError):
        raise Diagnostic('invalid_html', 'HTML must be UTF-8 without NUL.', 'Correct the source encoding.') from None
    reader = Reader()
    reader.feed(text)
    reader.close()
    if reader.stack:
        reader.finding('html_unbalanced', 'HTML has unclosed elements.')
    return Rendering('html', ''.join(reader.output), tuple(reader.styles), tuple(reader.findings))
