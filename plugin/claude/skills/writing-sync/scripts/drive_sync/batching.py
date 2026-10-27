"""Pure ordered request segmentation; no authorization, I/O or write retries.

Execution must journal and verify each segment with a fresh required revision.
These segments alone do not make a multi-request operation atomic or safe.
"""
from copy import deepcopy
from dataclasses import dataclass
import json

from .conversion import utf16
from .index import Diagnostic


def reject(reason):
    raise Diagnostic('batch_plan_limit', reason,
                     'Inspect the document request plan; do not send unguarded partial batches.')


@dataclass(frozen=True)
class BatchSegment:
    requests_json: str
    max_bytes: int
    max_requests: int

    def bind_revision(self, revision: str) -> dict:
        if not isinstance(revision, str) or not revision:
            reject('A fresh required revision is mandatory for every segment.')
        requests = json.loads(self.requests_json)
        batch = {'writeControl': {'requiredRevisionId': revision}, 'requests': requests}
        if len(requests) > self.max_requests or len(json.dumps(batch).encode()) > self.max_bytes:
            reject('The actual revision or requests exceed the segment budget.')
        return batch


def plan_batches(batch: dict, *, max_bytes: int = 1_000_000,
                 max_requests: int = 500, revision_reserve: int = 4096) -> tuple[BatchSegment, ...]:
    """Retain request order; split only oversized explicit-location text inserts.

    Each split insert advances by UTF-16 code units of earlier chunks. Character
    slicing never cuts a Python Unicode code point into a surrogate half. Style
    requests remain after all text inserts, with their original absolute ranges.
    The revision reserve budgets envelope space; bind_revision rechecks its real
    serialized size immediately before the executor may use it.
    """
    if (type(max_bytes) is not int or type(max_requests) is not int
            or type(revision_reserve) is not int or min(max_bytes, max_requests, revision_reserve) < 1):
        reject('Batch limits must be positive integers.')
    control = batch.get('writeControl', {})
    if set(control) != {'requiredRevisionId'} or not control['requiredRevisionId']:
        reject('Only required-revision document batches can be segmented.')
    requests = batch.get('requests')
    if not isinstance(requests, list):
        reject('Expected an ordered request list.')
    reserve = 'r' * revision_reserve

    def fits(values):
        envelope = {'writeControl': {'requiredRevisionId': reserve}, 'requests': values}
        return len(values) <= max_requests and len(json.dumps(envelope).encode()) <= max_bytes

    if not fits([]):
        reject('The revision envelope alone exceeds the byte budget.')

    def split_request(request):
        if fits([request]):
            yield deepcopy(request)
            return
        if not isinstance(request, dict) or set(request) != {'insertText'}:
            reject('An indivisible nontext request exceeds the byte budget.')
        insert = request['insertText']
        if (not isinstance(insert, dict) or set(insert) != {'text', 'location'}
                or not isinstance(insert['text'], str) or not isinstance(insert['location'], dict)):
            reject('Oversized insert is not an explicit-location text request.')
        location = insert['location']
        if type(location.get('index')) is not int or location['index'] < 1:
            reject('Text insertion requires a positive explicit UTF-16 index.')
        text = insert['text']
        if not text:
            reject('An oversized empty insert cannot be split.')
        position, index = 0, location['index']
        while position < len(text):
            def part(count):
                return {'insertText': {'location': dict(location, index=index),
                                       'text': text[position:position + count]}}
            low, high = 0, len(text) - position
            while low < high:
                middle = (low + high + 1) // 2
                if fits([part(middle)]):
                    low = middle
                else:
                    high = middle - 1
            if not low:
                reject('A single character cannot fit the request budget.')
            yield part(low)
            index += utf16(text[position:position + low])
            position += low

    segments, current = [], []
    for request in requests:
        for piece in split_request(request):
            if current and not fits(current + [piece]):
                segments.append(BatchSegment(json.dumps(current), max_bytes, max_requests))
                current = []
            current.append(piece)
    if current:
        segments.append(BatchSegment(json.dumps(current), max_bytes, max_requests))
    return tuple(segments)
