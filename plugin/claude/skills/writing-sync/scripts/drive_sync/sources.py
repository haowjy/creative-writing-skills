"""Platform-neutral immutable source snapshots and guarded candidate commits."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import stat
import json

from .index import Diagnostic
from .file_metadata import FileMetadata, capture, restore
from .storage import atomic_write, digest


@dataclass(frozen=True)
class SourceBytes:
    path: Path
    data: bytes
    digest: str
    device: int
    inode: int
    modified_ns: int
    mode: int
    metadata: FileMetadata


def snapshot(path: Path, max_bytes: int = 64 * 1024 * 1024) -> SourceBytes:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise Diagnostic('unsafe_source', 'Source path contains a symlink.', 'Select a regular source path.', str(path))
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > max_bytes:
            raise Diagnostic('unsupported_source', 'Source is nonregular or exceeds the snapshot size limit.', 'Use a supported regular source within the configured limit.', str(path))
        metadata = capture(fd)
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(max_bytes + 1)
        after = os.fstat(fd)
        current = path.stat(follow_symlinks=False)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if len(data) > max_bytes or identity(before) != identity(after) or identity(after) != identity(current):
            raise Diagnostic('source_race', 'Source changed while being read.', 'Stop editing and preview again.', str(path))
        return SourceBytes(path, data, digest(data), after.st_dev, after.st_ino, after.st_mtime_ns, stat.S_IMODE(after.st_mode), metadata)
    finally:
        os.close(fd)


def commit_candidate(original: SourceBytes, candidate: bytes, backup_directory: Path) -> SourceBytes:
    """Caller validates candidate format first. External editors must be paused.

    Atomic rename is not an OS compare-and-swap. Both versions are retained before
    replacement, and a post-write anomaly is reported rather than overwritten.
    """
    from .state import private_directory, write_json
    if original.mode & ~0o777:
        raise Diagnostic('unsupported_source_permissions', 'Source has special permission bits.',
                         'Review its permissions before returning edits; no replacement occurred.', str(original.path))
    directory = private_directory(backup_directory)
    atomic_write(directory / (original.digest + '.source'), original.data)
    atomic_write(directory / (digest(candidate) + '.candidate'), candidate)
    metadata_record = dict(version=1, source=str(original.path), content_hash=original.digest,
                           modified_ns=original.modified_ns, mode=original.metadata.mode,
                           uid=original.metadata.uid, gid=original.metadata.gid,
                           attributes={name: value.hex() for name, value in original.metadata.attributes})
    write_json(directory / (original.digest + '.metadata-' + digest(json.dumps(metadata_record, sort_keys=True).encode()) + '.json'), metadata_record)
    current = snapshot(original.path)
    if (current.digest, current.device, current.inode, current.metadata) != (original.digest, original.device, original.inode, original.metadata):
        raise Diagnostic('source_race', 'Source changed after candidate review.', 'Review the current source against the retained candidate; no replacement occurred.', str(original.path))
    atomic_write(original.path, candidate, mode=original.mode, prepare_fd=lambda fd: restore(fd, original.metadata))
    observed = snapshot(original.path)
    if observed.digest != digest(candidate) or observed.metadata != original.metadata:
        atomic_write(directory / (observed.digest + '.observed'), observed.data)
        raise Diagnostic('source_race', 'Source changed during replacement.', 'Pause external editors and reconcile retained source, candidate and observed versions.', str(original.path))
    return observed
