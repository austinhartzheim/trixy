'''
Test the ability of the TrixyInput, TrixyProcessor, and TrixyOutput
classes to chain together.
'''
import asyncore
import socket
import trixy
from tests import utils
from tests.utils import SRV_HOST, SRV_PORT, LOC_HOST, LOC_PORT


class DummyOutput(trixy.TrixyOutput):

    def handle_packet_down(self, data):
        print('Data got to the DummyOuptut')
        self.forward_packet_up(data)


class DummyInput(trixy.TrixyInput):
    def __init__(self, sock, addr):
        print('DummyInput created')
        super().__init__(sock, addr)

        processor = trixy.TrixyProcessor()
        self.connect_node(processor)

        # Create output, but tell it not to autoconnect. LOC_HOST and LOC_PORT
        #   are just used as place-holders because a connection is never made.
        output = DummyOutput(LOC_HOST, LOC_PORT, autoconnect=False)
        processor.connect_node(output)


class Test(utils.TestCase):
    def setUp(self):
        super().setUp()
        server = trixy.TrixyServer(DummyInput, SRV_HOST, SRV_PORT)

    def tearDown(self):
        super().tearDown()

    def test_input_output_via_roundtrip(self):
        '''
        Test that data can flow all the way through the chain to the
        output and then back.
        '''
        sock = socket.socket()
        sock.connect((SRV_HOST, SRV_PORT))

        sock.send(b'hello world')

        print('Sent data; waiting for it back')
        self.assertEqual(sock.recv(32), b'hello world')
