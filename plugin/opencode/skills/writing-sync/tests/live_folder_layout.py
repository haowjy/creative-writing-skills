"""One-shot metadata-only folder repair probe; synthetic left/right tree only."""
from dataclasses import asdict

from drive_sync.application import preview_sync, combined_plan, resolve_reviewed
from drive_sync.document_model import read_document
from drive_sync.google import DOC, FOLDER, fingerprint
from drive_sync.index import Diagnostic
from drive_sync.state import write_json
from drive_sync.storage import load_index


def run_folder_layout(run, remote, authorize):
    marker = run / 'folder-layout-probe.json'
    if marker.exists():
        raise Diagnostic('probe_already_attempted', 'Folder-layout probe was already attempted.',
                         'Inspect retained plans/results; do not repeat a possibly applied move.')
    index = run / 'index.yaml'
    load_index(index)
    plan = combined_plan(preview_sync(index, remote, home=run / 'state'))
    inventory = remote.inventory()
    folders = {m['name']: m for m in inventory if m['mimeType'] == FOLDER}
    docs = [m for m in inventory if m['mimeType'] == DOC]
    if (len(inventory) != 7 or len(folders) != 3 or len(docs) != 4
            or not {'left', 'right'} <= folders.keys()
            or len(plan.operations) != 7 or any(o.direction != 'noop' for o in plan.operations)):
        raise Diagnostic('unexpected_fixture', 'Expected a verified synthetic left/right tree with four Docs.',
                         'Initialize and populate a new disposable fixture; never use real sources.')
    left, right = folders['left'], folders['right']
    if left['parents'] != right['parents'] or len(left['parents']) != 1:
        raise Diagnostic('unexpected_fixture', 'Left and right must share the managed root.', 'Inspect the synthetic tree.')
    root = next((m for m in folders.values() if m['id'] == left['parents'][0]), None)
    if root is None or len(root.get('parents', [])) != 1:
        raise Diagnostic('unexpected_fixture', 'Managed root is missing.', 'Inspect without moving anything.')
    before = {m['id']: asdict(read_document(remote.observe_document(m['id'])).snapshot) for m in docs}
    inventory_ids = sorted(m['id'] for m in inventory)
    evidence = dict(status='attempting', before_docs=before, inventory_ids=inventory_ids, stages=[])
    write_json(marker, evidence)
    for item, name, parent in ((left, 'left-moved', right['id']),
                               (root, root['name'] + ' renamed', root['parents'][0])):
        metadata, etag = remote.metadata_guard(item['id'])
        stage = dict(remote_id=item['id'], source_id=item['appProperties']['source'],
                     before=metadata, desired_name=name, desired_parent=parent, status='attempting')
        evidence['stages'].append(stage)
        write_json(marker, evidence)  # Before the one remote mutation attempt.
        remote.update_layout(item['id'], name=name, parent=parent, before=metadata, etag=etag)
        moved = remote.metadata(item['id'])
        if moved['name'] != name or moved['parents'] != [parent]:
            raise Diagnostic('probe_move_pending', 'Move/rename read-back differs.', 'Inspect; never repeat this metadata mutation blindly.')
        full = combined_plan(preview_sync(index, remote, home=run / 'state'))
        operation = next(o for o in full.operations if o.source_id == stage['source_id'])
        if operation.reason != 'folder_changed' or operation.direction != 'conflict':
            raise Diagnostic('probe_conflict_missing', 'Unexpected folder change was not detected.', 'Stop and inspect the saved metadata.')
        repair = resolve_reviewed(index, remote, stage['source_id'], 'restore-layout', home=run / 'state')
        write_json(run / ('folder-layout-' + item['id'] + '-plan.json'), asdict(repair))
        result = resolve_reviewed(index, remote, stage['source_id'], 'restore-layout', authorize(repair), home=run / 'state')
        write_json(run / ('folder-layout-' + item['id'] + '-result.json'), asdict(result))
        if len(result.files) != 1 or result.files[0].status != 'verified':
            raise Diagnostic('probe_repair_pending', 'Folder restoration is not verified.', 'Use normal state recovery; never recreate the folder.')
        restored = remote.metadata(item['id'])
        if restored['name'] != metadata['name'] or restored['parents'] != metadata['parents']:
            raise Diagnostic('probe_restore_mismatch', 'Restored folder layout differs.', 'Inspect the retained repair plan.')
        stage['status'] = 'verified'
        write_json(marker, evidence)
    after = {m['id']: asdict(read_document(remote.observe_document(m['id'])).snapshot) for m in docs}
    final = combined_plan(preview_sync(index, remote, home=run / 'state'))
    if (fingerprint(after) != fingerprint(before)
            or sorted(m['id'] for m in remote.inventory()) != inventory_ids
            or len(final.operations) != 7 or any(o.direction != 'noop' for o in final.operations)):
        raise Diagnostic('probe_final_mismatch', 'Child snapshots, identities or final no-op plan differ.', 'Inspect retained evidence without overwriting content.')
    evidence.update(status='verified', after_docs=after, final_plan=asdict(final))
    write_json(marker, evidence)
    print('PASS: nested folder move/rename and root rename restored; child Doc snapshots/IDs unchanged; all seven operations no-op.')
