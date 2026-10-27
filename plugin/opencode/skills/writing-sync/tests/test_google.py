import unittest
from types import SimpleNamespace
from drive_sync.google import GoogleDrive, DocumentObservation, has_suggestions
from drive_sync.index import Diagnostic

ID = '590b7d30-bc08-45e3-aee3-f6bbfdac6342'


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return SimpleNamespace(status_code=200, json=lambda: value)


class GoogleTests(unittest.TestCase):
    def test_metadata_reader_requires_requested_identity(self):
        for value in (None, [], {}, dict(self.metadata(), id='other'), dict(self.metadata(), id=None)):
            with self.subTest(value=value):
                session = Session([value])
                with self.assertRaises(Diagnostic) as caught:
                    GoogleDrive(session, ID).metadata('doc')
                self.assertEqual(caught.exception.code, 'invalid_metadata')
                self.assertEqual(caught.exception.destination, 'doc')
                self.assertEqual(caught.exception.operation, 'read-metadata')
                self.assertEqual(len(session.calls), 1)
        self.assertEqual(GoogleDrive(Session([self.metadata()]), ID).metadata('doc'), self.metadata())

    def test_document_reader_requires_typed_revision_and_identity(self):
        values = [None, [], {}, {'documentId': 'other', 'revisionId': 'r'}]
        values += [{'documentId': 'doc', 'revisionId': revision} for revision in (None, '', 1, True, [], {})]
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(Diagnostic) as caught:
                    GoogleDrive(Session([value]), ID).document('doc')
                self.assertEqual(caught.exception.code, 'invalid_document')
                self.assertEqual(caught.exception.destination, 'doc')
                self.assertEqual(caught.exception.operation, 'read-document')

    def test_malformed_json_is_redacted_at_metadata_and_document_boundaries(self):
        class BadJSONSession:
            def request(self, *args, **kwargs):
                def bad():
                    raise ValueError('PRIVATE RESPONSE CONTENT')
                return SimpleNamespace(status_code=200, json=bad)
        for method, code in (('metadata', 'invalid_metadata'), ('document', 'invalid_document')):
            with self.subTest(method=method):
                with self.assertRaises(Diagnostic) as caught:
                    getattr(GoogleDrive(BadJSONSession(), ID), method)('doc')
                self.assertEqual(caught.exception.code, code)
                self.assertNotIn('PRIVATE', str(caught.exception.as_dict()))

    def test_inventory_rejects_malformed_pages_and_duplicate_identities(self):
        kind = {'kind': 'drive#fileList'}
        pages = [None, [], {}, dict(kind, files=None), dict(kind, files={}),
                 dict(kind, files=[None]), dict(kind, incompleteSearch='false')]
        pages += [dict(kind, nextPageToken=v) for v in ('', None, False, 0, [])]
        pages += [dict(kind, files=[dict(self.metadata(), id=v)]) for v in ('', None, 4)]
        for page in pages:
            with self.subTest(page=page):
                session = Session([page])
                with self.assertRaises(Diagnostic):
                    GoogleDrive(session, ID).inventory()
                self.assertEqual(len(session.calls), 1)
        session = Session([dict(kind, files=[self.metadata()], nextPageToken='next'),
                           dict(kind, files=[self.metadata()])])
        with self.assertRaises(Diagnostic) as caught:
            GoogleDrive(session, ID).inventory()
        self.assertEqual(caught.exception.code, 'invalid_inventory')
        for page in (kind, dict(kind, files=[], incompleteSearch=False)):
            self.assertEqual(GoogleDrive(Session([page]), ID).inventory(), ())

    def test_ownership_requires_boolean_true_and_valid_properties(self):
        invalid = [None, [], dict(self.metadata(), ownedByMe='false'),
                   dict(self.metadata(), ownedByMe=1), dict(self.metadata(), trashed='false'),
                   dict(self.metadata(), trashed=0), dict(self.metadata(), appProperties=None)]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(Diagnostic):
                GoogleDrive(Session([]), ID).verify_owner(value)

    def test_operation_search_checks_returned_marker(self):
        item = self.metadata()
        page = dict(kind='drive#fileList', files=[item])
        with self.assertRaises(Diagnostic) as caught:
            GoogleDrive(Session([page]), ID).inventory(operation_id=ID)
        self.assertEqual(caught.exception.code, 'invalid_inventory')
        item['appProperties']['operation'] = ID
        self.assertEqual(GoogleDrive(Session([page]), ID).inventory(operation_id=ID), (item,))

    def test_comments_validate_empty_and_paginated_observations(self):
        kind = {'kind': 'drive#commentList'}
        for page in (kind, dict(kind, comments=[])):
            self.assertEqual(GoogleDrive(Session([page]), ID).comments('doc'), ())
        comment = {'id': 'comment', 'deleted': False, 'resolved': True}
        session = Session([dict(kind, nextPageToken='next'), dict(kind, comments=[comment])])
        self.assertEqual(GoogleDrive(session, ID).comments('doc'), (comment,))
        self.assertEqual(session.calls[1][2]['params']['pageToken'], 'next')
        self.assertIn('kind', session.calls[0][2]['params']['fields'])

    def test_comments_reject_malformed_or_ambiguous_pages(self):
        kind = {'kind': 'drive#commentList'}
        cases = [None, [], {}, {'kind': 'other'}, dict(kind, comments=None),
                 dict(kind, comments={}), dict(kind, comments=[None]),
                 dict(kind, comments=[{}]), dict(kind, comments=[{'id': ''}])]
        cases += [dict(kind, nextPageToken=value) for value in (None, '', False, [], 42)]
        cases += [dict(kind, comments=[{'id': 'c', field: value}])
                  for field in ('deleted', 'resolved') for value in ('false', 0, 1, None)]
        for page in cases:
            with self.subTest(page=page):
                remote = GoogleDrive(Session([page]), ID)
                with self.assertRaises(Diagnostic) as caught:
                    remote.comments('doc')
                self.assertEqual(caught.exception.code, 'invalid_annotations')
                self.assertEqual(caught.exception.destination, 'doc')
                self.assertEqual(caught.exception.operation, 'read-comments')
                self.assertEqual(len(remote.session.calls), 1)
        page = dict(kind, comments=[{'id': 'c'}], nextPageToken='next')
        with self.assertRaises(Diagnostic):
            GoogleDrive(Session([page, dict(kind, comments=[{'id': 'c'}])]), ID).comments('doc')

    def test_comments_reject_invalid_json_without_echoing_content(self):
        class InvalidJSON(Session):
            def request(self, *args, **kwargs):
                def invalid():
                    raise ValueError('private response text')
                return SimpleNamespace(status_code=200, json=invalid)
        with self.assertRaises(Diagnostic) as caught:
            GoogleDrive(InvalidJSON([]), ID).comments('doc')
        self.assertNotIn('private response', str(caught.exception))

    def test_conditional_writes_reject_non_revision_etags(self):
        from drive_sync.google import strong_etag
        for etag in ('*', 'W/"revision"', '"one", "two"', 'unquoted', '"bad\nvalue"', None):
            with self.subTest(etag=etag):
                remote = GoogleDrive(Session([]), ID)
                with self.assertRaises(Diagnostic):
                    remote.update_original('doc', b'payload', etag)
                self.assertEqual(remote.session.calls, [])
                with self.assertRaises(Diagnostic):
                    remote.update_layout('doc', name='new', parent='folder', before=self.metadata(), etag=etag)
                self.assertEqual(remote.session.calls, [])
                with self.assertRaises(Diagnostic):
                    strong_etag(etag)
        self.assertEqual(strong_etag('"valid/revision-1"'), '"valid/revision-1"')

    def test_original_etag_rejects_wrong_resource_identity(self):
        before = dict(self.metadata(), mimeType='text/plain')
        session = Session([before, {'id': 'other', 'etag': '"guard"', 'mimeType': 'text/plain'}])
        with self.assertRaises(Diagnostic) as caught:
            GoogleDrive(session, ID).original_etag('doc')
        self.assertEqual(caught.exception.code, 'unguarded_original')
        self.assertTrue(all(call[0] == 'GET' for call in session.calls))

    def test_document_observation_retries_reads_only_and_is_bounded(self):
        remote = GoogleDrive(Session([]), ID)
        calls = []
        remote.metadata = lambda _: {'id': 'doc'}
        remote.comments = lambda _: ()
        def document(_):
            calls.append('read')
            return {'revisionId': 'old' if len(calls) == 1 else 'stable'}
        remote.document = document
        self.assertEqual(remote.observe_document('doc').revision, 'stable')
        self.assertEqual(len(calls), 4)
        calls.clear()
        def changing(_):
            calls.append('read')
            return {'revisionId': str(len(calls))}
        remote.document = changing
        with self.assertRaises(Diagnostic):
            remote.observe_document('doc')
        self.assertEqual(len(calls), 6)
        self.assertEqual(remote.session.calls, [])

    def test_original_read_retry_does_not_retry_other_errors(self):
        remote = GoogleDrive(Session([]), ID)
        calls = []
        def read(file_id, max_bytes):
            calls.append('read')
            if len(calls) == 1:
                raise Diagnostic('remote_race', 'changed', 'read again')
            return b'stable', {'id': file_id}
        remote._read_original_once = read
        self.assertEqual(remote.read_original('blob')[0], b'stable')
        self.assertEqual(len(calls), 2)
        def denied(file_id, max_bytes):
            calls.append('denied')
            raise Diagnostic('remote_http', 'denied', 'restore access')
        remote._read_original_once = denied
        with self.assertRaises(Diagnostic):
            remote.read_original('blob')
        self.assertEqual(calls.count('denied'), 1)

    def metadata(self):
        return dict(id='doc', ownedByMe=True, appProperties={'driveSyncIndex': ID})

    def test_scoped_pagination(self):
        session = Session([dict(kind='drive#fileList', files=[self.metadata()], nextPageToken='next'), dict(kind='drive#fileList', files=[])])
        result = GoogleDrive(session, ID).inventory()
        self.assertEqual(len(result), 1)
        self.assertIn(ID, session.calls[0][2]['params']['q'])
        self.assertEqual(session.calls[1][2]['params']['pageToken'], 'next')

    def test_incomplete_inventory_blocks(self):
        with self.assertRaises(Diagnostic):
            GoogleDrive(Session([dict(kind='drive#fileList', incompleteSearch=True)]), ID).inventory()

    def test_transport_never_retries(self):
        session = Session([TimeoutError('private data')])
        with self.assertRaises(Diagnostic) as caught:
            GoogleDrive(session, ID).create('test', 'application/vnd.google-apps.document', ID, ID)
        self.assertEqual(len(session.calls), 1)
        self.assertNotIn('private data', str(caught.exception))

    def test_suggestion_detection_and_guard(self):
        doc = dict(revisionId='revision', tabs=[dict(textRun={'suggestedInsertionIds': ['s']})])
        self.assertTrue(has_suggestions(doc))
        observation = DocumentObservation(self.metadata(), doc, ())
        with self.assertRaises(Diagnostic):
            GoogleDrive(Session([]), ID).update_document(observation, {'writeControl': {'requiredRevisionId': 'revision'}})

    def test_guarded_request(self):
        session = Session([{}])
        observation = DocumentObservation(self.metadata(), dict(revisionId='revision'), ())
        adapter = GoogleDrive(session, ID)
        with self.assertRaises(Diagnostic):
            adapter.update_document(observation, {'writeControl': {'targetRevisionId': 'revision'}})
        adapter.update_document(observation, {'writeControl': {'requiredRevisionId': 'revision'}, 'requests': []})
        self.assertEqual(len(session.calls), 1)
        self.assertFalse(session.calls[0][2]['allow_redirects'])

    def test_capabilities_are_account_data_not_assumed(self):
        expected={'importFormats':{'text/html':['application/vnd.google-apps.document']},'exportFormats':{}}
        self.assertEqual(GoogleDrive(Session([expected]),ID).capabilities(),expected)
        with self.assertRaises(Diagnostic):
            GoogleDrive(Session([{}]),ID).capabilities()

    def test_inspect_parent_accepts_granted_folder_without_index_marker(self):
        granted = dict(id='granted-folder', name='Writing', mimeType='application/vnd.google-apps.folder',
                       ownedByMe=True, trashed=False)
        self.assertEqual(GoogleDrive(Session([granted]), ID).inspect_parent('granted-folder'), granted)
        for value in (dict(granted, mimeType='application/vnd.google-apps.document'),
                      dict(granted, ownedByMe=False), dict(granted, trashed=True), dict(granted, id='other')):
            with self.subTest(value=value), self.assertRaises(Diagnostic) as caught:
                GoogleDrive(Session([value]), ID).inspect_parent('granted-folder')
            self.assertEqual(caught.exception.code, 'invalid_parent')

    def test_layout_update_uses_metadata_only_conditional_request(self):
        before=self.metadata()
        before.update(name='old',parents=['old-parent'])
        parent=self.metadata()
        parent.update(id='new-parent',mimeType='application/vnd.google-apps.folder')
        session=Session([before,parent,{}])
        GoogleDrive(session,ID).update_layout('doc',name='new',parent='new-parent',before=before,etag='"guard"')
        method,url,kwargs=session.calls[-1]
        self.assertEqual(method,'PUT')
        self.assertNotIn('/upload/',url)
        self.assertEqual(kwargs['headers'],{'If-Match':'"guard"'})
        self.assertEqual(kwargs['json'],{'title':'new'})
        self.assertEqual(kwargs['params'],{'addParents':'new-parent','removeParents':'old-parent'})
