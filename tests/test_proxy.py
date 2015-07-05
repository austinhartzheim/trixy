'''
Test the functionality of the proxy implementations.
'''
import asyncore
import socket
import struct
import trixy.proxy
from tests import utils
from tests.utils import SRV_HOST, SRV_PORT, LOC_HOST, LOC_PORT


class TestSocks4Input(utils.TestCase):
    def setUp(self):
        super().setUp()
        print('TestSocks4Input: setUp')
        self.server = trixy.TrixyServer(trixy.proxy.Socks4Input,
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
    def test_through(self):
        '''
        Test a single connection going all the way through the proxy.
        '''
        # Create connection request with userid "trixy"
        request_host = socket.inet_aton(LOC_HOST)
        request_port = struct.pack('!H', LOC_PORT)
        request_packet = (b'\x04\x01' + request_port +
                           request_host + b'trixy\x00')
        osock = socket.socket()
        osock.connect((SRV_HOST, SRV_PORT))
        osock.send(request_packet)

        # Accept the incomming connection
        isock = self.rsock.accept()[0]

        # Get response and validate
        meth_resp = osock.recv(10)
        self.assertEqual(len(meth_resp), 8, 'Method select response too long')
        print(meth_resp)
        self.assertGreater(meth_resp[1], 89, 'Reply code out of bounds.')
        self.assertLess(meth_resp[1], 93, 'Reply code out of bounds.')
        self.assertEqual(meth_resp[2:4], request_port, 'Allowed port mismatch')
        self.assertEqual(meth_resp[4:], request_host, 'Allowed host mismatch')

        # Now we can send some data
        osock.send(b'hwft')
        self.assertEqual(b'hwft', isock.recv(6))
        isock.send(b'tfwh')
        self.assertEqual(b'tfwh', osock.recv(6))

        # Test closing propagation through proxy
        isock.close()

        # This is an ugly hack because we use threads. It allows time for the
        #   close to propagate through before we test if it did.
        #   Hopefully this is reliable enough to prevent random failures.
        # TODO: Fix the above threading issue.
        import time
        time.sleep(0.1)

        osock.send(b'socked should be closed.')
        self.assertRaises(socket.error, osock.send,
                          b'so this should cause an error')

