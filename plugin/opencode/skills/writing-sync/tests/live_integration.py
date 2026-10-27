"""Opt-in synthetic integration using production services and a research token.

No deletes, existing-Doc adoption or real source selection. A persisted fixture
index is reused on later stages; pending writes require normal recovery.
"""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import uuid
import threading

from google.auth.transport.requests import AuthorizedSession, Request
from google.oauth2.credentials import Credentials

from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed, recover_sync, resolve_reviewed
from drive_sync.auth import account_identity, SCOPE, TOKEN_URI
from drive_sync.google import GoogleDrive, DOC, DRIVE, identifier
from drive_sync.document_model import read_document
from drive_sync.index import Diagnostic
from drive_sync.planner import Authorization
from drive_sync.state import write_json
from drive_sync.storage import Draft, commit, load_index
from test_index import fixture
from test_epub import book


def seed_cyclic(run):
    run.mkdir(mode=0o700)
    (run / 'notes').mkdir()
    (run / 'notes/a.md').write_bytes(b'[B](b.md)\n')
    (run / 'notes/b.md').write_bytes(b'[A](a.md)\n')
    raw = fixture()
    raw['id'] = str(uuid.uuid4())
    raw['roots']['notes']['destination_name'] = 'Drive Sync cyclic disposable ' + raw['id']
    commit(run / 'index.yaml', Draft(raw), None)


def verify_cyclic(run, remote):
    """Independent read-only content/link/provenance checks after initialization."""
    from drive_sync.folders import binding_map
    from drive_sync.state import StateStore
    index = load_index(run / 'index.yaml').model
    items = remote.inventory()
    docs = {m['name']: m for m in items if m['mimeType'] == DOC}
    if len(items) != 3 or set(docs) != {'a.md', 'b.md'}:
        raise Diagnostic('unexpected_fixture', 'Expected one folder and two unique cyclic Docs.', 'Inspect without creating or deleting anything.')
    store = StateStore(run / 'state', index.id)
    with store.lock():
        bindings = binding_map(store)
    evidence = []
    for name, target, label in (('a.md', 'b.md', 'B'), ('b.md', 'a.md', 'A')):
        item = docs[name]
        model = read_document(remote.observe_document(item['id']))
        expected_url = 'https://docs.google.com/document/d/' + docs[target]['id'] + '/edit'
        expected_provenance = [dict(source_href=target, destination_url=expected_url,
                                   target_source_id=docs[target]['appProperties']['source'])]
        binding = bindings[item['appProperties']['source']]
        if (model.text != label + '\n'
                or [s.value for s in model.styles if s.kind == 'link'] != [expected_url]
                or binding.get('link_provenance') != expected_provenance
                or binding.get('incomplete') or not binding.get('baseline')
                or (run / 'notes' / name).read_bytes() != f'[{label}]({target})\n'.encode()):
            raise Diagnostic('cyclic_verification_failed', 'Cyclic content, link or provenance differs.', 'Inspect both copies without rewriting either.')
        evidence.append(dict(name=name, remote_id=item['id'], target=expected_url,
                             provenance=expected_provenance, source_unchanged=True))
    plan = combined_plan(preview_sync(run / 'index.yaml', remote, home=run / 'state'))
    if len(plan.operations) != 3 or any(o.direction != 'noop' for o in plan.operations):
        raise Diagnostic('cyclic_verification_failed', 'Final cyclic preview is not all no-op.', 'Inspect the plan without applying changes.')
    write_json(run / 'cyclic-verification.json', dict(verified=True, files=evidence, final_plan=asdict(plan)))
    print('PASS: both cyclic Doc links and source provenance verified; source bytes unchanged; all no-op.')


