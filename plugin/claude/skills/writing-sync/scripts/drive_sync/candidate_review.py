"""Private, bounded-size change reports; never a replacement authorization."""
from dataclasses import dataclass
from difflib import unified_diff
from io import BytesIO
from zipfile import BadZipFile, ZipFile

from .storage import digest


@dataclass(frozen=True)
class CandidateChange:
    kind: str
    before_hash: str
    candidate_hash: str
    before_bytes: int
    candidate_bytes: int
    diff: str | None
    members: tuple[dict, ...] = ()
    note: str = ''


def describe_candidate(before: bytes, candidate: bytes, format: str) -> CandidateChange:
    from .conversion_process import _IN_WORKER, execute
    if not _IN_WORKER:
        from base64 import b64encode
        result = execute('report', dict(before=b64encode(before).decode('ascii'),
                         candidate=b64encode(candidate).decode('ascii'), format=format))
        result['members'] = tuple(result['members'])
        return CandidateChange(**result)
    common = dict(before_hash=digest(before), candidate_hash=digest(candidate),
                  before_bytes=len(before), candidate_bytes=len(candidate))
    if format == 'epub':
        try:
            inventories = []
            for data in (before, candidate):
                with ZipFile(BytesIO(data)) as archive:
                    entries = archive.infolist()
                    if (len(entries) > 2000 or sum(e.file_size for e in entries) > 20_000_000
                            or len({e.filename for e in entries}) != len(entries)):
                        raise ValueError('report bounds')
                    inventories.append({e.filename: dict(hash=digest(archive.read(e)), size=e.file_size)
                                        for e in entries})
            old, new = inventories
            members = tuple(dict(path=name, change='added' if name not in old else 'removed' if name not in new else
                                 'unchanged' if old[name] == new[name] else 'modified',
                                 before=old.get(name), candidate=new.get(name)) for name in sorted(old.keys() | new.keys()))
            return CandidateChange('epub-members', **common, diff=None, members=members,
                                   note='Member payload comparison, not proof of visual fidelity. Package metadata may intentionally change.')
        except (BadZipFile, ValueError, RuntimeError, OSError):
            return CandidateChange('binary', **common, diff=None,
                                   note='Archive comparison unavailable or exceeds report bounds; inspect the retained complete files.')
    if max(len(before), len(candidate)) <= 200_000:
        try:
            old, new = before.decode('utf-8'), candidate.decode('utf-8')
            if '\x00' not in old + new:
                # Preserve original bytes in artifacts; split only CR/LF for the
                # human-facing diff, not Unicode prose separators.
                old_lines = old.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                new_lines = new.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                diff = '\n'.join(unified_diff(old_lines, new_lines, fromfile='before.source',
                                              tofile='candidate.source', lineterm=''))
                return CandidateChange('text-diff', **common, diff=diff,
                                       note='Diff normalizes CR/LF for display; hashes and retained files compare exact bytes.')
        except UnicodeError:
            pass
    return CandidateChange('binary', **common, diff=None,
                           note='Text diff omitted for binary or large data; inspect the retained complete files.')
