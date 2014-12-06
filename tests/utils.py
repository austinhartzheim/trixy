import asyncore
import threading
import unittest

import trixy


SRV_HOST = '127.1.1.1'  # This is the proxy to connect to
SRV_PORT = 7943
LOC_HOST = '127.1.1.1'  # The proxy connects to this
LOC_PORT = SRV_PORT + 1


class AsyncorePoller(threading.Thread):
    '''
    Ensure that asyncore continues processing connections until the
    until the test that is using it has completed.
    '''
    def __init__(self):
        super().__init__()
        self.continue_running = True

    def run(self):
        while self.continue_running:
            #  asyncore.poll()
            asyncore.loop(1, count=1)
        asyncore.close_all()

    def stop(self):
        self.continue_running = False


class TestCase(unittest.TestCase):
    def setUp(self):
        self.async_poller = AsyncorePoller()
        self.async_poller.start()

    def tearDown(self):
        self.async_poller.stop()

        # This is an ugly hack because we use threads. It allows time for
        #   sockets to close before we run the next test.
        #   Hopefully this is reliable enough to prevent random failures.
        # TODO: Fix the above threading issue.
        import time
        time.sleep(1)
