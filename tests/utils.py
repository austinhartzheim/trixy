import asyncio
import threading
import unittest

import trixy


SRV_HOST = '127.1.1.1'  # This is the proxy to connect to
SRV_PORT = 7943
LOC_HOST = '127.1.1.1'  # The proxy connects to this
LOC_PORT = SRV_PORT + 1


def asyncio_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class TestCase(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
