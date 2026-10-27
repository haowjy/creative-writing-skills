"""Saved credential envelope validation without network or real credentials."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from drive_sync.auth import SCOPE, TOKEN_URI, auth_status, authorized_session, validate_profile
from drive_sync.index import Diagnostic
from drive_sync.state import write_json


def record():
    return {'version': 1, 'account': 'synthetic-account', 'credentials': {
        'token_uri': TOKEN_URI, 'scopes': [SCOPE],
        'client_id': 'synthetic.apps.googleusercontent.com',
        'client_secret': 'PRIVATE', 'refresh_token': 'PRIVATE'}}


class ProfileTests(unittest.TestCase):
    def test_invalid_metadata_is_consistently_rejected_before_network(self):
        mutations = [lambda r: r.update(version=True), lambda r: r.update(version=2),
                     lambda r: r.update(account={}), lambda r: r.update(account='')]
        for key in ('client_id', 'client_secret', 'refresh_token'):
            mutations.append(lambda r, key=key: r['credentials'].pop(key))
        mutations.extend([lambda r: r['credentials'].update(scopes=SCOPE),
                          lambda r: r['credentials'].update(scopes=[SCOPE, 'broad']),
                          lambda r: r['credentials'].update(token_uri='https://untrusted.invalid/token')])
        with TemporaryDirectory() as directory:
            home = Path(directory)
            (home / 'personal').mkdir()
            token = home / 'personal/token.json'
            for mutate in mutations:
                value = deepcopy(record())
                mutate(value)
                write_json(token, value)
                before = token.read_bytes()
                with patch('google.oauth2.credentials.Credentials.from_authorized_user_info') as factory:
                    for method in ('status', 'session'):
                        with self.subTest(method=method, value=value):
                            with self.assertRaises(Diagnostic) as caught:
                                if method == 'status':
                                    auth_status('personal', home=home)
                                else:
                                    with authorized_session('personal', home=home):
                                        self.fail('Invalid profile yielded a session')
                            self.assertEqual(caught.exception.code, 'invalid_profile')
                            self.assertNotIn('PRIVATE', str(caught.exception.as_dict()))
                    factory.assert_not_called()
                self.assertEqual(token.read_bytes(), before)

    def test_valid_record_is_returned_without_mutation(self):
        value = record()
        before = deepcopy(value)
        self.assertEqual(validate_profile(value), value['credentials'])
        self.assertEqual(value, before)