def verify_nested(run, remote):
    """Read-only independent checks of the fixed nested synthetic fixture."""
    from drive_sync.state import StateStore
    from drive_sync.folders import binding_map
    index = load_index(run / 'index.yaml').model
    inventory = remote.inventory()
    found = {}
    for name in ('notes', 'level1', 'level2', 'g.md', 'a.md'):
        remote_name = next(root.destination_name for root in index.roots if root.name == 'notes') if name == 'notes' else name
        matches = [item for item in inventory if item['name'] == remote_name]
        if len(matches) != 1:
            raise Diagnostic('unexpected_fixture', 'Nested fixture identity is not unique.', 'Inspect scoped inventory.')
        found[name] = remote.metadata(matches[0]['id'])
    for child, parent in (('level1', 'notes'), ('level2', 'level1'), ('g.md', 'level2')):
        if found[child]['parents'] != [found[parent]['id']]:
            raise Diagnostic('nested_layout_failed', 'Drive parent differs from the synthetic tree.', 'Inspect without relocating anything.')
    doc = read_document(remote.observe_document(found['g.md']['id']))
    url = 'https://docs.google.com/document/d/' + found['a.md']['id'] + '/edit'
    links = [style.value for style in doc.styles if style.kind == 'link']
    store = StateStore(run / 'state', index.id)
    with store.lock():
        binding = binding_map(store)[found['g.md']['appProperties']['source']]
    expected = [{'source_href': '../../a.md', 'destination_url': url,
                 'target_source_id': found['a.md']['appProperties']['source']}]
    source = (run / 'notes/level1/level2/g.md').read_bytes()
    if (doc.text != 'Nested fixture. Read parent.\n' or links != [url]
            or binding.get('link_provenance') != expected
            or source != b'Nested fixture. [Read parent](../../a.md).\n'):
        raise Diagnostic('nested_link_failed', 'Nested text, link or provenance differs.', 'Inspect private fixture evidence; do not overwrite it.')
    write_json(run / 'nested-verification.json', {'metadata': found, 'text': doc.text,
               'links': links, 'provenance': expected, 'source_unchanged': True})
    print('Nested parent chain, Doc link, provenance and unchanged local bytes verified.')


def move_nested(run, remote):
    """One synthetic remote move/rename; ambiguous requests cannot be replayed."""
    marker = run / 'move-nested.json'
    if marker.exists():
        raise Diagnostic('probe_already_attempted', 'Nested move was already attempted.',
                         'Inspect the saved marker and use production recovery/restoration; do not repeat the move.')
    inventory = remote.inventory()
    docs = [m for m in inventory if m['name'] == 'g.md' and m['mimeType'] == DOC]
    parents = [m for m in inventory if m['name'] == 'level1']
    if len(docs) != 1 or len(parents) != 1:
        raise Diagnostic('unexpected_fixture', 'Expected one nested Doc and level1 folder.', 'Inspect scoped fixture inventory.')
    file_id = docs[0]['id']
    before = read_document(remote.observe_document(file_id))
    metadata, etag = remote.metadata_guard(file_id)
    record = {'file_id': file_id, 'source_id': metadata['appProperties']['source'],
              'before': metadata, 'content_hash': before.snapshot.content_hash,
              'desired_name': 'g-moved.md', 'desired_parent': parents[0]['id']}
    write_json(marker, record)
    remote.update_layout(file_id, name=record['desired_name'], parent=record['desired_parent'],
                         before=metadata, etag=etag)
    actual = remote.observe_document(file_id)
    if (actual.metadata['name'] != record['desired_name']
            or actual.metadata['parents'] != [record['desired_parent']]
            or read_document(actual).snapshot.content_hash != record['content_hash']):
        raise Diagnostic('probe_move_pending', 'Nested move read-back differs.', 'Inspect without replaying the request.')
    write_json(marker, record | {'verified': True})
    print('Disposable move/rename verified; Doc content unchanged and sync baselines untouched.')


def authorize(plan):
    return Authorization(plan.digest, plan.index_id,
                         frozenset(o.source_id for o in plan.operations),
                         frozenset(('create', 'push', 'pull')))


