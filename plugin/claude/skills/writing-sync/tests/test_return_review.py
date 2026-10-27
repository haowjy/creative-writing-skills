from contextlib import nullcontext, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from drive_sync.application import initialize_documents, preview_sync, combined_plan, apply_reviewed
from drive_sync.candidate_review import describe_candidate
from drive_sync.index import Diagnostic
from drive_sync.return_review import preview_return
from drive_sync.state import StateStore, read_json
from drive_sync.storage import Draft, commit
from fake_google import FakeGoogle
from test_index import fixture
from test_epub import book
from test_scoping import authorize


class ReturnReviewTests(unittest.TestCase):
    def test_four_format_private_candidates_and_scoped_apply(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'notes').mkdir()
            originals = {'a.md': b'First.<!-- hidden -->\n', 'b.txt': b'First.\r\n',
                         'c.html': b'<p>First.</p><!-- hidden -->', 'd.epub': book()}
            for name, data in originals.items():
                (root / 'notes' / name).write_bytes(data)
            index = root / 'index.yaml'
            raw = fixture()
            commit(index, Draft(raw), None)
            remote = FakeGoogle()
            plan = initialize_documents(index, remote, home=root / 'state')
            initialize_documents(index, remote, authorize(plan), home=root / 'state')
            plan = combined_plan(preview_sync(index, remote, home=root / 'state'))
            apply_reviewed(index, remote, authorize(plan), home=root / 'state')
            for file_id, metadata in remote.files.items():
                if metadata['name'] in originals:
                    remote.bodies[file_id] = remote.bodies[file_id].replace('First', 'Changed')
                    metadata['version'] = str(int(metadata['version']) + 1)
            remote.calls.clear()
            store = StateStore(root / 'state', raw['id'])
            bindings_before = (store.path / 'bindings.json').read_bytes()
            reviews = []
            for file_id, metadata in remote.files.items():
                if metadata['name'] not in originals:
                    continue
                sid = metadata['appProperties']['source']
                review = preview_return(index, remote, sid, home=root / 'state')
                reviews.append(review)
                report = read_json(review.directory / 'changes.json')
                self.assertEqual((review.directory / 'before.source').read_bytes(), originals[metadata['name']])
                self.assertEqual((root / 'notes' / metadata['name']).read_bytes(), originals[metadata['name']])
                self.assertEqual(report['candidate_hash'], review.candidate_hash)
                self.assertEqual(report['kind'], 'epub-members' if metadata['name'] == 'd.epub' else 'text-diff')
                self.assertEqual(review.directory.stat().st_mode & 0o777, 0o700)
                for artifact in review.directory.iterdir():
                    self.assertEqual(artifact.stat().st_mode & 0o777, 0o600)
                if report['kind'] == 'epub-members':
                    changed = {m['path'] for m in report['members'] if m['change'] != 'unchanged'}
                    self.assertEqual(changed, {'OEBPS/z.xhtml', 'OEBPS/book.opf'})
                else:
                    self.assertIn('Changed', (review.directory / 'source.diff').read_text())
            self.assertEqual(remote.calls, [])
            self.assertEqual((store.path / 'bindings.json').read_bytes(), bindings_before)
            for review in reviews:
                scope = frozenset([review.source_id])
                plan = combined_plan(preview_sync(index, remote, home=root / 'state', source_ids=scope))
                self.assertEqual(plan.digest, review.plan_digest)
                result = apply_reviewed(index, remote, authorize(plan), home=root / 'state', source_ids=scope)
                self.assertTrue(all(f.status in ('verified', 'noop') for f in result.files))
                if review.format != 'epub':
                    self.assertEqual(Path(review.source).read_bytes(), (review.directory / 'candidate.source').read_bytes())
                else:
                    self.assertTrue(review.candidate_may_change_at_apply)
                    comparison = describe_candidate((review.directory / 'candidate.source').read_bytes(), Path(review.source).read_bytes(), 'epub')
                    self.assertTrue(all(m['change'] == 'unchanged' or m['path'] == 'OEBPS/book.opf' for m in comparison.members))
                applied = next(f for f in result.files if f.source_id == review.source_id)
                actual_report = read_json(store.journals / (applied.operation_id + '.review') / 'changes.json')
                from drive_sync.storage import digest
                self.assertEqual(actual_report['candidate_hash'], digest(Path(review.source).read_bytes()))
            with self.assertRaises(Diagnostic) as caught:
                preview_return(index, remote, reviews[0].source_id, home=root / 'state')
            self.assertEqual(caught.exception.code, 'return_review_ineligible')

    def test_accept_remote_candidate_uses_shared_conflict_rules(self):
        from drive_sync.application import resolve_reviewed
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'notes').mkdir()
            source = root / 'notes/a.md'
            source.write_bytes(b'First.<!-- protected -->\n')
            index = root / 'index.yaml'
            commit(index, Draft(fixture()), None)
            remote = FakeGoogle()
            plan = initialize_documents(index, remote, home=root / 'state')
            initialize_documents(index, remote, authorize(plan), home=root / 'state')
            plan = combined_plan(preview_sync(index, remote, home=root / 'state'))
            apply_reviewed(index, remote, authorize(plan), home=root / 'state')
            file_id = next(k for k, m in remote.files.items() if m['name'] == 'a.md')
            sid = remote.files[file_id]['appProperties']['source']
            source.write_bytes(b'Local.<!-- protected -->\n')
            remote.bodies[file_id] = 'Remote.\n'
            remote.files[file_id]['version'] = str(int(remote.files[file_id]['version']) + 1)
            remote.calls.clear()
            with self.assertRaises(Diagnostic):
                preview_return(index, remote, sid, home=root / 'state')
            review = preview_return(index, remote, sid, home=root / 'state', accept_remote=True)
            self.assertEqual(review.resolution, 'accept-remote')
            self.assertEqual(source.read_bytes(), b'Local.<!-- protected -->\n')
            self.assertEqual((review.directory / 'candidate.source').read_bytes(), b'Remote.<!-- protected -->\n')
            self.assertEqual(remote.calls, [])
            plan = resolve_reviewed(index, remote, sid, 'accept-remote', home=root / 'state')
            self.assertEqual(plan.digest, review.plan_digest)
            result = resolve_reviewed(index, remote, sid, 'accept-remote', authorize(plan), home=root / 'state')
            self.assertEqual(result.files[0].status, 'verified')
            self.assertEqual(source.read_bytes(), b'Remote.<!-- protected -->\n')

    def test_diff_bounds_binary_fallback_and_unicode(self):
        self.assertIsNone(describe_candidate(b'a' * 200001, b'b', 'text').diff)
        self.assertEqual(describe_candidate(b'\x00', b'\xff', 'text').kind, 'binary')
        self.assertEqual(describe_candidate(b'not zip', b'not zip', 'epub').kind, 'binary')
        self.assertIn('new', describe_candidate('😀 old\r\n'.encode(), '😀 new\r\n'.encode(), 'text').diff)

    def test_cli_translates_review_without_exposing_source_text(self):
        from drive_sync.cli import main
        from drive_sync.return_review import ReturnReview
        with TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / 'index.yaml'
            commit(index, Draft(fixture()), None)
            review = ReturnReview('index', 'source', '/external/a.md', 'doc', root, 'plan', 'before', 'after', 'markdown', 'google-doc')
            with patch('drive_sync.auth.authorized_session', return_value=nullcontext(object())), \
                    patch('drive_sync.google.GoogleDrive', return_value=object()), \
                    patch('drive_sync.return_review.preview_return', return_value=review) as service, \
                    redirect_stdout(StringIO()) as output:
                self.assertEqual(main(['--index', str(index), 'source', 'preview-return', '--source', 'source']), 0)
            self.assertEqual(json.loads(output.getvalue())['directory'], str(root))
            self.assertEqual(service.call_args.args[2], 'source')
