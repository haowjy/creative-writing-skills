import unittest
from drive_sync.google import GoogleDrive, DocumentObservation
from drive_sync.index import Diagnostic
from test_google import ID


class Response:
    def __init__(self, chunks):
        self.chunks = chunks
        self.closed = False
    def iter_content(self, chunk_size):
        yield from self.chunks
    def close(self):
        self.closed = True


class Downloads(GoogleDrive):
    def __init__(self, observations, chunks):
        super().__init__(None, ID)
        self.observations = iter(observations)
        self.response = Response(chunks)
    def request(self, *args, **kwargs):
        return self.response
    def metadata(self, file_id):
        return next(self.observations)
    def observe_document(self, file_id):
        return next(self.observations)


class DownloadTests(unittest.TestCase):
    def test_original_bytes_and_stream_closed(self):
        meta = {'mimeType':'application/octet-stream', 'version':'1'}
        adapter = Downloads([meta, meta], [b'\x00', b'\xff'])
        self.assertEqual(adapter.read_original('file')[0], b'\x00\xff')
        self.assertTrue(adapter.response.closed)

    def test_original_race_and_size_fail(self):
        for adapter, limit in [(Downloads([{'version': str(i)} for i in range(6)], [b'a']), 10),
                               (Downloads([{'version':'1'}], [b'ab']), 1)]:
            with self.assertRaises(Diagnostic):
                adapter.read_original('file', max_bytes=limit)
            self.assertTrue(adapter.response.closed)

    def test_export_bracket_includes_comments(self):
        first = DocumentObservation({'version':'1'}, {'revisionId':'r'}, ())
        second = DocumentObservation({'version':'1'}, {'revisionId':'r'}, ({'id':'comment'},))
        adapter = Downloads([first, second], [b'export'])
        with self.assertRaises(Diagnostic):
            adapter.export_document('file', 'text/plain')
        self.assertTrue(adapter.response.closed)

    def test_stable_export(self):
        obs = DocumentObservation({'version':'1'}, {'revisionId':'r'}, ())
        adapter = Downloads([obs, obs], [b'export'])
        self.assertEqual(adapter.export_document('file', 'text/plain'), (b'export', obs))
