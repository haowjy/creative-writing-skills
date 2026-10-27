"""Scoped Google infrastructure. No automatic write retries or content deletion API."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import re
import uuid

from .index import Diagnostic

DRIVE = 'https://www.googleapis.com/drive/v3'
DOCS = 'https://docs.googleapis.com/v1/documents'
DOC = 'application/vnd.google-apps.document'
FOLDER = 'application/vnd.google-apps.folder'
FIELDS = 'id,name,mimeType,parents,appProperties,ownedByMe,trashed,version'


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', value):
        raise Diagnostic('invalid_remote_id', 'Invalid remote identifier.', 'Restore the correct remote binding.')
    return value


def strong_etag(value: str) -> str:
    """Require one opaque strong entity tag, never wildcard/list/weak guards."""
    if not isinstance(value, str) or not re.fullmatch(r'"[\x21\x23-\x7e]*"', value):
        raise Diagnostic('invalid_etag', 'A single strong quoted ETag is required.',
                         'Acquire a fresh Google metadata guard; never substitute a wildcard or combine revisions.')
    return value


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate_batch_limits(batch: dict) -> None:
    """Local executor bounds, not a claim about Google's published API limits."""
    if len(json.dumps(batch).encode()) > 1_000_000 or len(batch.get('requests', [])) > 500:
        raise Diagnostic('batch_limit', 'Batch exceeds the current safe executor limit.',
                         'Use the journaled multi-batch sync service; retain both versions and do not split requests manually.')


def has_suggestions(value) -> bool:
    if isinstance(value, dict):
        return any((k.startswith('suggested') and bool(v)) or has_suggestions(v) for k, v in value.items())
    return isinstance(value, list) and any(has_suggestions(v) for v in value)


@dataclass(frozen=True)
class DocumentObservation:
    metadata: dict
    document: dict
    comments: tuple[dict, ...]

    @property
    def suggestions(self):
        return has_suggestions(self.document)

    @property
    def revision(self):
        return self.document['revisionId']


