"""Reviewed closure of revision-guarded native updates with unchanged read-back."""
from dataclasses import asdict, dataclass

from .document_model import read_document
from .executor import load_prepared
from .folders import binding_map
from .google import fingerprint
from .index import Diagnostic
from .state import write_json
from .storage import load_index


@dataclass(frozen=True)
class UnchangedPlan:
    index_id: str
    index_digest: str
    operation_id: str
    source_id: str
    remote_id: str
    observation: dict
    journal_hash: str
    preparation_hash: str
    binding_hash: str

    @property
    def digest(self):
        return fingerprint(asdict(self))


def plan_unchanged(index_path, store, remote, operation_id):
    loaded = load_index(index_path)
    if loaded.model.id != store.index_id:
        raise Diagnostic('wrong_state', 'Index and state differ.', 'Use the matching state namespace.')
    store.bind_account(remote.identity)
    intent = next((i for i in store.pending() if i.id == operation_id), None)
    if intent is None or intent.kind != 'push':
        raise Diagnostic('closure_ineligible', 'Only pending native content pushes can be closed this way.',
                         'Use normal recovery; never dismiss an uncertain create.')
    prepared = load_prepared(store, intent)
    binding = prepared.binding
    if (binding.get('kind') != 'file' or binding.get('storage') != 'google-doc'
            or binding.get('effect_kind') or not intent.remote_id
            or binding.get('remote_id') != intent.remote_id):
        raise Diagnostic('closure_ineligible', 'This effect is not a native revision-guarded content push.',
                         'Retain the pending journal and inspect its effect type.')
    current = asdict(read_document(remote.observe_document(intent.remote_id)).snapshot)
    if current != binding.get('prior_remote'):
        raise Diagnostic('remote_not_unchanged', 'Remote snapshot differs from the pre-write snapshot.',
                         'Recover or inspect both versions; do not dismiss this pending operation.')
    return UnchangedPlan(store.index_id, loaded.digest, intent.id, intent.source_id,
                         intent.remote_id, current, fingerprint(asdict(intent)),
                         fingerprint(asdict(prepared) | {'payload': prepared.payload.hex()}),
                         fingerprint(binding_map(store).get(intent.source_id)))


def close_unchanged(index_path, store, remote, operation_id, expected_digest=None):
    """No remote mutation. Recompute the whole reviewed plan under the state lock."""
    with store.lock():
        plan = plan_unchanged(index_path, store, remote, operation_id)
        if expected_digest is None:
            return plan
        if plan.digest != expected_digest:
            raise Diagnostic('stale_closure', 'Closure inputs changed since review.', 'Preview closure again.')
        intent = next(i for i in store.pending() if i.id == operation_id)
        write_json(store.journals / (intent.id + '.closure.json'),
                   {'plan': asdict(plan), 'authorized_digest': expected_digest})
        write_json(store.journals / (intent.id + '.json'), asdict(intent) | {'status': 'closed_unchanged'})
        return {'closed': intent.id, 'baseline_advanced': False, 'remote_written': False}
