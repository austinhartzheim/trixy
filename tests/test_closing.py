'''
Test to be sure that a close on either end (Input or Output) will
case the other end of the connection to be closed. In other words,
test close event propagation in the up and down directions.
'''
import asyncio
import socket
import trixy
from tests import utils
from tests.utils import SRV_HOST, SRV_PORT, LOC_HOST, LOC_PORT


class TestChainingDummyInput(trixy.TrixyInput):
    def __init__(self, sock, addr):
        super().__init__(sock, addr)

        output = trixy.TrixyOutput(LOC_HOST, LOC_PORT)
        self.connect_node(output)


class TestClosing(utils.TestCase):
    def setUp(self):
        super().setUp()
        print('TestClosing: setUp')
        #self.server = trixy.TrixyServer(TestChainingDummyInput,
        #                                SRV_HOST, SRV_PORT, loop=self.loop)
        self.server = trixy.create_server(TestChainingDummyInput,
                                          SRV_HOST, SRV_PORT, loop=self.loop)

        self.rsock = socket.socket()
        self.rsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rsock.bind((LOC_HOST, LOC_PORT))
        self.rsock.listen(2)

    def tearDown(self):
        super().tearDown()
        self.server.close()
        self.rsock.close()

    @utils.asyncio_test
    def test_output_close_propagation(self):
        sock = socket.socket()
        sock.connect((SRV_HOST, SRV_PORT))

        rs = self.rsock.accept()[0]
        rs.close()

        # This is an ugly hack because we use threads. It allows time for the
        #   close to propagate through before we test if it did.
        #   Hopefully this is reliable enough to prevent random failures.
        # TODO: Fix the above threading issue.
        import time
        time.sleep(0.1)

        sock.send(b'socket should be closed.')
        self.assertRaises(socket.error, sock.send,
                          b'so this should cause an error')
        sock.close()

    @utils.asyncio_test
    def test_input_close_propagation(self):
        reader, writer = yield from asyncio.open_connection(SRV_HOST, SRV_PORT)

        sock = socket.socket()
        sock.connect((SRV_HOST, SRV_PORT))

        rs = self.rsock.accept()[0]
        sock.close()

        # This is an ugly hack because we use threads. It allows time for the
        #   close to propagate through before we test if it did.
        #   Hopefully this is reliable enough to prevent random failures.
        # TODO: Fix the above threading issue.
        import time
        time.sleep(0.1)

        rs.send(b'socket should be closed.')
        self.assertRaises(socket.error, rs.send,
                          b'so this should cause an error')
        rs.close()
