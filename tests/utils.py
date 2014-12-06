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

    def stop(self):
        self.continue_running = False


class TestCase(unittest.TestCase):
    def setUp(self):
        self.async_poller = AsyncorePoller()
        self.async_poller.start()

    def tearDown(self):
        self.async_poller.stop()
