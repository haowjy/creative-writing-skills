import unittest
from drive_sync.native_effects import semantic
from drive_sync.conversion import Style


class NativeVerificationTests(unittest.TestCase):
    def test_streamed_fingerprint_matches_legacy_schema(self):
        from drive_sync.google import fingerprint
        from drive_sync.conversion import utf16
        import random
        def legacy(text, styles):
            spans = {}
            for style in styles:
                spans.setdefault((style.kind, style.value), set()).update(
                    range(style.start, min(style.end, 1 + utf16(text))))
            return fingerprint(dict(text=text, styles=[(k, sorted(v)) for k, v in sorted(spans.items()) if v]))
        rng = random.Random(42)
        for text in ('', '😀 text\n', 'quote " and slash \\', 'x' * 9000):
            for _ in range(20):
                styles = [Style(rng.randrange(-2, 15), rng.randrange(0, len(text) + 20),
                                rng.choice(('strong', 'em', 'link')), rng.choice(('', 'url😀')))
                          for _ in range(10)]
                self.assertEqual(semantic(text, styles), legacy(text, styles))

    def test_large_style_coverage_has_bounded_auxiliary_memory(self):
        import tracemalloc
        text = 'x' * 200_000
        tracemalloc.start()
        try:
            semantic(text, [Style(1, len(text) + 1, 'strong')])
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertLess(peak, 4_000_000)

    def test_run_splitting_does_not_change_style_coverage(self):
        a = [Style(1,5,'strong')]
        b = [Style(1,3,'strong'), Style(3,5,'strong')]
        self.assertEqual(semantic('text',a), semantic('text',b))
        self.assertNotEqual(semantic('text',a), semantic('text',[]))

    def test_text_and_style_changes_are_distinct(self):
        self.assertNotEqual(semantic('one',[]), semantic('two',[]))
        self.assertNotEqual(semantic('word',[Style(1,5,'strong')]), semantic('word',[Style(1,5,'em')]))

    def test_plaintext_create_push_pull_pipeline(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from drive_sync.index import Source, parse_index
        from drive_sync.layout import plan_layout
        from drive_sync.state import StateStore, write_json
        from drive_sync.sync_plan import file_plan
        from drive_sync.native_effects import NativeEffects
        from drive_sync.executor import apply_sync
        from drive_sync.planner import Authorization
        from drive_sync.google import DocumentObservation
        from drive_sync.html_conversion import render_html
        from drive_sync.conversion import utf16
        from test_index import fixture
        class Remote:
            def __init__(self):
                self.meta = None
                self.text = ''
                self.revision = 0
                self.paragraph_style = {}
            def capabilities(self):
                return {'importFormats':{'text/html':['application/vnd.google-apps.document']},'exportFormats':{}}
            def inventory(self, operation_id=None):
                return (self.meta,) if self.meta and (operation_id is None or operation_id == self.meta['appProperties']['operation']) else ()
            def metadata(self, file_id):
                return self.meta
            def create(self, name, mime, source_id, operation_id, parent=None, data=None, import_mime=None):
                self.meta = dict(id='doc', name=name, mimeType=mime, parents=[parent], appProperties=dict(source=source_id, operation=operation_id))
                # Model Docs' mandatory final paragraph boundary separately
                # from source text; render_html is a source converter, not an
                # emulator of Google's import container semantics.
                from html.parser import HTMLParser
                class ParagraphText(HTMLParser):
                    text = ''
                    def handle_data(self, value):
                        self.text += value
                    def handle_endtag(self, tag):
                        if tag == 'p':
                            self.text += '\n'
                parser = ParagraphText()
                parser.feed(data.decode())
                self.text = parser.text[:-1]
                self.revision += 1
            def observe_document(self, file_id):
                text = self.text + '\n'
                end = 1 + utf16(text)
                doc = dict(revisionId=str(self.revision), tabs=[dict(tabProperties={'tabId':'tab'}, documentTab=dict(body={'content':[
                    {'endIndex':1, 'sectionBreak':{}}, {'startIndex':1,'endIndex':end,'paragraph':{'elements':[
                        {'startIndex':1,'endIndex':end,'textRun':{'content':text,'textStyle':{}}}]}}
                ]}))])
                doc['tabs'][0]['documentTab']['body']['content'][1]['paragraph']['paragraphStyle'] = self.paragraph_style
                return DocumentObservation(self.meta,doc,())
            def update_document(self, observation, batch):
                assert batch['writeControl']['requiredRevisionId'] == str(self.revision)
                self.text = ''.join(r['insertText']['text'] for r in batch['requests'] if 'insertText' in r)
                self.revision += 1
        with TemporaryDirectory() as directory:
            path = Path(directory)
            file = path / 'a.txt'
            file.write_text('First.\n')
            index = parse_index(fixture())
            sources = (Source('notes','a.txt',file,'text','google-doc'),)
            layout = plan_layout(index,sources,{})
            store = StateStore(path/'state',index.id)
            write_json(store.path/'bindings.json',{layout.folders[0].id:{'remote_id':'folder'}})
            remote = Remote()
            effects = NativeEffects(layout,sources,store,remote,lambda:'index')
            def sync(expected):
                plan = file_plan('index',layout,sources,store,remote)
                self.assertEqual(plan.operations[0].direction,expected)
                auth = Authorization(plan.digest,index.id,frozenset([layout.files[0].source_id]),frozenset(['create','push','pull']))
                return apply_sync(plan,auth,store,effects)
            self.assertEqual(sync('create').files[0].status,'verified')
            sync('noop')
            file.write_text('Local edit.\n')
            self.assertEqual(sync('push').files[0].status,'verified')
            remote.text='Remote edit.\n'
            remote.revision += 1
            self.assertEqual(sync('pull').files[0].status,'verified')
            self.assertEqual(file.read_text(),'Remote edit.\n')
            sync('noop')
            remote.paragraph_style = {'alignment': 'CENTER'}
            remote.text = 'Centered remote edit.\n'
            remote.revision += 1
            result = sync('pull')
            self.assertEqual(result.files[0].status, 'conflict')
            self.assertEqual(file.read_text(), 'Remote edit.\n')
            self.assertEqual(sync('pull').files[0].status, 'conflict')
            remote.paragraph_style = {}
            remote.text = 'Remote edit.\n'
            remote.revision += 1
            file.write_text('x' * 1_000_001)
            revision = remote.revision
            result = sync('push')
            self.assertEqual(result.files[0].status, 'pending')
            self.assertEqual(len(store.pending()), 1)
            self.assertEqual(remote.revision, revision + 1)

    def test_document_settings_detects_named_style_changes(self):
        from drive_sync.native_effects import document_settings
        self.assertNotEqual(document_settings({'namedStyles':{'styles':[{'textStyle':{'bold':True}}]}}),document_settings({}))