def rebind_file(run, remote):
    """One-shot local rename, reviewed rebind and production layout restore."""
    from drive_sync.folders import binding_map
    from drive_sync.rebind import plan_rebind, apply_rebind
    from drive_sync.state import StateStore
    marker = run / 'rebind-file.json'
    if marker.exists():
        raise Diagnostic('probe_already_attempted', 'The rebind probe has already started.',
                         'Inspect its journal and retained evidence; do not replay it.')
    source = run / 'notes/a.md'
    target = run / 'notes/a-renamed.md'
    expected = b'Changed markdown sentence.\n'
    if source.read_bytes() != expected or target.exists() or target.is_symlink():
        raise Diagnostic('unexpected_fixture', 'The local rebind fixture differs.', 'Inspect without moving files.')
    inventory = remote.inventory()
    matches = [m for m in inventory if m['name'] == 'a.md']
    if len(matches) != 1:
        raise Diagnostic('unexpected_fixture', 'Expected one disposable a.md Doc.', 'Inspect scoped inventory.')
    item = matches[0]
    source_id = item['appProperties']['source']
    before = read_document(remote.observe_document(item['id'])).snapshot
    model = load_index(run / 'index.yaml').model
    store = StateStore(run / 'state', model.id)
    with store.lock():
        store.bind_account(remote.identity)
        binding_before = binding_map(store)[source_id]
    write_json(marker, dict(source_id=source_id, remote_id=item['id'],
                           before=asdict(before), binding_before=binding_before, status='attempting'))
    source.rename(target)
    with store.lock():
        plan = plan_rebind(run / 'index.yaml', store, source_id, 'notes', target.name, remote)
    write_json(run / 'rebind-plan.json', asdict(plan))
    apply_rebind(plan, run / 'index.yaml', store, plan.digest, 'notes', target.name, remote)
    resolution = resolve_reviewed(run / 'index.yaml', remote, source_id, 'restore-layout', home=run / 'state')
    write_json(run / 'rebind-layout-plan.json', asdict(resolution))
    result = resolve_reviewed(run / 'index.yaml', remote, source_id, 'restore-layout',
                              authorize(resolution), home=run / 'state')
    write_json(run / 'rebind-layout-result.json', asdict(result))
    if not result.files or any(f.status not in ('verified', 'noop') for f in result.files):
        raise Diagnostic('probe_rebind_pending', 'Layout restoration did not verify.', 'Use normal journal recovery; do not replay this probe.')
    after = remote.observe_document(item['id'])
    remaining = remote.inventory()
    if (after.metadata['name'] != target.name or after.metadata['parents'] != item['parents']
            or read_document(after).snapshot.content_hash != before.content_hash
            or {m['id'] for m in inventory} != {m['id'] for m in remaining}
            or source.exists() or target.read_bytes() != expected):
        raise Diagnostic('probe_rebind_failed', 'Rebind identity/content verification failed.', 'Inspect both sides without further writes.')
    final_plan = combined_plan(preview_sync(run / 'index.yaml', remote, home=run / 'state'))
    if any(o.direction != 'noop' for o in final_plan.operations):
        raise Diagnostic('probe_rebind_failed', 'Post-rebind preview is not entirely unchanged.', 'Inspect the plan before any further apply.')
    write_json(run / 'rebind-verification.json', dict(verified=True, remote_id=item['id'],
               no_duplicates=True, source_bytes_unchanged=True, content_unchanged=True,
               final_plan=asdict(final_plan)))
    print('PASS: renamed local source retains the same Doc ID and content; no duplicates; final preview all no-op.')


