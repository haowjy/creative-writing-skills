"""One-shot lost-response repair probe for a completed synthetic four-format fixture."""
from dataclasses import asdict

from drive_sync.application import preview_sync, combined_plan, apply_reviewed
from drive_sync.batch_repair import repair_batches
from drive_sync.index import Diagnostic
from drive_sync.state import StateStore, write_json
from drive_sync.storage import load_index


def run_batch_repair(run, remote, authorize):
    marker = run / 'batch-lost-repair.json'
    if marker.exists():
        raise Diagnostic('probe_already_attempted', 'This repair probe was already attempted.',
                         'Inspect retained results and use normal recovery; do not repeat the probe.')
    index = run / 'index.yaml'
    model = load_index(index).model
    initial = combined_plan(preview_sync(index, remote, home=run / 'state'))
    source = run / 'notes/b.txt'
    if (len(initial.operations) != 5 or any(o.direction != 'noop' for o in initial.operations)
            or source.read_bytes() != b'Changed text sentence.\r\n'):
        raise Diagnostic('unexpected_fixture', 'Expected the completed four-format synthetic round trip.',
                         'Use a fresh synthetic fixture, not real sources or an interrupted earlier test.')
    write_json(marker, {'status': 'attempting', 'index_id': model.id})
    source.write_bytes(b'x' * 1_010_000 + b'\r\n')
    plan = combined_plan(preview_sync(index, remote, home=run / 'state'))
    pushes = [o for o in plan.operations if o.direction == 'push']
    if len(pushes) != 1 or pushes[0].source_id != next(o.source_id for o in initial.operations if o.local.path == 'notes/b.txt'):
        raise Diagnostic('unexpected_fixture', 'Unexpected write scope in synthetic batch probe.', 'Inspect without applying the plan.')
    file_id = pushes[0].remote.file_id
    original_update = remote.update_document
    calls = []
    def lose_second(observed, batch):
        if observed.metadata['id'] != file_id:
            raise Diagnostic('unexpected_fixture', 'Write targets another Doc.', 'Stop the probe.')
        response = original_update(observed, batch)
        calls.append(response)
        if len(calls) == 2:
            raise TimeoutError('Synthetic loss after Google acknowledged application')
        return response
    remote.update_document = lose_second
    try:
        result = apply_reviewed(index, remote, authorize(plan), home=run / 'state')
    finally:
        remote.update_document = original_update
    write_json(run / 'batch-lost-result.json', asdict(result))
    assert len(calls) == 2 and len([f for f in result.files if f.status == 'pending']) == 1
    store = StateStore(run / 'state', model.id)
    intent = store.pending()[0]
    repair = repair_batches(index, remote, intent.id, home=run / 'state')
    write_json(run / 'batch-repair-plan.json', {'plan': asdict(repair), 'digest': repair.digest})
    result = repair_batches(index, remote, intent.id, repair.digest, home=run / 'state')
    write_json(run / 'batch-repair-result.json', asdict(result))
    assert result.files[0].status == 'verified', result.files[0].reason
    final = combined_plan(preview_sync(index, remote, home=run / 'state'))
    assert len(final.operations) == 5 and all(o.direction == 'noop' for o in final.operations)
    assert source.read_bytes() == b'x' * 1_010_000 + b'\r\n'
    write_json(marker, {'status': 'verified', 'index_id': model.id, 'operation_id': intent.id,
                       'remote_id': file_id, 'lost_response_after_batch': 2,
                       'repair_batches': len(repair.segments), 'source_unchanged_by_repair': True,
                       'final_plan': asdict(final)})
    print('PASS: applied-but-lost intermediate batch repaired through reviewed services; all five operations no-op.')
