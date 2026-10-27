"""Keep presentation dependencies out of reusable runtime services."""
import ast
from pathlib import Path
import unittest
import drive_sync


class ServiceBoundaryTests(unittest.TestCase):
    def test_services_do_not_depend_on_cli_or_interactive_presentation(self):
        package = Path(drive_sync.__file__).parent
        inspected = 0
        violations = []
        for path in sorted(package.glob('*.py')):
            if path.name == 'cli.py':
                continue
            inspected += 1
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if isinstance(node, ast.Import):
                    if any(name.name.split('.')[0] in {'argparse', 'webbrowser'}
                           or name.name == 'drive_sync.cli' for name in node.names):
                        violations.append((path.name, node.lineno, 'presentation import'))
                if isinstance(node, ast.ImportFrom):
                    if ((node.module or '').split('.')[0] in {'argparse', 'webbrowser', 'cli'}
                            or node.module == 'drive_sync.cli'):
                        violations.append((path.name, node.lineno, 'presentation import'))
                    if node.module in (None, 'drive_sync') and any(name.name == 'cli' for name in node.names):
                        violations.append((path.name, node.lineno, 'CLI import'))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in {'print', 'input', 'exit', 'quit'}:
                        violations.append((path.name, node.lineno, node.func.id))
        self.assertGreater(inspected, 0)
        self.assertEqual(violations, [])
