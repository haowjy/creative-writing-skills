"""Reversible source-link provenance; no filesystem URLs or guessed targets."""
from dataclasses import dataclass, replace
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .conversion import Rendering
from .index import Diagnostic


@dataclass(frozen=True)
class LinkProvenance:
    source_href: str
    destination_url: str
    target_source_id: str


def rewrite_links(rendering: Rendering, source_path: Path,
                  destinations: dict[Path, tuple[str, str]]) -> tuple[Rendering, tuple[LinkProvenance, ...]]:
    """Destinations map selected absolute paths to verified (source UUID, Doc ID)."""
    styles, provenance = [], []
    for style in rendering.styles:
        if style.kind != 'link':
            styles.append(style)
            continue
        href = style.value
        parsed = urlsplit(href)
        if parsed.scheme in ('https','http','mailto'):
            styles.append(style)
            continue
        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
            raise Diagnostic('unsupported_link', 'Link scheme, query or fragment lacks a reversible mapping.', 'Review the link; do not emit a filesystem URL or guess a Docs anchor.', str(source_path))
        path = Path(unquote(parsed.path))
        if path.is_absolute():
            raise Diagnostic('private_link', 'Absolute local links cannot be published.', 'Use a selected relative source link.', str(source_path))
        target = (source_path.parent / path).resolve()
        if target not in destinations:
            raise Diagnostic('unbound_link', 'Relative link target has no verified selected destination.', 'Select and bind the target before updating this document.', str(source_path))
        source_id, doc_id = destinations[target]
        from .google import identifier
        url = 'https://docs.google.com/document/d/' + identifier(doc_id) + '/edit'
        styles.append(replace(style,value=url))
        provenance.append(LinkProvenance(href,url,source_id))
    findings = tuple(f for f in rendering.findings if f.code != 'link_mapping_required')
    return replace(rendering,styles=tuple(styles),findings=findings),tuple(provenance)


def restore_link(url: str, provenance: tuple[LinkProvenance, ...]) -> str:
    candidates = {p.source_href for p in provenance if p.destination_url == url}
    if len(candidates) != 1:
        raise Diagnostic('ambiguous_link_return', 'Remote link lacks a unique original-source spelling.', 'Review link provenance rather than writing a guessed local path.')
    return next(iter(candidates))
