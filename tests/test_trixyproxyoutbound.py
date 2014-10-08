'''
Test trixy.TrixyProxyOutbound
'''
import socket
import unittest
import trixy
import utils

from utils import SRV_HOST, SRV_PORT, LOC_HOST, LOC_PORT


class DummyTrixyTunnelWithOutbound(trixy.TrixyTunnel):
    outbound_class = trixy.TrixyProxyOutbound

    def initiate(self):
        self.remote((LOC_HOST, LOC_PORT))


class Test(utils.TestCase):
    handler = DummyTrixyTunnelWithOutbound

    def setUp(self):
        super().setUp()
        self.listener = socket.socket()
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.settimeout(5)
        self.listener.bind((LOC_HOST, LOC_PORT))
        self.listener.listen(10)

        self.server = trixy.TrixyProxyServer(self.handler, SRV_HOST, SRV_PORT)

    def tearDown(self):
        super().tearDown()
        self.server.close()

    def test_outbound_connections(self):
        '''
        Test that TrixyProxyOutbound is properly making connections to
        external services.
        '''
        sock1 = socket.socket()
        sock2 = socket.socket()
        sock1.connect((SRV_HOST, SRV_PORT))
        sock2.connect((SRV_HOST, SRV_PORT))

        listener1 = self.listener.accept()[0]
        sock1.send(b'\x00')
        self.assertEqual(b'\x00', listener1.recv(1))

        listener2 = self.listener.accept()[0]
        sock2.send(b'\x01')
        self.assertEqual(b'\x01', listener2.recv(1))

        sock1.close()
        sock2.close()
        listener1.close()
        listener2.close()

if __name__ == '__main__':
    unittest.main()
