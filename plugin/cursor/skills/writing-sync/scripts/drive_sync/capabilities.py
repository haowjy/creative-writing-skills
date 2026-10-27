"""Offline conversion capability reporting, independent of CLI presentation."""
from dataclasses import dataclass
from pathlib import Path

from .conversion import Finding, render
from .index import Diagnostic, Source, resolve
from .sources import snapshot
from .storage import load_index


@dataclass(frozen=True)
class FormatCapability:
    format: str
    import_route: str
    remote_read_route: str
    update_route: str
    semantic_comparison: str
    return_route: str
    protected_material: tuple[str, ...]
    return_requires_candidate_verification: bool = True


def format_capabilities() -> tuple[FormatCapability, ...]:
    """Implemented routes, not certification of arbitrary input or remote edits.

    Per-source rendering findings and per-edit candidate verification remain
    authoritative gates. This table does not query an account or authorize I/O.
    """
    protection = {
        'markdown': ('frontmatter', 'comments', 'source markup and link syntax'),
        'text': ('UTF-8 literal text', 'source newline convention'),
        'html': ('original tags and attributes', 'comments', 'whitespace outside mapped text runs'),
        'epub': ('archive members', 'spine order', 'package metadata except modified timestamp', 'XHTML markup'),
    }
    returns = {
        'markdown': 'uniquely mapped literal-text patches to original Markdown bytes',
        'text': 'plain-text candidate with source newline convention; unrepresentable formatting blocks',
        'html': 'uniquely mapped literal-text patches to original HTML bytes',
        'epub': 'mapped XHTML text patches in original package; update modified timestamp',
    }
    return tuple(FormatCapability(format,
        'local readable model; HTML import or separately initialized Doc population',
        'guarded Docs structural observation, not a reconstructed files.export source',
        'Docs requiredRevisionId batches', 'canonical text and supported style coverage',
        returns[format], protection[format]) for format in protection)


@dataclass(frozen=True)
class ConversionReport:
    source: str
    storage: str
    format: str
    supported: bool
    fingerprint: str | None = None
    findings: tuple[Finding, ...] = ()
    return_policy: str = 'not_evaluated'


def check_source_conversion(source: Source) -> ConversionReport:
    """Inspect one resolved source; never substitute another storage mode."""
    try:
        captured = snapshot(source.path)
        if source.storage == 'original':
            return ConversionReport(str(source.path), source.storage, source.format, True,
                                    return_policy='guarded_original_bytes')
        result = render(captured.data, source.format)
        return ConversionReport(str(source.path), source.storage, source.format,
            result.supported, result.fingerprint, result.findings,
            'candidate_verification_required' if result.supported else 'blocked_by_source_conversion')
    except Diagnostic as exc:
        return ConversionReport(str(source.path), source.storage, source.format,
            False, findings=(Finding(exc.code, exc.reason, exc.action),))
    except OSError:
        return ConversionReport(str(source.path), source.storage, source.format,
            False, findings=(Finding('source_unreadable', 'Selected source could not be read.',
                'Check that the file still exists and is readable, then preview again.'),))


def check_conversion(index_path: Path) -> tuple[ConversionReport, ...]:
    """Report every selected source without credentials, state or remote writes.

    Selection/index errors abort because the requested scope is not established.
    Per-file findings do not suppress reports for the remaining known selection.
    Original mode validates readable bytes, not conversion fidelity.
    """
    loaded = load_index(index_path)
    return tuple(check_source_conversion(source) for source in resolve(loaded.model, index_path))