class GoogleDrive:
    def __init__(self, session, index_id: str):
        self.session = session
        self.identity = getattr(session, 'drive_sync_identity', None)
        self.index_id = str(uuid.UUID(index_id))

    def request(self, method, url, **kwargs):
        # Session must itself be configured with zero automatic mutation retries.
        try:
            response = self.session.request(method, url, timeout=60, allow_redirects=False, **kwargs)
        except Exception:
            raise Diagnostic('remote_transport', 'Google request did not produce a reliable response.', 'Reconcile journaled writes; do not blindly retry.') from None
        if not 200 <= response.status_code < 300:
            raise Diagnostic('remote_http', f'Google returned HTTP {response.status_code}.', 'For writes, reconcile possible side effects before retrying.')
        return response

    def capabilities(self) -> dict:
        result = self.request('GET', DRIVE + '/about', params={'fields':'importFormats,exportFormats'}).json()
        if not isinstance(result.get('importFormats'), dict) or not isinstance(result.get('exportFormats'), dict):
            raise Diagnostic('unknown_capabilities', 'Account conversion capabilities are unreadable.', 'Check Drive API access; do not assume import or export support.')
        return result

    def inventory(self, operation_id: str | None = None) -> tuple[dict, ...]:
        query = "trashed = false and appProperties has { key='driveSyncIndex' and value='" + self.index_id + "' }"
        if operation_id is not None:
            query += " and appProperties has { key='operation' and value='" + str(uuid.UUID(operation_id)) + "' }"
        results = []
        seen = set()
        identities = set()
        token = None
        def invalid():
            return Diagnostic('invalid_inventory', 'Google returned an invalid ownership inventory.',
                              'Retry the read after checking API access; never infer absence or create from an incomplete listing.',
                              operation='read-inventory')
        for _ in range(1000):
            params = dict(q=query, spaces='drive', pageSize=100, fields=f'kind,nextPageToken,incompleteSearch,files({FIELDS})')
            if token:
                params['pageToken'] = token
            response = self.request('GET', DRIVE + '/files', params=params)
            try:
                page = response.json()
            except ValueError:
                raise invalid() from None
            if not isinstance(page, dict) or page.get('kind') != 'drive#fileList':
                raise invalid()
            if 'incompleteSearch' in page and type(page['incompleteSearch']) is not bool:
                raise invalid()
            if page.get('incompleteSearch'):
                raise Diagnostic('incomplete_inventory', 'Google returned an incomplete ownership search.', 'Retry the read later; do not infer that resources are missing.')
            files = page.get('files', [])
            if not isinstance(files, list):
                raise invalid()
            for item in files:
                self.verify_owner(item)
                file_id = item.get('id')
                if not isinstance(file_id, str) or not file_id or file_id in identities:
                    raise invalid()
                if operation_id is not None and item['appProperties'].get('operation') != str(uuid.UUID(operation_id)):
                    raise invalid()
                identities.add(file_id)
                results.append(item)
            token = page.get('nextPageToken')
            if 'nextPageToken' not in page:
                return tuple(results)
            if not isinstance(token, str) or not token:
                raise invalid()
            if token in seen:
                break
            seen.add(token)
        raise Diagnostic('inventory_limit', 'Ownership search exceeded bounded pagination.', 'Inspect the inventory; no create is safe from this observation.')

    def verify_owner(self, metadata):
        if (not isinstance(metadata, dict) or metadata.get('ownedByMe') is not True
                or type(metadata.get('trashed', False)) is not bool or metadata.get('trashed')
                or not isinstance(metadata.get('appProperties'), dict)
                or metadata.get('appProperties', {}).get('driveSyncIndex') != self.index_id):
            raise Diagnostic('unmanaged_remote', 'Remote object does not match this index ownership.', 'Inspect bindings; never adopt by title.')

    def metadata(self, file_id: str):
        def invalid():
            return Diagnostic('invalid_metadata', 'Metadata response is malformed or belongs to a different file.',
                              'Read the bound object again; do not adopt another object from this response.',
                              destination=file_id, operation='read-metadata')
        response = self.request('GET', DRIVE + '/files/' + identifier(file_id), params={'fields': FIELDS})
        try:
            result = response.json()
        except ValueError:
            raise invalid() from None
        if not isinstance(result, dict) or result.get('id') != file_id:
            raise invalid()
        self.verify_owner(result)
        return result

    def inspect_parent(self, file_id: str) -> dict:
        """A granted destination folder. Not an index-owned object."""
        def invalid():
            return Diagnostic('invalid_parent', 'Destination is not an owned untrashed folder.',
                              'Pick a Drive folder with auth pick-folder, or use a verified mirrored parent.',
                              destination=file_id, operation='read-parent')
        response = self.request('GET', DRIVE + '/files/' + identifier(file_id), params={'fields': FIELDS})
        try:
            result = response.json()
        except ValueError:
            raise invalid() from None
        if (not isinstance(result, dict) or result.get('id') != file_id
                or result.get('mimeType') != FOLDER or result.get('ownedByMe') is not True
                or result.get('trashed') is True):
            raise invalid()
        return result

    def document(self, file_id: str):
        def invalid():
            return Diagnostic('invalid_document', 'Document observation lacks valid identity or revision.',
                              'Read again; do not update from an incomplete observation.',
                              destination=file_id, operation='read-document')
        response = self.request('GET', DOCS + '/' + identifier(file_id), params={
            'includeTabsContent': 'true', 'suggestionsViewMode': 'SUGGESTIONS_INLINE'})
        try:
            result = response.json()
        except ValueError:
            raise invalid() from None
        if (not isinstance(result, dict) or not isinstance(result.get('revisionId'), str)
                or not result['revisionId'] or result.get('documentId') != file_id):
            raise invalid()
        return result

    def comments(self, file_id: str) -> tuple[dict, ...]:
        results = []
        seen = set()
        comment_ids = set()
        token = None
        def invalid():
            return Diagnostic('invalid_annotations', 'Google returned an invalid comments observation.',
                              'Read annotations again before syncing; never treat unreadable comments as absent.',
                              destination=file_id, operation='read-comments')
        for _ in range(1000):
            params = dict(fields='kind,nextPageToken,comments(id,resolved,deleted,anchor,quotedFileContent)', pageSize=100)
            if token:
                params['pageToken'] = token
            response = self.request('GET', DRIVE + '/files/' + identifier(file_id) + '/comments', params=params)
            try:
                page = response.json()
            except ValueError:
                raise invalid() from None
            # Repeated fields may be omitted when empty. Require the requested
            # resource discriminator instead of accepting an arbitrary {} as empty.
            if not isinstance(page, dict) or page.get('kind') != 'drive#commentList':
                raise invalid()
            comments = page.get('comments', [])
            if not isinstance(comments, list):
                raise invalid()
            for comment in comments:
                if (not isinstance(comment, dict)
                        or not isinstance(comment.get('id'), str) or not comment['id']
                        or any(type(comment[field]) is not bool for field in ('deleted', 'resolved') if field in comment)):
                    raise invalid()
                if comment['id'] in comment_ids:
                    raise invalid()  # Pagination raced; do not certify completeness.
                comment_ids.add(comment['id'])
            results.extend(comments)
            token = page.get('nextPageToken')
            if 'nextPageToken' not in page:
                return tuple(results)
            if not isinstance(token, str) or not token:
                raise invalid()
            if token in seen:
                break
            seen.add(token)
        raise Diagnostic('annotation_limit', 'Comments could not be read completely.', 'Do not treat unreadable annotations as absent.')

    def observe_document(self, file_id: str) -> DocumentObservation:
        # Newly written resources can settle across reads. Discard raced reads,
        # never retry a mutation, and retain a strict bound on observations.
        for _ in range(3):
            before = self.metadata(file_id)
            first = self.document(file_id)
            comments = self.comments(file_id)
            second = self.document(file_id)
            after = self.metadata(file_id)
            if before == after and first == second:
                return DocumentObservation(after, second, comments)
        raise Diagnostic('remote_race', 'Google document changed during bounded observations.', 'Discard this snapshot and preview again.')

    def create(self, name: str, mime: str, source_id: str, operation_id: str,
               parent: str | None = None, data: bytes | None = None, import_mime: str | None = None):
        properties = dict(driveSyncIndex=self.index_id, source=str(uuid.UUID(source_id)), operation=str(uuid.UUID(operation_id)))
        metadata = dict(name=name, mimeType=mime, appProperties=properties)
        if parent:
            try:
                self.metadata(parent)
            except Diagnostic as exc:
                if exc.code != 'unmanaged_remote':
                    raise
                self.inspect_parent(parent)
            metadata['parents'] = [identifier(parent)]
        if data is None:
            return self.request('POST', DRIVE + '/files', params={'fields': FIELDS}, json=metadata).json()
        boundary = 'drive_sync_' + uuid.uuid4().hex
        if not import_mime or '\r' in import_mime or '\n' in import_mime:
            raise Diagnostic('invalid_mime', 'Upload MIME type is invalid.', 'Use a supported format adapter.')
        body = (f'--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'.encode()
                + json.dumps(metadata).encode() + f'\r\n--{boundary}\r\nContent-Type: {import_mime}\r\n\r\n'.encode()
                + data + f'\r\n--{boundary}--\r\n'.encode())
        return self.request('POST', 'https://www.googleapis.com/upload/drive/v3/files',
                            params={'uploadType': 'multipart', 'fields': FIELDS},
                            headers={'Content-Type': f'multipart/related; boundary={boundary}'}, data=body).json()

    def update_document(self, observation: DocumentObservation, batch: dict):
        self.verify_owner(observation.metadata)
        if observation.suggestions or any(not c.get('deleted', False) for c in observation.comments):
            raise Diagnostic('annotations_protected', 'Document has comments or suggestions.', 'Review annotations before destructive replacement.')
        if batch.get('writeControl') != {'requiredRevisionId': observation.revision}:
            raise Diagnostic('unguarded_write', 'Batch lacks the observed required revision.', 'Rebuild the batch from a fresh observation.')
        validate_batch_limits(batch)
        return self.request('POST', DOCS + '/' + identifier(observation.metadata['id']) + ':batchUpdate', json=batch).json()

    def export_document(self, file_id: str, mime: str, max_bytes: int = 10_000_000) -> tuple[bytes, DocumentObservation]:
        before = self.observe_document(file_id)
        response = self.request('GET', DRIVE + '/files/' + identifier(file_id) + '/export',
                                params={'mimeType': mime}, stream=True)
        try:
            chunks, size = [], 0
            for chunk in response.iter_content(chunk_size=65536):
                size += len(chunk)
                if size > max_bytes:
                    raise Diagnostic('export_limit', 'Export exceeds the configured size limit.', 'Use a supported bounded conversion; no source was replaced.')
                chunks.append(chunk)
            data = b''.join(chunks)
        finally:
            response.close()
        after = self.observe_document(file_id)
        if before != after:
            raise Diagnostic('remote_race', 'Document changed during export.', 'Discard exported bytes and obtain a fresh snapshot.')
        return data, after

    def read_original(self, file_id: str, max_bytes: int = 64 * 1024 * 1024) -> tuple[bytes, dict]:
        for attempt in range(3):
            try:
                return self._read_original_once(file_id, max_bytes)
            except Diagnostic as exc:
                if exc.code != 'remote_race' or attempt == 2:
                    raise

    def _read_original_once(self, file_id: str, max_bytes: int) -> tuple[bytes, dict]:
        before = self.metadata(file_id)
        if before.get('mimeType', '').startswith('application/vnd.google-apps.'):
            raise Diagnostic('not_original', 'Bound object is a native Google resource.', 'Review storage mode and binding; do not download as an original file.')
        response = self.request('GET', DRIVE + '/files/' + identifier(file_id), params={'alt': 'media'}, stream=True)
        try:
            chunks, size = [], 0
            for chunk in response.iter_content(chunk_size=65536):
                size += len(chunk)
                if size > max_bytes:
                    raise Diagnostic('download_limit', 'Original file exceeds the configured size limit.', 'Review the transfer limit before downloading.')
                chunks.append(chunk)
            data = b''.join(chunks)
        finally:
            response.close()
        after = self.metadata(file_id)
        if before != after:
            raise Diagnostic('remote_race', 'Original file changed during download.', 'Discard downloaded bytes and preview again.')
        return data, after

    def original_etag(self, file_id: str) -> str:
        self.metadata(file_id)
        result = self.request('GET', 'https://www.googleapis.com/drive/v2/files/' + identifier(file_id),
                              params={'fields': 'id,etag,mimeType'}).json()
        if result.get('id') != file_id or result.get('mimeType', '').startswith('application/vnd.google-apps.') or not result.get('etag'):
            raise Diagnostic('unguarded_original', 'Original-file ETag is unavailable or resource is native.', 'Do not use media replacement for Google Docs.')
        return strong_etag(result['etag'])

    def update_original(self, file_id: str, data: bytes, etag: str):
        strong_etag(etag)
        metadata = self.metadata(file_id)
        if metadata.get('mimeType', '').startswith('application/vnd.google-apps.'):
            raise Diagnostic('not_original', 'Native Google resources cannot use media replacement.', 'Use revision-controlled Docs requests.')
        return self.request('PUT', 'https://www.googleapis.com/upload/drive/v2/files/' + identifier(file_id),
                            params={'uploadType': 'media'}, headers={'If-Match': etag, 'Content-Type':'application/octet-stream'}, data=data).json()

    def metadata_guard(self, file_id: str) -> tuple[dict, str]:
        before = self.metadata(file_id)
        guard = self.request('GET', 'https://www.googleapis.com/drive/v2/files/' + identifier(file_id),
                             params={'fields':'id,etag'}).json()
        after = self.metadata(file_id)
        if before != after or guard.get('id') != file_id or not guard.get('etag'):
            raise Diagnostic('remote_race', 'Metadata changed while acquiring its conditional guard.', 'Refresh the layout plan before writing.')
        return after, strong_etag(guard['etag'])

    def update_layout(self, file_id: str, *, name: str, parent: str, before: dict, etag: str):
        strong_etag(etag)
        self.verify_owner(before)
        if before.get('id') != file_id or self.metadata(file_id) != before:
            raise Diagnostic('remote_race', 'Layout metadata changed before the guarded update.', 'Refresh and review the layout plan.')
        if before.get('parents', []) != [parent]:
            try:
                destination = self.metadata(parent)
            except Diagnostic as exc:
                if exc.code != 'unmanaged_remote':
                    raise
                try:
                    destination = self.inspect_parent(parent)
                except Diagnostic:
                    # The account's My Drive root is the remaining non-app-created
                    # parent permitted for restoring a managed root folder.
                    destination = self.request('GET', DRIVE + '/files/root',params={'fields':'id,mimeType'}).json()
                    if destination.get('id') != parent:
                        raise Diagnostic('invalid_parent','Destination is neither a granted folder nor the account root.','Pick the destination folder or restore an app-created parent.') from None
            if destination.get('mimeType') != FOLDER:
                raise Diagnostic('invalid_parent', 'Destination is not an owned folder.', 'Use a verified mirrored folder binding.')
        params = {}
        old_parents = before.get('parents', [])
        if old_parents != [parent]:
            params['addParents'] = identifier(parent)
            if old_parents:
                params['removeParents'] = ','.join(identifier(p) for p in old_parents)
        return self.request('PUT', 'https://www.googleapis.com/drive/v2/files/' + identifier(file_id),
                            params=params, headers={'If-Match':etag}, json={'title':name}).json()
