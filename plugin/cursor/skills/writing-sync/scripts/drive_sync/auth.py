"""Desktop OAuth with an interface-neutral loopback login session."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit
import json
import os
import re
import time

from .index import Diagnostic
from .state import private_directory, read_json, write_json
from .storage import locked

SCOPE = 'https://www.googleapis.com/auth/drive.file'
TOKEN_URI = 'https://oauth2.googleapis.com/token'


def config_home() -> Path:
    return Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'drive-sync'


def profile_path(profile: str, home: Path | None = None) -> Path:
    if not re.fullmatch(r'[A-Za-z0-9_-]+', profile):
        raise Diagnostic('invalid_profile', 'Profile must be a simple name.', 'Use letters, digits, underscore or hyphen.')
    return (home or config_home()) / profile


def client_config(path: Path) -> dict:
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise Diagnostic('invalid_client', 'Client must be a regular nonsymlink file.', 'Supply the path to a Google Desktop OAuth client JSON.')
    try:
        config = read_json(path)
        # google-auth-oauthlib prefers 'web' when both sections are present.
        # Validate the same single Desktop configuration the library will use.
        if not isinstance(config, dict) or set(config) != {'installed'}:
            raise ValueError()
        client = config['installed']
        if (client['auth_uri'] != 'https://accounts.google.com/o/oauth2/auth'
                or client['token_uri'] != TOKEN_URI
                or not isinstance(client['client_id'], str)
                or not client['client_id'].endswith('.apps.googleusercontent.com')
                or not isinstance(client['client_secret'], str) or not client['client_secret']):
            raise ValueError()
        return config
    except (ValueError, TypeError, KeyError):
        raise Diagnostic('invalid_client', 'Expected a Google Desktop client with official OAuth endpoints.', 'Download a Desktop client JSON; do not paste its contents.') from None


@dataclass
class LoginSession:
    authorization_url: str
    profile: Path
    client: dict = field(repr=False)
    flow: object = field(repr=False)
    server: HTTPServer = field(repr=False)
    callback: list[str] = field(repr=False)
    deadline: float = field(repr=False)
    closed: bool = False
    picker: bool = False

    def close(self):
        if not self.closed:
            self.server.server_close()
            self.closed = True


def begin_login(profile: str, client_path: Path, *, home: Path | None = None,
                port: int = 8765, timeout: float = 600, flow_factory=None,
                picker: bool = False) -> LoginSession:
    if not 0 <= port <= 65535 or timeout <= 0:
        raise Diagnostic('invalid_login', 'Invalid callback port or timeout.', 'Use an available local port and positive timeout.')
    config = client_config(client_path.expanduser())
    directory = private_directory(profile_path(profile, home))
    authorized = (directory / 'token.json').exists()
    if picker and not authorized:
        raise Diagnostic('reauthorization_required', 'Folder picking requires an authorized profile.', 'Run auth login before auth pick-folder.')
    if authorized and not picker:
        raise Diagnostic('already_authorized', 'Profile already contains credentials.', 'Use auth status, or logout before replacing this profile.')
    if flow_factory is None:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow_factory = InstalledAppFlow.from_client_config
    flow = flow_factory(config, [SCOPE], autogenerate_code_verifier=True)
    callback: list[str] = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Callback contains authorization codes; never log requests.

        def do_GET(self):
            parsed = urlsplit(self.path)
            query = parse_qs(parsed.query)
            valid = (parsed.path == '/' and not parsed.scheme and not parsed.netloc
                     and query.get('state') == [expected_state]
                     and (len(query.get('code', [])) == 1 or 'error' in query))
            if valid and not callback:
                callback.append('https://127.0.0.1:' + str(self.server.server_port) + self.path)
            self.send_response(200 if valid else 400)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(b'Callback received. Check the CLI for login result.' if valid else b'Invalid OAuth callback.')
    server = HTTPServer(('127.0.0.1', port), Handler)
    try:
        flow.redirect_uri = f'http://127.0.0.1:{server.server_port}/'
        extra = dict(trigger_onepick='true', allow_folder_selection='true') if picker else {}
        url, expected_state = flow.authorization_url(access_type='offline', prompt='consent', **extra)
        return LoginSession(url, directory, config, flow, server, callback, time.monotonic() + timeout, picker=picker)
    except Exception:
        server.server_close()
        raise Diagnostic('login_failed', 'Could not initialize OAuth.', 'Check Desktop client setup and callback port.') from None


def account_identity(credentials) -> str:
    from google.auth.transport.requests import AuthorizedSession
    with AuthorizedSession(credentials) as session:
        response = session.get('https://www.googleapis.com/drive/v3/about',
                               params={'fields': 'user(permissionId)'}, timeout=30)
        response.raise_for_status()
        return response.json()['user']['permissionId']


def complete_login(session: LoginSession, *, cancellation=None, identify=account_identity) -> dict:
    try:
        if session.closed:
            raise ValueError('closed session')
        while not session.callback:
            if cancellation is not None and cancellation.is_set():
                raise Diagnostic('login_cancelled', 'Login was cancelled.', 'Start a new login when ready.')
            remaining = session.deadline - time.monotonic()
            if remaining <= 0:
                raise Diagnostic('login_timeout', 'No valid callback arrived before timeout.', 'Check SSH port forwarding and restart login.')
            session.server.timeout = min(0.5, remaining)
            session.server.handle_request()
        session.flow.fetch_token(authorization_response=session.callback[0], timeout=30)
        credentials = session.flow.credentials
        granted = set(credentials.granted_scopes or credentials.scopes or [])
        if granted != {SCOPE} or not credentials.refresh_token:
            raise Diagnostic('invalid_grant', 'Expected only drive.file scope and a refresh token.', 'Review consent and authorize the Desktop application again.')
        identity = identify(credentials)
        if not isinstance(identity, str) or not identity:
            raise ValueError('missing account identity')
        token = json.loads(credentials.to_json())
        if token.get('token_uri') != TOKEN_URI or token.get('client_id') != session.client['installed']['client_id']:
            raise ValueError('credential identity mismatch')
        saved = dict(version=1, account=identity, credentials=token)
        validate_profile(saved)
        with locked(session.profile / 'profile.lock'):
            if (session.profile / 'token.json').exists():
                raise Diagnostic('profile_changed', 'Another login already saved this profile.', 'Inspect auth status; do not overwrite credentials.')
            # One durable document binds account, client and token together.
            write_json(session.profile / 'token.json', saved)
        return dict(authorized=True, profile=str(session.profile), scope=SCOPE)
    except Diagnostic:
        raise
    except Exception:
        raise Diagnostic('login_failed', 'Google authorization or account verification failed.', 'Check enabled APIs, consent test users and client setup; restart login.') from None
    finally:
        session.close()


def begin_pick_folder(profile: str, client_path: Path, *, home: Path | None = None,
                      port: int = 8765, timeout: float = 600, flow_factory=None) -> LoginSession:
    return begin_login(profile, client_path, home=home, port=port, timeout=timeout,
                       flow_factory=flow_factory, picker=True)


def complete_pick_folder(session: LoginSession, *, cancellation=None, identify=account_identity,
                         inspect=None) -> dict:
    if not session.picker:
        raise Diagnostic('invalid_login', 'This session is not a folder picker.', 'Use auth pick-folder.')
    try:
        result = _complete_picker_grant(session, cancellation=cancellation, identify=identify, inspect=inspect)
        return result
    finally:
        session.close()


def _complete_picker_grant(session: LoginSession, *, cancellation, identify, inspect) -> dict:
    if session.closed:
        raise ValueError('closed session')
    while not session.callback:
        if cancellation is not None and cancellation.is_set():
            raise Diagnostic('login_cancelled', 'Folder picking was cancelled.', 'Start auth pick-folder when ready.')
        remaining = session.deadline - time.monotonic()
        if remaining <= 0:
            raise Diagnostic('login_timeout', 'No valid callback arrived before timeout.', 'Check SSH port forwarding and restart pick-folder.')
        session.server.timeout = min(0.5, remaining)
        session.server.handle_request()
    query = parse_qs(urlsplit(session.callback[0]).query)
    picked = [item for value in query.get('picked_file_ids', []) for item in value.split(',') if item]
    if len(picked) != 1 or not re.fullmatch(r'[A-Za-z0-9_-]+', picked[0]):
        raise Diagnostic('invalid_parent', 'Picker did not return exactly one folder.', 'Select one Drive folder and approve access.')
    session.flow.fetch_token(authorization_response=session.callback[0], timeout=30)
    credentials = session.flow.credentials
    granted = set(credentials.granted_scopes or credentials.scopes or [])
    if granted != {SCOPE}:
        raise Diagnostic('invalid_grant', 'Expected only drive.file scope.', 'Review consent and pick the folder again.')
    identity = identify(credentials)
    with locked(session.profile / 'profile.lock'):
        record = read_json(session.profile / 'token.json')
        validate_profile(record)
        if identity != record['account']:
            raise Diagnostic('invalid_grant', 'Picker used a different Google account.', 'Pick the folder with the same account as this profile.')
        token = json.loads(credentials.to_json())
        if token.get('refresh_token'):
            saved = dict(version=1, account=record['account'], credentials=token)
            validate_profile(saved)
            write_json(session.profile / 'token.json', saved)
    folder_id = picked[0]
    if inspect is None:
        folder = _inspect_picked_folder(credentials, folder_id)
    else:
        folder = inspect(credentials, folder_id)
    if not isinstance(folder, dict) or folder.get('id') != folder_id:
        raise Diagnostic('invalid_parent', 'Picked destination could not be verified.', 'Pick an owned Drive folder.')
    return dict(authorized=True, profile=str(session.profile), scope=SCOPE,
                folder_id=folder_id, name=folder.get('name', ''))


def _inspect_picked_folder(credentials, folder_id: str) -> dict:
    from google.auth.transport.requests import AuthorizedSession
    from .google import DRIVE, FOLDER, identifier
    with AuthorizedSession(credentials, max_refresh_attempts=0) as session:
        response = session.request('GET', DRIVE + '/files/' + identifier(folder_id),
                                   timeout=60, allow_redirects=False,
                                   params={'fields': 'id,name,mimeType,ownedByMe,trashed'})
        if not 200 <= response.status_code < 300:
            raise Diagnostic('invalid_parent', 'Picked folder is not readable with drive.file.', 'Pick the folder again in the browser.')
        result = response.json()
    if (not isinstance(result, dict) or result.get('id') != folder_id
            or result.get('mimeType') != FOLDER or result.get('ownedByMe') is not True
            or result.get('trashed') is True):
        raise Diagnostic('invalid_parent', 'Picked destination is not an owned untrashed folder.', 'Select one Drive folder you own.')
    return result


def validate_profile(record: object) -> dict:
    """Validate the same saved credential envelope for status and runtime use."""
    try:
        if (not isinstance(record, dict) or type(record.get('version')) is not int
                or record['version'] != 1 or not isinstance(record.get('account'), str)
                or not record['account']):
            raise ValueError()
        info = record['credentials']
        if (not isinstance(info, dict) or info.get('token_uri') != TOKEN_URI
                or not isinstance(info.get('scopes'), list)
                or info['scopes'] != [SCOPE]):
            raise ValueError()
        for key in ('client_id', 'client_secret', 'refresh_token'):
            if not isinstance(info.get(key), str) or not info[key]:
                raise ValueError()
        if not info['client_id'].endswith('.apps.googleusercontent.com'):
            raise ValueError()
        return info
    except (KeyError, TypeError, ValueError):
        raise Diagnostic('invalid_profile', 'Saved profile has invalid credentials metadata.',
                         'Restore a profile backup or explicitly log out and authorize again.') from None


def auth_status(profile: str, *, home: Path | None = None) -> dict:
    path = profile_path(profile, home)
    if not path.exists():
        return dict(authorized=False, profile=profile)
    private_directory(path)
    with locked(path / 'profile.lock'):
        file = path / 'token.json'
        if not file.exists():
            return dict(authorized=False, profile=profile)
        record = read_json(file)
        validate_profile(record)
        return dict(authorized=True, profile=profile, scope=SCOPE,
                    expiry=record['credentials'].get('expiry'), verified_online=False)


def logout(profile: str, *, home: Path | None = None) -> dict:
    path = profile_path(profile, home)
    if path.exists():
        private_directory(path)
        with locked(path / 'profile.lock'):
            file = path / 'token.json'
            if file.is_symlink():
                raise Diagnostic('unsafe_profile', 'Token is a symlink.', 'Inspect the private profile directory.')
            file.unlink(missing_ok=True)
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    return dict(authorized=False, profile=profile, revoked_at_google=False)


from contextlib import contextmanager


@contextmanager
def authorized_session(profile: str, *, home: Path | None = None):
    """Refresh credentials before requests; never automatically replay a mutation."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import AuthorizedSession, Request
    path = private_directory(profile_path(profile, home))
    with locked(path / 'profile.lock'):
        record = read_json(path / 'token.json')
        info = validate_profile(record)
        try:
            credentials = Credentials.from_authorized_user_info(info, scopes=[SCOPE])
            if not credentials.valid:
                credentials.refresh(Request())
            if account_identity(credentials) != record['account']:
                raise ValueError()
            refreshed = dict(record, credentials=json.loads(credentials.to_json()))
            validate_profile(refreshed)
            write_json(path / 'token.json', refreshed)
        except Exception:
            raise Diagnostic('reauthorization_required', 'Could not validate this Google account profile.', 'Check auth setup or explicitly log out and log in again.') from None
    # google-auth ordinarily retries a request after refreshing on 401. Disable
    # that replay: the journal decides recovery for every failed mutation.
    with AuthorizedSession(credentials, max_refresh_attempts=0) as session:
        session.drive_sync_identity = {'account': record['account'], 'client': credentials.client_id}
        yield session
