"""Internal fixed-dispatch converter worker; no source paths, OAuth or remote API."""
import base64
from dataclasses import asdict
import json
import os
from pathlib import Path
import resource
import sys


def apply_limits(cpu: int, memory: int, output: int) -> None:
    for kind, requested in ((resource.RLIMIT_CPU, cpu), (resource.RLIMIT_AS, memory),
                            (resource.RLIMIT_FSIZE, output), (resource.RLIMIT_CORE, 0)):
        _, hard = resource.getrlimit(kind)
        limit = requested if hard == resource.RLIM_INFINITY else min(requested, hard)
        resource.setrlimit(kind, (limit, limit))


def dispatch(request: dict) -> dict:
    from . import conversion_process
    conversion_process._IN_WORKER = True
    args = request['arguments']
    decode = lambda value: base64.b64decode(value, validate=True)
    if request['operation'] == 'render':
        from .conversion import render
        return asdict(render(decode(args['data']), args['format']))
    if request['operation'] == 'return':
        from .return_conversion import return_candidate
        result = return_candidate(decode(args['source']), expected_source_hash=args['expected_source_hash'],
                                  format=args['format'], baseline_text=args['baseline_text'], remote_text=args['remote_text'])
        return asdict(result) | {'data': base64.b64encode(result.data).decode('ascii')}
    if request['operation'] == 'report':
        from .candidate_review import describe_candidate
        return asdict(describe_candidate(decode(args['before']), decode(args['candidate']), args['format']))
    raise ValueError('Unknown worker operation')


def main():
    os.umask(0o077)
    request, output = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        apply_limits(*(int(v) for v in sys.argv[3:6]))
    except (ValueError, OSError, AttributeError):
        # Fail closed if the platform cannot establish the requested limits.
        return
    from .index import Diagnostic
    try:
        result = {'result': dispatch(json.loads(request.read_bytes()))}
    except Diagnostic as exc:
        result = {'error': exc.as_dict()}
    except (MemoryError, RecursionError):
        result = {'error': dict(code='conversion_resource_limit', reason='Conversion exceeded its memory or recursion budget.',
                               action='Retain both copies and reduce document complexity; do not bypass the limit.')}
    except Exception:
        result = {'error': dict(code='conversion_worker_failed', reason='Conversion worker could not produce a validated result.',
                               action='Inspect the source capability findings; private worker exceptions are not logged.')}
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False)


if __name__ == '__main__':
    main()
