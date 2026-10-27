import signal
import unittest
from drive_sync.interruptions import cancellation_signals


class CancellationTests(unittest.TestCase):
    def test_signal_sets_token_and_restores_previous_handler(self):
        before=signal.getsignal(signal.SIGINT)
        with cancellation_signals() as token:
            self.assertFalse(token.is_set())
            handler=signal.getsignal(signal.SIGINT)
            handler(signal.SIGINT,None)
            self.assertTrue(token.is_set())
        self.assertEqual(signal.getsignal(signal.SIGINT),before)
