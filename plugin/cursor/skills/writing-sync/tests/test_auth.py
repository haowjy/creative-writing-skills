from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import unittest

from drive_sync.auth import SCOPE, TOKEN_URI, auth_status, begin_login, begin_pick_folder, complete_login, complete_pick_folder, logout
from drive_sync.index import Diagnostic


class FakeFlow:
    def __init__(self, config, scopes, **kwargs):
        self.config = config
        self.scopes = scopes
        self.kwargs = kwargs
        self.credentials = SimpleNamespace(granted_scopes=[SCOPE], scopes=[SCOPE], refresh_token='synthetic',
            to_json=lambda: json.dumps(dict(token_uri=TOKEN_URI, client_id='test.apps.googleusercontent.com', scopes=[SCOPE], refresh_token='synthetic', client_secret='synthetic')))

    def authorization_url(self, **kwargs):
        self.auth_kwargs = kwargs
        return 'https://accounts.google.com/test?state=test-state', 'test-state'

    def fetch_token(self, **kwargs):
        self.response = kwargs


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.client = self.home / 'client.json'
        self.client.write_text(json.dumps(dict(installed=dict(auth_uri='https://accounts.google.com/o/oauth2/auth',
            token_uri=TOKEN_URI, client_id='test.apps.googleusercontent.com', client_secret='synthetic'))))

    def test_mixed_web_and_desktop_client_is_rejected_before_flow_creation(self):
        from unittest.mock import Mock
        raw = json.loads(self.client.read_text())
        raw['web'] = {'auth_uri': 'https://untrusted.invalid/auth',
                      'token_uri': 'https://untrusted.invalid/token',
                      'client_id': 'untrusted', 'client_secret': 'PRIVATE'}
        self.client.write_text(json.dumps(raw))
        factory = Mock()
        with self.assertRaises(Diagnostic) as caught:
            begin_login('personal', self.client, home=self.home / 'config', port=0, flow_factory=factory)
        self.assertEqual(caught.exception.code, 'invalid_client')
        self.assertNotIn('PRIVATE', str(caught.exception.as_dict()))
        factory.assert_not_called()
        self.assertFalse((self.home / 'config').exists())

    def test_duplicate_client_sections_are_rejected(self):
        from drive_sync.auth import client_config
        installed = json.loads(self.client.read_text())['installed']
        self.client.write_text('{"installed":' + json.dumps(installed) +
                               ',"installed":' + json.dumps(installed) + '}')
        with self.assertRaises(Diagnostic) as caught:
            client_config(self.client)
        self.assertEqual(caught.exception.code, 'invalid_client')

    def begin(self, **kwargs):
        session = begin_login('personal', self.client, home=self.home / 'config', port=0, flow_factory=FakeFlow, **kwargs)
        self.addCleanup(session.close)
        return session

    def test_save_status_logout_and_no_secret_output(self):
        session = self.begin()
        self.assertTrue(session.flow.kwargs['autogenerate_code_verifier'])
        session.callback.append('https://127.0.0.1/?code=synthetic&state=test-state')
        result = complete_login(session, identify=lambda _: 'account')
        self.assertTrue(result['authorized'])
        self.assertNotIn('synthetic', json.dumps(result))
        self.assertTrue(auth_status('personal', home=self.home / 'config')['authorized'])
        self.assertEqual((session.profile / 'token.json').stat().st_mode & 0o777, 0o600)
        with self.assertRaises(Diagnostic):
            self.begin()
        self.assertFalse(logout('personal', home=self.home / 'config')['authorized'])

    def test_scope_rejected(self):
        session = self.begin()
        session.callback.append('synthetic')
        session.flow.credentials.granted_scopes.append('broad')
        with self.assertRaises(Diagnostic):
            complete_login(session, identify=lambda _: 'account')
        self.assertFalse((session.profile / 'token.json').exists())

    def test_timeout_closes_server(self):
        session = self.begin(timeout=0.001)
        with self.assertRaises(Diagnostic) as caught:
            complete_login(session)
        self.assertEqual(caught.exception.code, 'login_timeout')
        self.assertTrue(session.closed)

    def test_bad_client_and_profile(self):
        self.client.write_text('{"web":{}}')
        with self.assertRaises(Diagnostic):
            self.begin()
        with self.assertRaises(Diagnostic):
            auth_status('../escape', home=self.home)

    def test_token_exchange_error_redacted(self):
        session = self.begin()
        session.callback.append('synthetic')
        def fail(**kwargs):
            raise ValueError('secret-token-contents')
        session.flow.fetch_token = fail
        with self.assertRaises(Diagnostic) as caught:
            complete_login(session)
        self.assertNotIn('secret-token', str(caught.exception))

    def test_pick_folder_requires_login_and_returns_one_folder(self):
        with self.assertRaises(Diagnostic) as caught:
            begin_pick_folder('personal', self.client, home=self.home / 'config', port=0, flow_factory=FakeFlow)
        self.assertEqual(caught.exception.code, 'reauthorization_required')
        session = self.begin()
        session.callback.append('https://127.0.0.1/?code=synthetic&state=test-state')
        complete_login(session, identify=lambda _: 'account')
        picker = begin_pick_folder('personal', self.client, home=self.home / 'config', port=0, flow_factory=FakeFlow)
        self.addCleanup(picker.close)
        self.assertEqual(picker.flow.auth_kwargs.get('trigger_onepick'), 'true')
        self.assertEqual(picker.flow.auth_kwargs.get('allow_folder_selection'), 'true')
        self.assertNotIn('mimetypes', picker.flow.auth_kwargs)
        picker.callback.append('https://127.0.0.1/?code=synthetic&state=test-state&picked_file_ids=granted-folder')
        result = complete_pick_folder(picker, identify=lambda _: 'account',
                                      inspect=lambda _creds, fid: dict(id=fid, name='Writing', mimeType='application/vnd.google-apps.folder', ownedByMe=True, trashed=False))
        self.assertEqual(result['folder_id'], 'granted-folder')
        self.assertEqual(result['name'], 'Writing')
        self.assertNotIn('synthetic', json.dumps(result))

    def test_loopback_validates_state_without_logging_codes(self):
        import threading
        from urllib.request import urlopen
        from urllib.error import HTTPError
        session = self.begin()
        output = []
        thread = threading.Thread(target=lambda: output.append(complete_login(session, identify=lambda _: 'account')))
        thread.start()
        base = f'http://127.0.0.1:{session.server.server_port}/'
        try:
            with self.assertRaises(HTTPError) as caught:
                urlopen(base + '?code=synthetic&state=wrong', timeout=3)
            self.assertEqual(caught.exception.code, 400)
            caught.exception.close()
            self.assertEqual(session.callback, [])
            with urlopen(base + '?code=synthetic&state=test-state', timeout=3) as response:
                self.assertEqual(response.status, 200)
        finally:
            thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        self.assertTrue(output[0]['authorized'])
