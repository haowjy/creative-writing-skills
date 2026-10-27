"""Reviewed baseline repair for existing identities whose two sides agree."""
from dataclasses import dataclass,asdict
import json
from pathlib import Path
from copy import deepcopy

from .conversion import render
from .document_model import read_document
from .folders import binding_map
from .google import fingerprint
from .index import Diagnostic,resolve
from .layout import plan_layout
from .native_effects import semantic,document_settings
from .planner import LocalSnapshot,Baseline
from .sources import snapshot
from .state import StateStore,read_json
from .storage import load_index,digest
from .sync_plan import observe_file,render_source


@dataclass(frozen=True)
class RebaselinePlan:
    index_id: str
    index_digest: str
    source_id: str
    old_binding_hash: str
    baseline: Baseline
    source_path: str
    source_data: bytes
    remote_text: str | None
    provenance: tuple
    remote_settings: str | None = None

    @property
    def digest(self):
        return fingerprint(dict(index=self.index_id,index_digest=self.index_digest,source=self.source_id,
             old_binding=self.old_binding_hash,baseline=asdict(self.baseline),source_hash=digest(self.source_data),
             remote_text_hash=digest(self.remote_text.encode()) if self.remote_text is not None else None))


def plan_rebaseline(index_path: Path,store: StateStore,remote,source_id: str) -> RebaselinePlan:
    loaded=load_index(index_path)
    if loaded.model.id!=store.index_id:
        raise Diagnostic('wrong_state','Index/state mismatch.','Use the correct state namespace.')
    store.bind_account(remote.identity)
    sources=resolve(loaded.model,index_path)
    bindings=binding_map(store)
    binding=bindings.get(source_id)
    if not binding or binding.get('kind')!='file' or binding.get('incomplete'):
        raise Diagnostic('missing_identity','Rebaseline requires an existing complete file identity.','Restore identity state from backup; do not adopt by name.')
    if any(i.source_id==source_id for i in store.pending()):
        raise Diagnostic('pending_write','Uncertain writes must be recovered before rebaselining.','Run state recover; do not suppress unfinished effects.')
    source=next((s for s in sources if str(s.path)==binding['path']),None)
    if source is None or source.storage!=binding['storage']:
        raise Diagnostic('unselected_binding','Source is unselected or its storage mode changed.','Restore the selected source/storage policy before baseline repair.')
    captured=snapshot(source.path)
    metadata=remote.metadata(binding['remote_id'])
    if metadata.get('id') != binding['remote_id'] or metadata.get('appProperties',{}).get('source')!=source_id:
        raise Diagnostic('identity_mismatch','Remote source marker differs.','Restore the correct identity; never adopt by title.')
    if metadata.get('name')!=binding.get('name') or metadata.get('parents')!=[binding.get('parent')]:
        raise Diagnostic('layout_divergence','Remote layout differs from the bound destination.','Restore layout before baseline repair.')
    provenance=()
    text=None
    settings=None
    if source.storage=='original':
        data,_=remote.read_original(binding['remote_id'])
        observed=observe_file(remote,binding['remote_id'],'original')
        if digest(data)!=captured.digest or observed.content_hash!=captured.digest:
            raise Diagnostic('rebaseline_divergence','Local and remote originals differ.','Reconcile their content before repairing a common baseline.')
        rendered_hash=captured.digest
    else:
        layout=plan_layout(loaded.model,sources,read_json(store.path/'identities.json'))
        rendering,provenance=render_source(source,captured.data,layout,sources,bindings)
        observation=remote.observe_document(binding['remote_id'])
        model=read_document(observation)
        settings=document_settings(observation.document)
        if (not rendering.supported or model.snapshot.comments or model.snapshot.suggestions
                or semantic(rendering.text,rendering.styles)!=semantic(model.text,model.styles)):
            raise Diagnostic('rebaseline_divergence','Content/formatting differs or annotations require review.','Reconcile both sides before baseline repair; no differences will be hidden.')
        observed=model.snapshot
        text=model.text
        rendered_hash=rendering.fingerprint
    if remote.metadata(binding['remote_id']) != metadata:
        raise Diagnostic('rebaseline_remote_race', 'Remote metadata changed during baseline comparison.',
                         'Preview baseline repair again; do not accept observations from different remote states.',
                         str(source.path), destination=binding['remote_id'], operation='rebaseline')
    current = snapshot(source.path)
    if (current.digest, current.device, current.inode, current.mode) != (captured.digest, captured.device, captured.inode, captured.mode):
        raise Diagnostic('rebaseline_source_race', 'Source changed during baseline comparison.',
                         'Pause source edits and preview baseline repair again.', str(source.path), operation='rebaseline')
    if load_index(index_path).digest != loaded.digest:
        raise Diagnostic('rebaseline_index_race', 'Index changed during baseline comparison.',
                         'Reload the index and review baseline repair again.', str(index_path), operation='rebaseline')
    local=LocalSnapshot(source_id,source.root+'/'+source.relative_path,captured.digest,rendered_hash,source.storage)
    return RebaselinePlan(store.index_id,loaded.digest,source_id,fingerprint(binding),Baseline(local,observed),str(source.path),captured.data,text,provenance,settings)


def apply_rebaseline(index_path: Path,store: StateStore,remote,source_id: str,expected_digest: str):
    with store.lock():
        store.bind_account(remote.identity)
        plan=plan_rebaseline(index_path,store,remote,source_id)
        if plan.digest!=expected_digest:
            raise Diagnostic('stale_rebaseline','Baseline repair inputs changed after review.','Preview the repair again.')
        bindings=binding_map(store)
        old=deepcopy(bindings[source_id])
        repaired=deepcopy(old)
        repaired.update(baseline=asdict(plan.baseline),source_blob=store.save_blob(plan.source_data))
        if plan.remote_text is not None:
            repaired['remote_text_blob']=store.save_blob(plan.remote_text.encode())
            repaired['remote_settings']=plan.remote_settings
            repaired['link_provenance']=[asdict(p) for p in plan.provenance]
        repaired.setdefault('baseline_repairs',[]).append(dict(prior_hash=plan.old_binding_hash,
            prior_binding_blob=store.save_blob(json.dumps(old,sort_keys=True).encode())))
        bindings[source_id]=repaired
        store.commit_records({'bindings.json':bindings})
        return dict(rebaselined=True,source_id=source_id,remote_id=plan.baseline.remote.file_id)
