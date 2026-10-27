"""Fixed-operation, private subprocess boundary for untrusted conversion inputs."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from .index import Diagnostic

_IN_WORKER = False


@dataclass(frozen=True)
class ConversionLimits:
    cpu_seconds: int = 10
    wall_seconds: float = 20
    memory_bytes: int = 512 * 1024 * 1024
    output_bytes: int = 64 * 1024 * 1024
    input_bytes: int = 256 * 1024 * 1024


def limited(reason):
    return Diagnostic('conversion_resource_limit', reason,
                      'Retain both copies. Reduce the selected document complexity or review conversion manually; no source replacement was authorized.')


def execute(operation: str, arguments: dict, *, limits: ConversionLimits | None = None) -> dict:
    limits = limits or ConversionLimits()
    if (operation not in ('render', 'return', 'report')
            or any(type(v) is not int or v <= 0 for v in
                   (limits.cpu_seconds, limits.memory_bytes, limits.output_bytes, limits.input_bytes))
            or type(limits.wall_seconds) not in (int, float) or not 0 < limits.wall_seconds <= 3600):
        raise Diagnostic('invalid_conversion_request', 'Invalid conversion operation or resource policy.', 'Use a supported bounded conversion request.')
    payload = json.dumps(dict(operation=operation, arguments=arguments), ensure_ascii=False).encode('utf-8')
    if len(payload) > limits.input_bytes:
        raise limited('Conversion input exceeds the serialized input limit.')
    with TemporaryDirectory(prefix='drive-sync-conversion-') as directory:
        directory = Path(directory)
        request, response = directory / 'request.json', directory / 'response.json'
        fd = os.open(request, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
        # Do not inherit profile/token environment variables or arbitrary source
        # PYTHONPATH. Both installed and development packages resolve explicitly.
        env = {'PYTHONPATH': str(Path(__file__).resolve().parent.parent),
               'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1',
               'HOME': str(directory), 'TMPDIR': str(directory), 'LANG': 'C.UTF-8'}
        command = [sys.executable, '-m', 'drive_sync.conversion_worker', str(request), str(response),
                   str(limits.cpu_seconds), str(limits.memory_bytes), str(limits.output_bytes)]
        try:
            result = subprocess.run(command, cwd=directory, env=env, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    timeout=limits.wall_seconds, check=False, close_fds=True)
        except subprocess.TimeoutExpired:
            raise limited('Conversion exceeded its wall-time budget; its worker was stopped.') from None
        except OSError:
            raise Diagnostic('conversion_worker_unavailable', 'The bounded conversion worker could not start.',
                             'Check the installed Python environment; do not bypass conversion limits.') from None
        if result.returncode != 0 or not response.is_file():
            raise limited('Conversion worker stopped without a complete result (resource limit or worker failure).')
        if response.stat().st_size > limits.output_bytes:
            raise limited('Conversion result exceeds the output limit.')
        try:
            value = json.loads(response.read_bytes())
            if not isinstance(value, dict):
                raise ValueError()
            if 'error' in value:
                error = value['error']
                raise Diagnostic(error['code'], error['reason'], error['action'], error.get('source', ''),
                                 destination=error.get('destination', ''), operation=error.get('operation', ''))
            if not isinstance(value['result'], dict):
                raise ValueError()
            return value['result']
        except (ValueError, KeyError, TypeError) as exc:
            if isinstance(exc, Diagnostic):
                raise
            raise limited('Conversion worker returned an invalid or incomplete result.') from None
