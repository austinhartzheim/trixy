'''
Test the ability of the TrixyInput, TrixyProcessor, and TrixyOutput
classes to chain together.
'''
import asyncio
import socket
import trixy
from tests import utils
from tests.utils import SRV_HOST, SRV_PORT, LOC_HOST, LOC_PORT


class TestChainingDummyOutput(trixy.TrixyOutput):

    def handle_packet_up(self, data):
        self.forward_packet_down(data)

    def handle_packet_down(self, data):
        raise Exception('This method should not be called')


class TestChainingDummyInput(trixy.TrixyInput):
    def __init__(self, loop):
        super().__init__(loop)
        print('TestChaniningDummyInput init')

        processor = trixy.TrixyProcessor()
        self.connect_node(processor)

        # Create output, but tell it not to autoconnect. LOC_HOST and LOC_PORT
        #   are just used as place-holders because a connection is never made.
        output = TestChainingDummyOutput(LOC_HOST, LOC_PORT, autoconnect=False)
        print(output)
        processor.connect_node(output)


class TestChaining(utils.TestCase):
    def setUp(self):
        print('TestChaining: setUp')
        super().setUp()
        #self.server = trixy.TrixyServer(TestChainingDummyInput,
        #                                SRV_HOST, SRV_PORT, loop=self.loop)
        self.server = trixy.TrixyServer(TestChainingDummyInput,
                                        SRV_HOST, SRV_PORT, loop=self.loop)
        #self.server.run_loop()
        print('TestChaining: setUp complete')

    def tearDown(self):
        super().tearDown()
        self.server.close()
        del self.server

    #@utils.asyncio_test
    def test_input_output_via_roundtrip(self):
        '''
        Test that data can flow all the way through the chain to the
        output and then back.
        '''

        import time
        time.sleep(1)

        sock = socket.socket()
        sock.connect((SRV_HOST, SRV_PORT))

        print('Connected to server')

        @asyncio.coroutine
        def send_data():
            yield from sock.send(b'hello world')
            print('Data sent')

            self.assertEqual(sock.recv(32), b'hello world')
            print('Got response')

        #self.loop.run_util_complete(send_data())
        self.loop.create_task(send_data())

        sock.close()
