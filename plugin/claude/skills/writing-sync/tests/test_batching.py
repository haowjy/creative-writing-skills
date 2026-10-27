from copy import deepcopy
import json
import unittest

from drive_sync.batching import plan_batches
from drive_sync.conversion import render, docs_requests, utf16
from drive_sync.index import Diagnostic


class BatchPlanningTests(unittest.TestCase):
    def test_large_unicode_insert_preserves_indices_text_and_styles(self):
        source = ('**Emoji 😀 with combining e\u0301 and slash \\**\n\n' * 40).encode()
        rendering = render(source, 'markdown')
        original = docs_requests(rendering, tab_id='tab', revision='old', old_end=25)
        saved = deepcopy(original)
        segments = plan_batches(original, max_bytes=700, max_requests=4, revision_reserve=32)
        self.assertGreater(len(segments), 1)
        emitted = []
        text = ''
        for i, segment in enumerate(segments):
            batch = segment.bind_revision('fresh-' + str(i))
            self.assertLessEqual(len(json.dumps(batch).encode()), 700)
            self.assertLessEqual(len(batch['requests']), 4)
            for request in batch['requests']:
                emitted.append(request)
                if 'insertText' in request:
                    insert = request['insertText']
                    self.assertEqual(insert['location']['index'], 1 + utf16(text))
                    text += insert['text']
        self.assertEqual(text, rendering.text)
        self.assertEqual([r for r in emitted if 'insertText' not in r],
                         [r for r in original['requests'] if 'insertText' not in r])
        self.assertEqual(original, saved)

    def test_request_count_and_segment_immutability(self):
        batch = {'writeControl': {'requiredRevisionId': 'r'}, 'requests': [{'x': i} for i in range(11)]}
        segments = plan_batches(batch, max_bytes=500, max_requests=3, revision_reserve=16)
        self.assertEqual([len(s.bind_revision('r')['requests']) for s in segments], [3, 3, 3, 2])
        changed = segments[0].bind_revision('r')
        changed['requests'][0]['x'] = 99
        self.assertEqual(segments[0].bind_revision('r')['requests'][0]['x'], 0)

    def test_indivisible_request_and_invalid_guards_block(self):
        for batch in ({'writeControl': {'targetRevisionId': 'r'}, 'requests': []},
                      {'writeControl': {'requiredRevisionId': 'r'}, 'requests': [{'style': 'x' * 1000}]}):
            with self.assertRaises(Diagnostic):
                plan_batches(batch, max_bytes=300, revision_reserve=16)

    def test_actual_revision_is_rechecked(self):
        batch = {'writeControl': {'requiredRevisionId': 'r'}, 'requests': [{'x': 1}]}
        segment = plan_batches(batch, max_bytes=200, revision_reserve=16)[0]
        with self.assertRaises(Diagnostic):
            segment.bind_revision('r' * 500)

    def test_oversized_empty_insert_is_not_silently_dropped(self):
        batch = {'writeControl': {'requiredRevisionId': 'r'}, 'requests': [
            {'insertText': {'text': '', 'location': {'index': 1, 'tabId': 't' * 1000}}}]}
        with self.assertRaises(Diagnostic):
            plan_batches(batch, max_bytes=300, revision_reserve=16)
