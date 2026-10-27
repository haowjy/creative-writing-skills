"""Opt-in official EPUBCheck gate. Synthetic files only; no downloads or Google.

Use the installed skill environment or set PYTHONPATH to the skill scripts dir.
Java and the complete EPUBCheck distribution are external test tools, not runtime
requirements. The output directory must not already exist.
"""
import argparse
from copy import copy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile

from drive_sync.epub_return import patch_epub
from test_epub import book


def fixtures():
    source = book()
    samples = {'source': source}
    for name, text in (('short-return', 'X'), ('unicode-return', 'A longer sentence with 😀 & text')):
        samples[name] = patch_epub(source, 'First\nSecond\n', text + '\nSecond\n',
                                  modified='2026-09-15T00:00:00Z')
    invalid = BytesIO()
    with ZipFile(BytesIO(source)) as archive, ZipFile(invalid, 'w') as target:
        for entry in archive.infolist():
            data = archive.read(entry.filename)
            if entry.filename == 'OEBPS/book.opf':
                data = data.replace(b' properties="nav"', b'')
            target.writestr(copy(entry), data)
    samples['invalid-missing-nav-property'] = invalid.getvalue()
    return samples


def report_matches(report, *, invalid):
    checker = report.get('checker', {})
    counts = [checker.get(k) for k in ('nFatal', 'nError', 'nWarning')]
    if any(type(n) is not int or n < 0 for n in counts):
        return False
    if not invalid:
        return counts == [0, 0, 0] and report.get('messages') == []
    return (counts == [0, 1, 0] and any(
        m.get('ID') == 'RSC-005' and m.get('severity') == 'ERROR'
        and 'nav' in m.get('message', '') for m in report.get('messages', [])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', required=True, type=Path)
    parser.add_argument('--jar', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    java, jar, output = args.java.resolve(), args.jar.resolve(), args.output.resolve()
    if not java.is_file() or not jar.is_file():
        parser.error('Supply existing Java executable and official EPUBCheck JAR paths.')
    output.mkdir()  # Never overwrite previous evidence.
    command = [str(java), '-jar', str(jar)]
    version = subprocess.run(command + ['--version'], capture_output=True, text=True,
                             timeout=60, check=True)
    results = []
    for name, data in fixtures().items():
        source = output / (name + '.epub')
        source.write_bytes(data)
        result = subprocess.run(command + ['--failonwarnings', '--json',
            str(output / (name + '.json')), str(source)], capture_output=True,
            text=True, timeout=120, check=False)
        (output / (name + '.log')).write_text(result.stdout + result.stderr)
        expected = 1 if name.startswith('invalid-') else 0
        report_path = output / (name + '.json')
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        results.append({'fixture': name, 'report_matches': report_matches(report, invalid=bool(expected)), 'sha256': sha256(data).hexdigest(),
                        'exit_code': result.returncode, 'expected_exit_code': expected})
    evidence = {'checker_version': version.stdout.strip() or version.stderr.strip(),
                'jar_sha256': sha256(jar.read_bytes()).hexdigest(), 'results': results}
    (output / 'summary.json').write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))
    return int(any(r['exit_code'] != r['expected_exit_code'] or not r['report_matches'] for r in results))


if __name__ == '__main__':
    raise SystemExit(main())