def replace_storage(run, remote, storage):
    """One-shot reviewed representation replacement, retaining every old object."""
    from drive_sync.folders import binding_map
    from drive_sync.state import StateStore
    from drive_sync.sync_plan import observe_file
    marker = run / ('replace-' + storage + '.json')
    if marker.exists():
        raise Diagnostic('probe_already_attempted', 'This storage replacement probe has already started.',
                         'Inspect retained plans and recover uncertain creates; do not replay the probe.')
    loaded = load_index(run / 'index.yaml')
    source = run / 'notes/a-renamed.md'
    expected = b'Changed markdown sentence.\n'
    if source.read_bytes() != expected:
        raise Diagnostic('unexpected_fixture', 'Storage fixture bytes differ.', 'Inspect without editing sources.')
    store = StateStore(run / 'state', loaded.model.id)
    with store.lock():
        store.bind_account(remote.identity)
        matches = [(sid, b) for sid, b in binding_map(store).items() if b.get('path') == str(source)]
    if len(matches) != 1 or matches[0][1]['storage'] == storage:
        raise Diagnostic('unexpected_fixture', 'Expected one active binding in the other storage mode.', 'Inspect state without changing identities.')
    sid, before = matches[0]
    inventory_before = remote.inventory()
    old_snapshot = observe_file(remote, before['remote_id'], before['storage'])
    write_json(marker, dict(status='attempting', old_binding=before, old_snapshot=asdict(old_snapshot)))
    raw = loaded.raw
    raw['policy']['overrides'] = [o for o in raw['policy']['overrides']
                                 if not (o['root'] == 'notes' and o['glob'] == source.name)]
    raw['policy']['overrides'].append(dict(root='notes', glob=source.name, storage=storage))
    commit(run / 'index.yaml', Draft(raw), loaded.digest)
    plan = resolve_reviewed(run / 'index.yaml', remote, sid, 'replace-storage', home=run / 'state')
    write_json(run / ('replace-' + storage + '-plan.json'), asdict(plan))
    result = resolve_reviewed(run / 'index.yaml', remote, sid, 'replace-storage', authorize(plan), home=run / 'state')
    write_json(run / ('replace-' + storage + '-result.json'), asdict(result))
    if len(result.files) != 1 or result.files[0].status != 'verified':
        raise Diagnostic('probe_replacement_pending', 'The new representation has not verified.',
                         'Use normal journal recovery; never retry the create blindly.')
    with store.lock():
        after = binding_map(store)[sid]
    old_ids = {m['id'] for m in inventory_before}
    new_ids = {m['id'] for m in remote.inventory()}
    retained = [{k: v for k, v in before.items() if k != 'retained_bindings'}]
    if (after['remote_id'] in old_ids or new_ids != old_ids | {after['remote_id']}
            or after['storage'] != storage
            or after['retained_bindings'] != before.get('retained_bindings', []) + retained
            or observe_file(remote, before['remote_id'], before['storage']) != old_snapshot
            or source.read_bytes() != expected):
        raise Diagnostic('probe_replacement_failed', 'Old representation or binding retention differs.', 'Inspect private evidence; do not delete objects.')
    if storage == 'original':
        if remote.read_original(after['remote_id'])[0] != expected:
            raise Diagnostic('probe_replacement_failed', 'Original replacement bytes differ.', 'Inspect without overwriting either representation.')
    elif read_document(remote.observe_document(after['remote_id'])).text != expected.decode():
        raise Diagnostic('probe_replacement_failed', 'Replacement Doc text differs.', 'Inspect without overwriting either representation.')
    final = combined_plan(preview_sync(run / 'index.yaml', remote, home=run / 'state'))
    if any(o.direction != 'noop' for o in final.operations):
        raise Diagnostic('probe_replacement_failed', 'Post-replacement preview is not entirely no-op.', 'Inspect the current plan without applying it.')
    write_json(run / ('replace-' + storage + '-verified.json'), dict(verified=True,
               old_remote_id=before['remote_id'], new_remote_id=after['remote_id'],
               retained_count=len(after['retained_bindings']), final_plan=asdict(final)))
    print('PASS: storage replacement verified; old object/binding retained; source unchanged; final preview all no-op.')


def edit_remote(run, remote, *, needle='First', replacement='Changed', name=None, prefix='edit-'):
    """Simulate a human text edit, without touching sync baselines."""
    for item in remote.inventory():
        if item['mimeType'] != DOC:
            continue
        if name is not None and item['name'] != name:
            continue
        marker = run / (prefix + item['id'] + '.json')
        observation = remote.observe_document(item['id'])
        model = read_document(observation)
        if marker.exists():
            record = json.loads(marker.read_text())
            if model.text != record['desired']:
                raise Diagnostic('probe_edit_pending', 'Earlier test edit is not verified.',
                                 'Inspect this same disposable Doc; do not repeat the edit.')
            continue
        if model.text.count(needle) != 1:
            raise Diagnostic('unexpected_fixture', 'Synthetic text differs from the expected fixture.',
                             'Inspect the disposable test data before further edits.')
        record = {'before': model.text, 'desired': model.text.replace(needle, replacement),
                  'remote_id': item['id'], 'revision': model.snapshot.revision}
        write_json(marker, record)  # Persist before the one mutation attempt.
        batch = {'writeControl': {'requiredRevisionId': model.snapshot.revision},
                 'requests': [{'replaceAllText': {
                     'containsText': {'text': needle, 'matchCase': True},
                     'replaceText': replacement}}]}
        remote.update_document(observation, batch)
        actual = read_document(remote.observe_document(item['id']))
        if actual.text != record['desired']:
            raise Diagnostic('probe_edit_pending', 'Test edit read-back differs.',
                             'Inspect the disposable Doc; do not replay the write.')
    print('Synthetic remote edits verified; local baselines were not changed.')


