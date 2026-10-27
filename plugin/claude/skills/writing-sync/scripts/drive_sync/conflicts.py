"""Private conflict inspection artifacts; inspection never resolves by overwrite."""
from dataclasses import dataclass
from pathlib import Path
import uuid

from .document_model import read_document
from .folders import binding_map
from .index import Diagnostic
from .sources import snapshot
from .state import StateStore, private_directory, write_json
from .storage import atomic_write, digest


@dataclass(frozen=True)
class ConflictReview:
    source_id: str
    directory: Path
    local_hash: str
    base_hash: str
    remote_hash: str
    storage: str
    remote_revision: str


def inspect_conflict(store: StateStore, remote, source_id: str) -> ConflictReview:
    source_id = str(uuid.UUID(source_id))
    with store.lock():
        store.bind_account(remote.identity)
        if getattr(remote, 'index_id', store.index_id) != store.index_id:
            raise Diagnostic('wrong_state', 'Remote adapter and state belong to different indexes.',
                             'Use the matching index and OAuth profile for conflict inspection.')
        binding = binding_map(store).get(source_id)
        if not binding or binding.get('kind') != 'file':
            raise Diagnostic('unknown_binding', 'No file binding exists for this source.', 'Inspect index identities and restore missing state.')
        base = store.load_blob(binding['source_blob'])
        local = snapshot(Path(binding['path']))
        if binding['storage'] == 'original':
            data, metadata = remote.read_original(binding['remote_id'])
            revision = str(metadata['version'])
        else:
            observation = remote.observe_document(binding['remote_id'])
            metadata = observation.metadata
            model = read_document(observation)
            data = model.text.encode()
            revision = model.snapshot.revision
        if (metadata.get('id') != binding['remote_id']
                or metadata.get('appProperties', {}).get('source') != source_id):
            raise Diagnostic('wrong_remote_source', 'Observed remote identity does not match the source binding.',
                             'Restore the correct binding; do not compare or resolve unrelated source versions.',
                             str(local.path), destination=binding['remote_id'], operation='inspect-conflict')
        directory = private_directory(store.path / 'reviews' / str(uuid.uuid4()))
        atomic_write(directory / 'base.source', base)
        atomic_write(directory / 'local.source', local.data)
        atomic_write(directory / ('remote.original' if binding['storage'] == 'original' else 'remote.txt'), data)
        review = ConflictReview(source_id, directory, local.digest, digest(base), digest(data), binding['storage'], revision)
        write_json(directory / 'review.json', dict(source_id=source_id, local_hash=review.local_hash,
                   base_hash=review.base_hash, remote_hash=review.remote_hash, storage=review.storage,
                   remote_revision=revision, candidate_is_source=False))
        return review
