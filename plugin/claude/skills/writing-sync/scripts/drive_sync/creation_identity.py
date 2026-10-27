"""Creation reconciliation never hides mismatched operation-marked candidates."""
from .index import Diagnostic


def verify_created_identity(item, intent, mime: str, *, source: str = '') -> None:
    if (not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id']
            or not isinstance(item.get('appProperties'), dict)
            or item['appProperties'].get('source') != intent.source_id
            or item['appProperties'].get('operation') != intent.id
            or item.get('mimeType') != mime):
        raise Diagnostic('creation_identity_mismatch', 'Created object identity or representation differs from the staged intent.',
                         'Inspect the operation markers and retain the pending journal; do not recreate by title.',
                         source, destination=item.get('id', '') if isinstance(item, dict) else '',
                         operation='read-back')


def unique_created_object(remote, intent, mime: str, *, source: str = '') -> dict:
    matches = remote.inventory(operation_id=intent.id)
    if len(matches) != 1:
        raise Diagnostic('creation_not_found' if not matches else 'ambiguous_identity',
                         'No unique operation-marked object can be verified.',
                         'Inspect all operation-marked candidates; never repeat an uncertain create.',
                         source, operation='read-back')
    item = matches[0]
    verify_created_identity(item, intent, mime, source=source)
    return item