def edit_original(run, remote):
    matches = [m for m in remote.inventory() if m['name'] == 'e.bin']
    if len(matches) != 1:
        raise Diagnostic('unexpected_fixture', 'Expected one disposable e.bin.', 'Inspect the test index inventory.')
    file_id = matches[0]['id']
    marker = run / ('edit-original-' + file_id + '.json')
    expected = b'\x00Local binary edit\r\n\xff'
    desired = b'\x00Remote binary edit\r\n\xff'
    data, _ = remote.read_original(file_id)
    if marker.exists():
        if data != desired:
            raise Diagnostic('probe_edit_pending', 'Earlier binary edit is unverified.', 'Inspect it; do not retry.')
        return
    if data != expected:
        raise Diagnostic('unexpected_fixture', 'Binary fixture differs from expected bytes.', 'Inspect before editing.')
    etag = remote.original_etag(file_id)
    write_json(marker, {'remote_id': file_id, 'before': expected.hex(), 'desired': desired.hex(), 'etag': etag})
    remote.update_original(file_id, desired, etag)
    data, _ = remote.read_original(file_id)
    if data != desired:
        raise Diagnostic('probe_edit_pending', 'Binary edit read-back differs.', 'Inspect before any further writes.')
    print('Synthetic remote binary edit verified; sync baselines unchanged.')


def add_comment(run, remote):
    matches = [m for m in remote.inventory() if m['name'] == 'c.html' and m['mimeType'] == DOC]
    if len(matches) != 1:
        raise Diagnostic('unexpected_fixture', 'Expected one disposable HTML Doc.', 'Inspect the scoped test inventory.')
    file_id = identifier(matches[0]['id'])
    marker = run / ('comment-' + file_id + '.json')
    if marker.exists():
        record = json.loads(marker.read_text())
    else:
        if remote.comments(file_id):
            raise Diagnostic('unexpected_fixture', 'Disposable Doc already has comments.', 'Inspect; do not add duplicates.')
        record = {'remote_id': file_id, 'message': 'Disposable integration annotation ' + str(uuid.uuid4())}
        write_json(marker, record)
        response = remote.request('POST', DRIVE + '/files/' + file_id + '/comments',
                                  params={'fields': 'id'}, json={'content': record['message']}).json()
        record['comment_id'] = response['id']
        write_json(marker, record)
    if not record.get('comment_id') or not any(c['id'] == record['comment_id'] for c in remote.comments(file_id)):
        raise Diagnostic('probe_comment_pending', 'Test comment is unverified.', 'Inspect this Doc; never repeat the create blindly.')
    source = run / 'notes/c.html'
    before = b'<p>Changed HTML sentence.</p><!-- retained -->'
    after = b'<p>Local annotated conflict.</p><!-- retained -->'
    if source.read_bytes() == before:
        source.write_bytes(after)
    elif source.read_bytes() != after:
        raise Diagnostic('unexpected_fixture', 'Local HTML differs from the fixture.', 'Inspect before editing.')
    print('Synthetic comment verified and local change prepared; no Doc content overwritten.')


