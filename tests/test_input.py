'''
Test the TrixyInput class.
'''
import unittest
import unittest.mock
import trixy


class TestTrixyInput(unittest.TestCase):

    def test_handle_close(self):
        '''
        Test that handle_close() results in calling close() on the
        input's transport.
        '''
        node = trixy.TrixyInput(None)
        node.transport = unittest.mock.MagicMock()
        node.transport.close = unittest.mock.MagicMock()

        node.handle_close()
        node.transport.close.assert_called_with()

    def test_connection_last_closes(self):
        '''
        Test that the connection_lost() method calls close() on the
        transport.
        '''
        node = trixy.TrixyInput(None)
        node.transport = unittest.mock.MagicMock()
        node.transport.close = unittest.mock.MagicMock()

        node.connection_lost(None)
        node.transport.close.assert_called_with()
