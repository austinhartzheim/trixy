import asyncore
import threading
import unittest

import trixy


SRV_HOST = '127.1.1.1'  # This is the proxy to connect to
SRV_PORT = 7943
LOC_HOST = '127.1.1.1'  # The proxyc onnects to this
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


class DummyHandler(trixy.TrixyProxy):
    '''
    DummyHandler can act as a handler for TrixyProxyServer, accepting
    and reading data from the connection. Specific data is sent in
    response to incoming data to make unit testing posisble.
    '''
    def handle_read(self):
        data = self.recv(32)
        if data == b'\x00':
            self.send(b'\x00\x00\x00\x00')


class TestCase(unittest.TestCase):
    def setUp(self):
        self.async_poller = AsyncorePoller()
        self.async_poller.start()

    def tearDown(self):
        self.async_poller.stop()
