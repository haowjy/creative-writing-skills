"""Verified empty Doc identities for first-time cross-linked source sets.

Initialization is separately authorized and never counts as content sync. The
next full plan fills the verified empty Docs with revision-controlled updates.
"""
from dataclasses import asdict
from pathlib import Path
import json

from .document_model import read_document
from .creation_identity import unique_created_object, verify_created_identity
from .executor import Prepared,Observation
from .folders import binding_map
from .google import DOC,fingerprint
from .index import Diagnostic
from .planner import LocalSnapshot,Operation,SyncPlan
from .sources import snapshot


def initialization_plan(index_digest,layout,sources,store,remote):
    bindings=binding_map(store)
    inventory=remote.inventory()
    source_map={(s.root,s.relative_path):s for s in sources}
    pending={i.source_id for i in store.pending()}
    missing=any(b.get('kind')=='file' and b.get('path') and not Path(b['path']).exists() and not b.get('missing_acknowledged') for b in bindings.values())
    operations=[]
    for dest in layout.files:
        source=source_map[dest.root,dest.relative_path]
        if source.storage != 'google-doc' or dest.source_id in bindings:
            continue
        captured=snapshot(source.path)
        local=LocalSnapshot(dest.source_id,dest.root+'/'+dest.relative_path,captured.digest,'identity-only','google-doc')
        exists=any(m.get('appProperties',{}).get('source')==dest.source_id for m in inventory)
        if missing:
            operations.append(Operation(dest.source_id,'conflict','possible_source_relocation','Rebind relocated sources or acknowledge their absence before initializing replacements.',local,None,None))
        elif exists or dest.source_id in pending:
            operations.append(Operation(dest.source_id,'conflict','initialization_pending','Recover existing identity creation before trying again.',local,None,None))
        else:
            operations.append(Operation(dest.source_id,'create','initialize_identity','Creates an empty Doc, not a completed reading copy.',local,None,None))
    return SyncPlan(store.index_id,index_digest,tuple(operations))


class InitializationEffects:
    def __init__(self,effects):
        self.effects=effects
        self.store,self.remote=effects.store,effects.remote
    def refresh_plan(self,plan):
        from .folders import folder_plan
        self.effects.folder.expected_index_digest=plan.index_digest
        self.effects.native.expected_digest=plan.index_digest
        current=self.effects.current_digest()
        folders=folder_plan(self.effects.layout,self.store,self.remote,current)
        files=initialization_plan(current,self.effects.layout,self.effects.sources,self.store,self.remote)
        return SyncPlan(self.store.index_id,current,folders.operations+files.operations)
    def prepare(self,operation):
        if operation.source_id in self.effects.folder_ids:
            return self.effects.folder.prepare(operation)
        dest=self.effects.native.destinations[operation.source_id]
        parent=binding_map(self.store).get(dest.parent_id,{}).get('remote_id')
        if not parent:
            raise Diagnostic('parent_pending','Parent folder is unverified.','Complete its creation before initializing the Doc.')
        desired=dict(name=dest.name,parent=parent,source=dest.source_id)
        binding=dict(kind='file',storage='google-doc',incomplete=True,identity_verified=True,
                     effect_kind='initialize',name=dest.name,parent=parent,
                     path=str(self.effects.native.by_id[dest.source_id].path))
        return Prepared(dest.source_id,None,fingerprint(desired),json.dumps(desired).encode(),binding)
    def guard(self,operation):
        if operation.source_id in self.effects.folder_ids:
            return self.effects.folder.guard(operation)
        self.effects.native.guard(operation)
        if any(m.get('appProperties',{}).get('source')==operation.source_id for m in self.remote.inventory()):
            raise Diagnostic('identity_exists','Source identity appeared before initialization.','Refresh or recover; do not create another Doc.')
    def mutate(self,operation,prepared,intent):
        if operation.source_id in self.effects.folder_ids:
            return self.effects.folder.mutate(operation,prepared,intent)
        desired=json.loads(prepared.payload)
        self.remote.create(desired['name'],DOC,intent.source_id,intent.id,parent=desired['parent'])
    def observe(self,intent,prepared):
        if prepared.binding.get('kind')=='folder':
            return self.effects.folder.observe(intent,prepared)
        source = prepared.binding.get('path', '')
        item = unique_created_object(self.remote, intent, DOC, source=source)
        observation = self.remote.observe_document(item['id'])
        verify_created_identity(observation.metadata, intent, DOC, source=source)
        if observation.metadata['id'] != item['id']:
            raise Diagnostic('creation_identity_mismatch', 'Observed Doc differs from the unique creation candidate.',
                             'Inspect both identities; never adopt or recreate by title.', source,
                             destination=item['id'], operation='read-back')
        model=read_document(observation)
        if (model.text or model.styles or model.snapshot.comments or model.snapshot.suggestions
                or not model.snapshot.annotations_readable):
            raise Diagnostic('initialization_content_changed', 'Created Doc is not a verified empty, annotation-free skeleton.',
                             'Preserve its content and inspect the pending initialization; do not overwrite it.',
                             source, destination=item['id'], operation='read-back')
        parents=observation.metadata.get('parents',[])
        actual=dict(name=observation.metadata.get('name'),parent=parents[0] if len(parents)==1 else None,source=intent.source_id)
        return (Observation(fingerprint(actual),dict(remote_id=item['id'],skeleton_remote=asdict(model.snapshot))),)