def stale_original(run, remote):
    matches = [m for m in remote.inventory() if m['name'] == 'e.bin']
    if len(matches) != 1:
        raise Diagnostic('unexpected_fixture', 'Expected one disposable binary file.', 'Inspect the scoped inventory.')
    file_id = matches[0]['id']
    marker = run / ('stale-original-' + file_id + '.json')
    if marker.exists():
        raise Diagnostic('probe_already_attempted', 'Stale-write probe was already attempted.', 'Inspect its result; do not repeat it.')
    old = json.loads((run / ('edit-original-' + file_id + '.json')).read_text())
    before, metadata = remote.read_original(file_id)
    if before != b'\x00Remote binary edit\r\n\xff' or old['etag'] == remote.original_etag(file_id):
        raise Diagnostic('unexpected_fixture', 'Fixture or stale ETag precondition differs.', 'Inspect before probing.')
    record = {'remote_id': file_id, 'before': before.hex(), 'metadata_before': metadata, 'result': 'attempting'}
    write_json(marker, record)
    try:
        remote.update_original(file_id, b'STALE WRITE MUST NOT LAND', old['etag'])
        outcome = 'unexpected_success'
    except Diagnostic as exc:
        outcome = exc.code + ': ' + exc.reason
    after, after_metadata = remote.read_original(file_id)
    record.update(result=outcome, bytes_unchanged=after == before, metadata_unchanged=after_metadata == metadata)
    write_json(marker, record)
    if outcome != 'remote_http: Google returned HTTP 412.' or after != before or after_metadata != metadata:
        raise Diagnostic('stale_guard_failed', 'Conditional-write probe did not prove unchanged rejection.', 'Stop original-file writes and inspect the private probe result.')
    print('PASS: production original-file adapter rejected stale ETag with HTTP 412; bytes and metadata unchanged.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('seed', 'seed-cyclic', 'verify-cyclic', 'seed-original', 'seed-nested', 'verify-nested', 'move-nested', 'restore-nested', 'rebind-file', 'replace-original', 'replace-doc', 'repair-created-layout', 'repair-created-content', 'initialize', 'sync', 'inspect', 'recover', 'edit-remote', 'edit-rich', 'edit-original', 'make-conflict', 'resolve-conflict', 'add-comment', 'close-unchanged', 'cancel-large', 'resume-large', 'stale-original', 'lost-batch-repair', 'folder-layout', 'seed-styled', 'edit-styled', 'verify-styled'))
    parser.add_argument('--operation')
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--research-token', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    run = args.run.resolve()
    if args.stage == 'seed-styled':
        from live_styled_formats import seed_styled
        seed_styled(run)
        print('Synthetic styled fixture created; no Google requests.')
        return
    if args.stage == 'seed-cyclic':
        seed_cyclic(run)
        print('Synthetic cyclic fixture created; no Google requests.')
        return
    if args.stage == 'seed':
        run.mkdir(mode=0o700)  # Never overwrite an existing fixture.
        (run / 'notes').mkdir()
        for name, data in {'a.md': b'First markdown sentence.\n',
                           'b.txt': b'First text sentence.\r\n',
                           'c.html': b'<p>First HTML sentence.</p><!-- retained -->',
                           'd.epub': book()}.items():
            (run / 'notes' / name).write_bytes(data)
        raw = fixture()
        raw['id'] = str(uuid.uuid4())
        raw['roots']['notes']['destination_name'] = 'Drive Sync disposable ' + raw['id']
        commit(run / 'index.yaml', Draft(raw), None)
        print('Synthetic fixture created; no Google requests.')
        return
    if args.stage == 'seed-original':
        loaded = load_index(run / 'index.yaml')
        if (run / 'notes/e.bin').exists():
            parser.error('Original-file fixture already exists')
        raw = loaded.raw
        raw['policy']['overrides'].append({'root': 'notes', 'glob': 'e.bin', 'storage': 'original'})
        commit(run / 'index.yaml', Draft(raw), loaded.digest)
        with (run / 'notes/e.bin').open('xb') as output:
            output.write(b'\x00Original fixture\r\n\xff')
        print('Synthetic original-file fixture selected; no Google requests.')
        return
    if args.stage == 'seed-nested':
        load_index(run / 'index.yaml')
        directory = run / 'notes/level1/level2'
        directory.mkdir(parents=True)
        with (directory / 'g.md').open('xb') as output:
            output.write(b'Nested fixture. [Read parent](../../a.md).\n')
        print('Synthetic nested source created; no Google requests.')
        return
    if not args.research_token or not args.apply:
        parser.error('Google stages require --research-token and explicit --apply')
    model = load_index(run / 'index.yaml').model
    credentials = Credentials.from_authorized_user_file(str(args.research_token.expanduser()))
    if credentials.token_uri != TOKEN_URI or set(credentials.scopes or ()) != {SCOPE}:
        raise Diagnostic('wrong_scope', 'Research token scope or endpoint differs.', 'Use the dedicated drive.file profile.')
    if not credentials.valid:
        credentials.refresh(Request())
    account = account_identity(credentials)
    with AuthorizedSession(credentials, max_refresh_attempts=0) as session:
        session.drive_sync_identity = {'account': account, 'client': credentials.client_id}
        remote = GoogleDrive(session, model.id)
        if args.stage == 'verify-styled':
            from live_styled_formats import verify_styled
            verify_styled(run, remote)
            return
        if args.stage == 'folder-layout':
            from live_folder_layout import run_folder_layout
            run_folder_layout(run, remote, authorize)
            return
        if args.stage == 'lost-batch-repair':
            from live_batch_repair import run_batch_repair
            run_batch_repair(run, remote, authorize)
            return
        if args.stage == 'verify-cyclic':
            verify_cyclic(run, remote)
            return
        if args.stage in ('replace-original', 'replace-doc'):
            replace_storage(run, remote, 'original' if args.stage == 'replace-original' else 'google-doc')
            return
        if args.stage == 'rebind-file':
            rebind_file(run, remote)
            return
        if args.stage == 'verify-nested':
            verify_nested(run, remote)
            return
        if args.stage == 'move-nested':
            move_nested(run, remote)
            return
        if args.stage == 'restore-nested':
            from drive_sync.state import read_json
            record = read_json(run / 'move-nested.json')
            plan = resolve_reviewed(run / 'index.yaml', remote, record['source_id'], 'restore-layout', home=run / 'state')
            write_json(run / 'restore-nested-plan.json', asdict(plan))
            result = resolve_reviewed(run / 'index.yaml', remote, record['source_id'], 'restore-layout', authorize(plan), home=run / 'state')
        elif args.stage in ('repair-created-layout', 'repair-created-content'):
            from drive_sync.create_repair import repair_created_layout, repair_created_content
            service = repair_created_layout if args.stage == 'repair-created-layout' else repair_created_content
            if not args.operation:
                parser.error('repair-created-* requires --operation')
            plan = service(run / 'index.yaml', remote, args.operation, home=run / 'state')
            write_json(run / (args.stage + '-' + args.operation + '-plan.json'), asdict(plan))
            result = service(run / 'index.yaml', remote, args.operation, plan.digest, home=run / 'state')
        elif args.stage == 'initialize':
            plan = initialize_documents(run / 'index.yaml', remote, home=run / 'state')
            result = initialize_documents(run / 'index.yaml', remote, authorize(plan), home=run / 'state')
        elif args.stage == 'sync':
            plan = combined_plan(preview_sync(run / 'index.yaml', remote, home=run / 'state'))
            result = apply_reviewed(run / 'index.yaml', remote, authorize(plan), home=run / 'state')
        elif args.stage == 'recover':
            result = recover_sync(run / 'index.yaml', remote, home=run / 'state')
        elif args.stage == 'edit-remote':
            edit_remote(run, remote)
            result = None
        elif args.stage == 'edit-styled':
            edit_remote(run, remote, needle='bold', replacement='brave', prefix='edit-styled-')
            result = None
        elif args.stage == 'edit-rich':
            edit_remote(run, remote, needle='bold', replacement='brave', name='a.md', prefix='edit-rich-')
            result = None
        elif args.stage == 'edit-original':
            edit_original(run, remote)
            result = None
        elif args.stage == 'add-comment':
            add_comment(run, remote)
            result = None
        elif args.stage == 'stale-original':
            stale_original(run, remote)
            result = None
        elif args.stage == 'cancel-large':
            source = run / 'notes/b.txt'
            expected = ('😀' * 90000 + '\r\n').encode()
            desired = ('😺' * 90000 + '\r\n').encode()
            if source.read_bytes() == expected:
                source.write_bytes(desired)
            elif source.read_bytes() != desired:
                raise Diagnostic('unexpected_fixture', 'Large source differs from the synthetic fixture.', 'Inspect before continuing.')
            token = threading.Event()
            update = remote.update_document
            def cancel_after_write(observation, batch):
                response = update(observation, batch)
                token.set()
                return response
            remote.update_document = cancel_after_write
            plan = combined_plan(preview_sync(run / 'index.yaml', remote, home=run / 'state'))
            result = apply_reviewed(run / 'index.yaml', remote, authorize(plan), home=run / 'state', cancellation=token)
        elif args.stage == 'resume-large':
            from drive_sync.batch_resume import resume_batches
            if not args.operation:
                parser.error('resume-large requires --operation')
            plan = resume_batches(run / 'index.yaml', remote, args.operation, home=run / 'state')
            write_json(run / ('resume-plan-' + args.operation + '.json'), asdict(plan))
            result = resume_batches(run / 'index.yaml', remote, args.operation, plan.digest, home=run / 'state')
        elif args.stage == 'make-conflict':
            source = run / 'notes/b.txt'
            if source.read_bytes() == b'Changed text sentence.\r\n':
                source.write_bytes(b'Local conflict sentence.\r\n')
            elif source.read_bytes() != b'Local conflict sentence.\r\n':
                raise Diagnostic('unexpected_fixture', 'Local conflict fixture differs.', 'Inspect before editing.')
            edit_remote(run, remote, needle='Changed', replacement='Remote conflict', name='b.txt', prefix='edit-conflict-')
            result = None
        elif args.stage == 'resolve-conflict':
            matches = [m for m in remote.inventory() if m['name'] == 'b.txt']
            if len(matches) != 1:
                raise Diagnostic('unexpected_fixture', 'Expected one conflict fixture.', 'Inspect inventory.')
            source_id = matches[0]['appProperties']['source']
            plan = resolve_reviewed(run / 'index.yaml', remote, source_id, 'accept-remote', home=run / 'state')
            write_json(run / 'conflict-resolution-plan.json', asdict(plan))
            result = resolve_reviewed(run / 'index.yaml', remote, source_id, 'accept-remote', authorize(plan), home=run / 'state')
        elif args.stage == 'close-unchanged':
            from drive_sync.state import StateStore
            from drive_sync.unchanged import close_unchanged
            if not args.operation:
                parser.error('close-unchanged requires --operation')
            store = StateStore(run / 'state', model.id)
            plan = close_unchanged(run / 'index.yaml', store, remote, args.operation)
            write_json(run / ('closure-plan-' + args.operation + '.json'), asdict(plan))
            closed = close_unchanged(run / 'index.yaml', store, remote, args.operation, plan.digest)
            print(json.dumps(closed))
            result = None
        else:
            result = None
        if result is not None:
            write_json(run / (args.stage + '-result.json'), asdict(result))
            print(json.dumps(asdict(result), indent=2))
        # Scoped to this synthetic index, never an inventory of unrelated Drive.
        for item in remote.inventory():
            if item['mimeType'] == DOC:
                if args.stage == 'inspect':
                    write_json(run / ('raw-' + item['id'] + '.json'),
                               {'metadata_before': remote.metadata(item['id']),
                                'document_before': remote.document(item['id']),
                                'comments': remote.comments(item['id']),
                                'document_after': remote.document(item['id']),
                                'metadata_after': remote.metadata(item['id'])})
                    continue
                observed = remote.observe_document(item['id'])
                write_json(run / ('observation-' + item['id'] + '.json'), asdict(observed))


if __name__ == '__main__':
    try:
        main()
    except Diagnostic as exc:
        print(json.dumps({'error': exc.as_dict()}))
        raise SystemExit(2)
    except Exception:
        print('Integration stopped; inspect private artifacts. No automatic write retry.')
        raise SystemExit(2)
