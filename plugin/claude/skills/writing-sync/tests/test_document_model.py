import unittest
from copy import deepcopy
from drive_sync.document_model import read_document
from drive_sync.google import DocumentObservation
from drive_sync.index import Diagnostic


def observation():
    doc = dict(revisionId='r', tabs=[dict(tabProperties={'tabId':'tab'}, documentTab=dict(body={'content': [
        {'endIndex':1, 'sectionBreak':{}},
        {'startIndex':1, 'endIndex':8, 'paragraph': {'elements':[
            {'startIndex':1, 'endIndex':8, 'textRun': {'content':'Hello\n\n', 'textStyle':{}}}
        ]}}
    ]}))])
    return DocumentObservation(dict(id='doc',name='a.md',parents=['folder']), doc, ())


class DocumentTests(unittest.TestCase):
    def test_exact_import_defaults_normalize_but_remain_in_snapshot(self):
        from drive_sync.document_model import IMPORT_BORDER, IMPORT_BORDERS
        plain = observation()
        value = observation()
        paragraph = value.document['tabs'][0]['documentTab']['body']['content'][1]['paragraph']
        paragraph['paragraphStyle'] = {k: deepcopy(IMPORT_BORDER) for k in IMPORT_BORDERS}
        paragraph['paragraphStyle']['shading'] = {'backgroundColor': {}}
        self.assertEqual(read_document(value).styles, ())
        self.assertNotEqual(read_document(value).snapshot.content_hash, read_document(plain).snapshot.content_hash)
        for field, extra in (('width', {'magnitude': 1}), ('padding', {'magnitude': 1}),
                             ('color', {'color': {'rgbColor': {'red': 1}}})):
            changed = deepcopy(value)
            border = changed.document['tabs'][0]['documentTab']['body']['content'][1]['paragraph']['paragraphStyle']['borderBottom']
            border[field].update(extra)
            self.assertTrue(any(s.kind == 'unrepresentable' for s in read_document(changed).styles))
        paragraph['paragraphStyle']['shading'] = {'backgroundColor': {'color': {'rgbColor': {'red': 1}}}}
        self.assertTrue(any(s.kind == 'unrepresentable' for s in read_document(value).styles))

    def test_many_runs_do_not_reencode_accumulated_text(self):
        from unittest.mock import patch
        from drive_sync.conversion import utf16
        value = observation()
        block = value.document['tabs'][0]['documentTab']['body']['content'][1]
        count = 5000
        block['paragraph']['elements'] = [
            {'startIndex': 1 + 2 * i, 'endIndex': 3 + 2 * i,
             'textRun': {'content': '😀', 'textStyle': {}}} for i in range(count)]
        block['paragraph']['elements'].append({'startIndex': 1 + 2 * count,
            'endIndex': 2 + 2 * count, 'textRun': {'content': '\n', 'textStyle': {}}})
        block['endIndex'] = 2 + 2 * count
        encoded_characters = 0
        def measured(text):
            nonlocal encoded_characters
            encoded_characters += len(text)
            return utf16(text)
        with patch('drive_sync.document_model.utf16', side_effect=measured):
            model = read_document(value)
        self.assertEqual(model.text, '😀' * count)
        self.assertEqual(encoded_characters, count + 1)

    def test_observed_link_decoration_but_not_custom_color(self):
        from drive_sync.document_model import LINK_COLOR
        value = observation()
        run = value.document['tabs'][0]['documentTab']['body']['content'][1]['paragraph']['elements'][0]['textRun']
        run['textStyle'] = {'link': {'url': 'https://example.com'}, 'underline': True,
                            'foregroundColor': deepcopy(LINK_COLOR)}
        self.assertEqual([s.kind for s in read_document(value).styles], ['link'])
        run['textStyle']['foregroundColor']['color']['rgbColor']['red'] = 1
        self.assertTrue(any(s.kind == 'unrepresentable' for s in read_document(value).styles))

    def test_observed_list_indents_but_not_custom_indents(self):
        from drive_sync.document_model import LIST_INDENTS
        value = observation()
        tab = value.document['tabs'][0]['documentTab']
        paragraph = tab['body']['content'][1]['paragraph']
        paragraph['bullet'] = {'listId': 'list'}
        paragraph['paragraphStyle'] = deepcopy(LIST_INDENTS)
        level = dict(deepcopy(LIST_INDENTS), glyphSymbol='\u25cf', glyphFormat='%0',
                     textStyle={'underline': False}, bulletAlignment='START')
        tab['lists'] = {'list': {'listProperties': {'nestingLevels': [level]}}}
        self.assertEqual([s.kind for s in read_document(value).styles], ['bullet'])
        paragraph['paragraphStyle']['indentStart']['magnitude'] = 72
        self.assertTrue(any(s.kind == 'unrepresentable' for s in read_document(value).styles))

    def test_explicit_default_direction_is_supported(self):
        value = observation()
        value.document['tabs'][0]['documentTab']['body']['content'][1]['paragraph']['paragraphStyle'] = {
            'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}
        self.assertEqual(read_document(value).styles, ())

    def test_paragraph_layout_cannot_silently_become_plain_text(self):
        for field, content in (('alignment', 'CENTER'), ('direction', 'RIGHT_TO_LEFT'),
                               ('spaceAbove', {'magnitude': 20, 'unit': 'PT'}),
                               ('lineSpacing', 200)):
            with self.subTest(field=field):
                value = observation()
                paragraph = value.document['tabs'][0]['documentTab']['body']['content'][1]['paragraph']
                paragraph['paragraphStyle'] = {field: content}
                result = read_document(value)
                self.assertTrue(any(s.kind == 'unrepresentable'
                                    and s.value.startswith('paragraph:' + field + ':')
                                    for s in result.styles))

    def test_nondefault_list_numbering_is_not_decimal_from_one(self):
        for level in ({'glyphType': 'UPPER_ROMAN'},
                      {'glyphType': 'DECIMAL', 'startNumber': 5},
                      {'glyphType': 'DECIMAL', 'glyphFormat': '(%0)'}):
            with self.subTest(level=level):
                value = observation()
                tab = value.document['tabs'][0]['documentTab']
                tab['body']['content'][1]['paragraph']['bullet'] = {'listId': 'list'}
                tab['lists'] = {'list': {'listProperties': {'nestingLevels': [level]}}}
                self.assertTrue(any(s.kind == 'unrepresentable' for s in read_document(value).styles))

    def test_removes_only_container_newline(self):
        result = read_document(observation())
        self.assertEqual(result.text, 'Hello\n')
        self.assertEqual(result.end_index, 8)

    def test_revision_not_content_change(self):
        before = observation()
        after = deepcopy(before)
        after.document['revisionId'] = 'r2'
        self.assertEqual(read_document(before).snapshot.content_hash, read_document(after).snapshot.content_hash)
        after.document['tabs'][0]['documentTab']['body']['content'][1]['paragraph']['elements'][0]['textRun']['textStyle']['underline'] = True
        self.assertNotEqual(read_document(before).snapshot.content_hash, read_document(after).snapshot.content_hash)

    def test_extra_tab_and_object_blocked(self):
        for mutate in (lambda d: d['tabs'].append(deepcopy(d['tabs'][0])),
                       lambda d: d['tabs'][0]['documentTab'].update(inlineObjects={'image':{}})):
            value = observation()
            mutate(value.document)
            with self.assertRaises(Diagnostic):
                read_document(value)

    def test_unsupported_decoration_is_not_treated_as_plain_text(self):
        value=observation()
        value.document['tabs'][0]['documentTab']['body']['content'][1]['paragraph']['elements'][0]['textRun']['textStyle']['underline']=True
        self.assertTrue(any(s.kind=='unrepresentable' for s in read_document(value).styles))

    def test_font_size_and_color_are_not_silently_plain(self):
        value=observation()
        style=value.document['tabs'][0]['documentTab']['body']['content'][1]['paragraph']['elements'][0]['textRun']['textStyle']
        style.update(fontSize={'magnitude':24,'unit':'PT'},foregroundColor={'color':{'rgbColor':{'red':1}}})
        self.assertTrue(any(s.kind=='unrepresentable' and s.value.startswith('fontSize:') for s in read_document(value).styles))
