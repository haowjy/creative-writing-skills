"""Two-stage installed-package/state test. No Google or credentials are used.

Run seed with a new external directory, reinstall the package, then run verify
with the same directory. The second stage must issue no fake remote mutations.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import uuid

import drive_sync
from drive_sync.application import (
    apply_reviewed, combined_plan, initialize_documents, preview_sync,
)
from drive_sync.planner import Authorization
from drive_sync.storage import Draft, commit
from fake_google import FakeGoogle
from test_index import fixture


def fingerprints(directory):
    return {str(p.relative_to(directory)): sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def authorization(plan):
    return Authorization(plan.digest, plan.index_id,
                         frozenset(o.source_id for o in plan.operations),
                         frozenset(('create', 'push', 'pull')))


def seed(directory):
    directory.mkdir()  # Refuse to reuse or overwrite any existing directory.
    projects = []
    for name in ('first', 'second'):
        project = directory / name
        (project / 'notes').mkdir(parents=True)
        source = project / 'notes' / 'note.md'
        source.write_text(f'{name} independent source.\n', encoding='utf-8')
        raw = fixture()
        raw['id'] = str(uuid.uuid4())
        index = project / 'index.yaml'
        commit(index, Draft(raw), None)
        remote = FakeGoogle()
        plan = initialize_documents(index, remote, home=directory / 'state')
        initialize_documents(index, remote, authorization(plan), home=directory / 'state')
        plan = combined_plan(preview_sync(index, remote, home=directory / 'state'))
        result = apply_reviewed(index, remote, authorization(plan), home=directory / 'state')
        assert all(f.status in ('verified', 'noop') for f in result.files), result
        projects.append(dict(name=name, index_id=raw['id'], files=remote.files,
                             bodies=remote.bodies, styles=remote.styles))
    record = dict(projects=projects, state=fingerprints(directory / 'state'),
                  sources={p['name']: fingerprints(directory / p['name']) for p in projects})
    (directory / 'fixture.json').write_text(json.dumps(record), encoding='utf-8')


def verify(directory):
    record = json.loads((directory / 'fixture.json').read_text(encoding='utf-8'))
    assert len({p['index_id'] for p in record['projects']}) == 2
    assert fingerprints(directory / 'state') == record['state'], 'Reinstall changed state'
    for project in record['projects']:
        root = directory / project['name']
        assert fingerprints(root) == record['sources'][project['name']]
        remote = FakeGoogle()
        for field in ('files', 'bodies', 'styles'):
            setattr(remote, field, project[field])
        plan = combined_plan(preview_sync(root / 'index.yaml', remote, home=directory / 'state'))
        assert all(o.direction == 'noop' for o in plan.operations), plan
        result = apply_reviewed(root / 'index.yaml', remote, authorization(plan), home=directory / 'state')
        assert all(f.status == 'noop' for f in result.files), result
        assert remote.calls == [], 'No-op rerun mutated the remote'
        assert fingerprints(root) == record['sources'][project['name']]
    assert fingerprints(directory / 'state') == record['state'], 'No-op rerun changed durable state'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('seed', 'verify'))
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    package = Path(drive_sync.__file__).resolve().parent
    if 'site-packages' not in package.parts:
        parser.error('Use a noneditable installed package without source PYTHONPATH.')
    before = fingerprints(package)
    (seed if args.stage == 'seed' else verify)(args.directory.resolve())
    assert fingerprints(package) == before, 'Runtime changed installed package'
    print(f'PASS: {args.stage}; installed package, two external projects, isolated persistent state')


if __name__ == '__main__':
    main()
