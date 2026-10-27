"""POSIX source metadata captured/restored through already-open descriptors."""
from dataclasses import dataclass
import errno
import os
import stat
from .index import Diagnostic


@dataclass(frozen=True)
class FileMetadata:
    mode: int
    uid: int
    gid: int
    attributes: tuple[tuple[str, bytes], ...]


def attributes(fd: int) -> tuple[tuple[str, bytes], ...]:
    try:
        try:
            names = os.listxattr(fd)
        except OSError as exc:
            if exc.errno in (errno.ENOTSUP, errno.EOPNOTSUPP):
                return ()  # Filesystem explicitly reports no attribute support.
            raise
        if len(names) > 1024:
            raise Diagnostic('source_metadata_limit', 'Too many source extended attributes.',
                             'Review filesystem metadata before syncing this source.')
        result = []
        size = 0
        for name in sorted(names):
            value = os.getxattr(fd, name)
            size += len(os.fsencode(name)) + len(value)
            if size > 1024 * 1024:
                raise Diagnostic('source_metadata_limit', 'Source metadata exceeds the capture limit.',
                                 'Review filesystem metadata before syncing this source.')
            result.append((name, value))
        return tuple(result)
    except OSError:
        raise Diagnostic('source_metadata_unreadable', 'Extended attributes could not be read.',
                         'Restore metadata access; do not replace a source with unknown metadata.') from None
    except AttributeError:
        raise Diagnostic('source_metadata_unsupported', 'This runtime cannot inspect extended attributes.',
                         'Use a supported POSIX runtime before returning edits to sources.') from None


def capture(fd: int) -> FileMetadata:
    metadata = os.fstat(fd)
    return FileMetadata(stat.S_IMODE(metadata.st_mode), metadata.st_uid, metadata.st_gid, attributes(fd))


def restore(fd: int, expected: FileMetadata) -> None:
    """Restore on a temporary file; failure must precede pathname replacement."""
    try:
        current = os.fstat(fd)
        if (current.st_uid, current.st_gid) != (expected.uid, expected.gid):
            os.fchown(fd, expected.uid, expected.gid)
        actual = dict(attributes(fd))
        wanted = dict(expected.attributes)
        for name in actual.keys() - wanted.keys():
            os.removexattr(fd, name)
        for name, value in wanted.items():
            if actual.get(name) != value:
                os.setxattr(fd, name, value)
        if capture(fd) != expected:
            raise Diagnostic('source_metadata_mismatch', 'Temporary file metadata differs from the source.',
                             'Review permissions, ACLs and ownership; the original path was not replaced.')
    except OSError:
        raise Diagnostic('source_metadata_restore_failed', 'Source metadata could not be restored on the candidate.',
                         'Review ownership and extended-attribute permissions; the original path was not replaced.') from None
