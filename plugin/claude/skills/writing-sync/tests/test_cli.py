"""Presentation tests: the CLI translates requests into service operations."""
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import json
import tempfile
import unittest
from drive_sync.cli import main


class CLITests(unittest.TestCase):
    def call(self, *args):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(args))
        return code, json.loads(out.getvalue() or err.getvalue())

    def test_create_edit_preview_and_stale_save(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            root=path/'source'
            root.mkdir()
            (root/'a.md').write_text('Hello.\n')
            index=str(path/'index.yaml')
            code,created=self.call('--index',index,'index','create')
            self.assertEqual(code,0)
            edits=json.dumps([
                {'operation':'set','path':['roots','notes'],'value':{'path':str(root),'destination_name':'Notes'}},
                {'operation':'append','path':['selection','include'],'value':{'root':'notes','path':'.','glob':'**/*'}}])
            code,preview=self.call('--index',index,'index','edit','--expected-digest',created['digest'],'--edits',edits)
            self.assertEqual(code,0)
            self.assertFalse(preview['saved'])
            _,saved=self.call('--index',index,'index','edit','--expected-digest',created['digest'],'--edits',edits,'--save')
            self.assertTrue(saved['saved'])
            code,stale=self.call('--index',index,'index','edit','--expected-digest',created['digest'],'--edits',edits,'--save')
            self.assertEqual(code,2)
            self.assertEqual(stale['error']['code'],'stale_index')
            code,converted=self.call('--index',index,'conversion','check')
            self.assertEqual(code,0)
            self.assertTrue(converted['reports'][0]['supported'])

    def test_invalid_yaml_is_structured_not_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            index=Path(directory)/'bad.yaml'
            index.write_text('!!python/object:unsafe {}')
            code,result=self.call('--index',str(index),'index','validate')
            self.assertEqual(code,2)
            self.assertEqual(result['error']['code'],'invalid_yaml')

    def test_conversion_command_only_translates_service_report(self):
        from unittest.mock import patch
        from drive_sync.capabilities import ConversionReport
        from drive_sync.conversion import Finding
        report = ConversionReport('/external/source.txt', 'google-doc', 'text', False,
            findings=(Finding('invalid_text', 'Invalid encoding.', 'Use UTF-8.'),))
        with patch('drive_sync.capabilities.check_conversion', return_value=(report,)) as service:
            code, output = self.call('--index', '/external/index.yaml', 'conversion', 'check')
        service.assert_called_once_with(Path('/external/index.yaml'))
        self.assertEqual(code, 2)
        self.assertEqual(output['reports'][0]['source'], report.source)
        self.assertEqual(output['reports'][0]['findings'][0]['code'], 'invalid_text')
