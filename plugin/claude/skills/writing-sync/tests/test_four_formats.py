"""All-format application path with deterministic remote text edits."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from drive_sync.application import initialize_documents,preview_sync,combined_plan,apply_reviewed
from drive_sync.planner import Authorization
from drive_sync.storage import commit,Draft
from drive_sync.conversion import render
from fake_google import FakeGoogle
from test_index import fixture
from test_epub import book


class FourFormatTests(unittest.TestCase):
    def test_initialize_push_pull_preserves_original_formats(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)
            root=path/'notes'
            root.mkdir()
            (root/'a.md').write_bytes(b'---\ntitle: Protected\n---\n\nFirst.<!-- protected -->\n')
            (root/'b.txt').write_bytes(b'First.\r\n')
            (root/'c.html').write_bytes(b'<p id="protected">First.</p><!-- protected -->')
            (root/'d.epub').write_bytes(book())
            index=path/'index.yaml'
            commit(index,Draft(fixture()),None)
            remote=FakeGoogle()
            def authorize(plan):
                return Authorization(plan.digest,plan.index_id,frozenset(o.source_id for o in plan.operations),frozenset(['create','push','pull']))
            initial=initialize_documents(index,remote,home=path/'state')
            initialize_documents(index,remote,authorize(initial),home=path/'state')
            plan=combined_plan(preview_sync(index,remote,home=path/'state'))
            result=apply_reviewed(index,remote,authorize(plan),home=path/'state')
            self.assertTrue(all(f.status in ('noop','verified') for f in result.files),result)
            for file_id,metadata in remote.files.items():
                if metadata['name'] in ('a.md','b.txt','c.html','d.epub'):
                    remote.bodies[file_id]=remote.bodies[file_id].replace('First','Changed')
                    metadata['version']=str(int(metadata['version'])+1)
            plan=combined_plan(preview_sync(index,remote,home=path/'state'))
            self.assertEqual(sum(o.direction=='pull' for o in plan.operations),4)
            result=apply_reviewed(index,remote,authorize(plan),home=path/'state')
            self.assertTrue(all(f.status in ('noop','verified') for f in result.files),result)
            self.assertIn(b'title: Protected',(root/'a.md').read_bytes())
            self.assertIn(b'<!-- protected -->',(root/'a.md').read_bytes())
            self.assertEqual((root/'b.txt').read_bytes(),b'Changed.\r\n')
            self.assertEqual((root/'c.html').read_bytes(),b'<p id="protected">Changed.</p><!-- protected -->')
            self.assertEqual(render((root/'d.epub').read_bytes(),'epub').text,'Changed\nSecond\n')
            self.assertTrue(all(o.direction=='noop' for o in combined_plan(preview_sync(index,remote,home=path/'state')).operations))
