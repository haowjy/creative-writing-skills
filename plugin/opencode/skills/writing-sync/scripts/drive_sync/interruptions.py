"""CLI-only signal translation; application services receive a cancellation token."""
from contextlib import contextmanager
import signal
import threading


@contextmanager
def cancellation_signals():
    token=threading.Event()
    previous={}
    def cancel(signum,frame):
        token.set()
    try:
        for signum in (signal.SIGINT,signal.SIGTERM):
            previous[signum]=signal.getsignal(signum)
            signal.signal(signum,cancel)
        yield token
    finally:
        for signum,handler in previous.items():
            signal.signal(signum,handler)


def cancellable(function):
    """Run an apply callback; first signal requests stop after reconciliation."""
    with cancellation_signals() as token:
        return function(token)
