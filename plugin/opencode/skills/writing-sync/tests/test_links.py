from pathlib import Path
import unittest
from drive_sync.conversion import render, Rendering, Style
from drive_sync.links import rewrite_links, restore_link
from drive_sync.index import Diagnostic


class LinkTests(unittest.TestCase):
    def test_reversible_relative_link(self):
        rendering=render(b'[Other](../other.md)','markdown')
        converted,provenance=rewrite_links(rendering,Path('/project/notes/source.md'),{Path('/project/other.md'):('uuid','doc-id')})
        self.assertTrue(converted.supported)
        self.assertEqual(restore_link(converted.styles[0].value,provenance),'../other.md')
    def test_unselected_fragment_and_filesystem_url_block(self):
        for href in ('missing.md','other.md#part','file:///secret'):
            with self.assertRaises(Diagnostic):
                rewrite_links(Rendering('markdown','link',(Style(1,5,'link',href),)),Path('/project/a.md'),{})
    def test_external_links_are_unchanged(self):
        original=render(b'[Site](https://example.com/page)','markdown')
        converted,provenance=rewrite_links(original,Path('/project/a.md'),{})
        self.assertEqual(converted,original)
        self.assertEqual(provenance,())

    def test_context_uses_only_verified_native_bindings(self):
        from drive_sync.index import Source, parse_index
        from drive_sync.layout import plan_layout
        from drive_sync.sync_plan import render_source
        from test_index import fixture
        sources=(Source('notes','a.md',Path('/project/a.md'),'markdown','google-doc'),
                 Source('notes','b.md',Path('/project/b.md'),'markdown','google-doc'))
        layout=plan_layout(parse_index(fixture()),sources,{})
        target=layout.files[1].source_id
        with self.assertRaises(Diagnostic):
            render_source(sources[0],b'[B](b.md)',layout,sources,{})
        rendering,provenance=render_source(sources[0],b'[B](b.md)',layout,sources,
            {target:{'storage':'google-doc','remote_id':'target-doc','baseline':{'verified':True}}})
        self.assertTrue(rendering.supported)
        self.assertEqual(provenance[0].target_source_id,target)
