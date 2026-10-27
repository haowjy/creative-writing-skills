"""Offline validation of the external conformance gate's result checks."""
import unittest
from epub_conformance import report_matches


class ConformanceReportTests(unittest.TestCase):
    def test_positive_requires_explicit_clean_report(self):
        self.assertFalse(report_matches({}, invalid=False))
        report = {'checker': {'nFatal': 0, 'nError': 0, 'nWarning': 0}, 'messages': []}
        self.assertTrue(report_matches(report, invalid=False))
        report['checker']['nWarning'] = 1
        self.assertFalse(report_matches(report, invalid=False))

    def test_negative_requires_expected_nav_failure(self):
        report = {'checker': {'nFatal': 0, 'nError': 1, 'nWarning': 0}, 'messages': []}
        self.assertFalse(report_matches(report, invalid=True))
        report['messages'] = [{'ID': 'RSC-005', 'severity': 'ERROR', 'message': 'Missing nav property'}]
        self.assertTrue(report_matches(report, invalid=True))
        report['checker']['nFatal'] = 1
        self.assertFalse(report_matches(report, invalid=True))
