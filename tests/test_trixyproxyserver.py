'''
Test trixy.TrixyProxyServer
'''
import socket
import unittest
import trixy
import utils

from utils import SRV_HOST, SRV_PORT


class Test(utils.TestCase):
    handler = utils.DummyHandler

    def setUp(self):
        super().setUp()
        self.server = trixy.TrixyProxyServer(self.handler, SRV_HOST, SRV_PORT)

    def tearDown(self):
        super().tearDown()
        self.server.close()

    def test_handle_accepted(self):
        '''
        Test that TrixyProxyServer.handle_accepted processes the
        connection properly and creates a DummyHandler innstance to
        manage the connection.
        '''
        sock = socket.socket()
        sock.connect((SRV_HOST, SRV_PORT))
        sock.send(b'\x00')

        self.assertEqual(b'\x00\x00\x00\x00', sock.recv(32),
                         'Incorrect response from DummyHandler')

        sock.close()


if __name__ == '__main__':
    unittest.main()
