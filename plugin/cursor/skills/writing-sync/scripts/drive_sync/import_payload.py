"""Serialize the validated readable model to self-contained import HTML."""
from html import escape
from .conversion import Rendering, utf16
from .index import Diagnostic


def import_html(rendering: Rendering) -> bytes:
    if not rendering.supported:
        raise Diagnostic('conversion_blocked', 'Rendering has unresolved findings.', 'Review conversion check before importing.')
    output = ['<!doctype html><html><head><meta charset="UTF-8"></head><body>']
    offset = 1
    current_list = None
    # Every HTML paragraph acquires a Docs paragraph boundary. Keep the final
    # empty segment as the container's sentinel, rather than consuming a source
    # newline as that sentinel. Only LF separates model paragraphs; Unicode
    # separators and vertical tabs must not be silently split by splitlines().
    lines = rendering.text.split('\n')
    for number, text in enumerate(lines):
        end = offset + utf16(text) + (number < len(lines) - 1)
        paragraph_styles = [s for s in rendering.styles if s.start <= offset < s.end]
        heading = next((s.value for s in paragraph_styles if s.kind == 'heading'), None)
        list_kind = next((s.kind for s in paragraph_styles if s.kind in ('bullet', 'number')), None)
        desired_list = {'bullet':'ul', 'number':'ol'}.get(list_kind)
        if current_list != desired_list:
            if current_list:
                output.append(f'</{current_list}>')
            if desired_list:
                output.append(f'<{desired_list}>')
            current_list = desired_list
        tag = 'li' if current_list else 'h' + heading if heading else 'p'
        if tag not in ('li','p','h1','h2','h3','h4','h5','h6'):
            raise Diagnostic('invalid_heading', 'Heading level is unsupported.', 'Use heading levels one through six.')
        output.append(f'<{tag} style="white-space:pre-wrap">')
        position = offset
        active = []
        for char in text:
            styles = [s for s in rendering.styles if s.kind in ('strong','em','code','link') and s.start <= position < s.end]
            if styles != active:
                for _ in reversed(active):
                    output.append('</span>')
                for style in styles:
                    css = {'strong':'font-weight:bold', 'em':'font-style:italic', 'code':'font-family:monospace', 'link':''}[style.kind]
                    # Links use their own anchor inside a stable span wrapper.
                    output.append(f'<span style="{css}">')
                active = styles
            value = escape(char)
            link = next((s for s in styles if s.kind == 'link'), None)
            if link:
                value = f'<a href="{escape(link.value, quote=True)}">{value}</a>'
            output.append(value)
            position += utf16(char)
        output.extend('</span>' for _ in reversed(active))
        if not text:
            output.append('<br>')
        output.append(f'</{tag}>')
        offset = end
    if current_list:
        output.append(f'</{current_list}>')
    output.append('</body></html>')
    return ''.join(output).encode('utf-8')
