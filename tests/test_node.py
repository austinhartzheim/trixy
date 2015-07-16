'''
Perform simple tests on the TrixyNode class, especially the
functionality relating to upstream and downstream nodes.
'''
import unittest
import unittest.mock
import trixy


class TestTrixyNode(unittest.TestCase):

    def test_add_downstream_node(self):
        '''
        Test that nodes are correctly added to the list of downstream
        nodes and check that duplicates are prevented.
        '''
        node = trixy.TrixyNode()
        n = trixy.TrixyNode()
        node.add_downstream_node(n)
        node.add_downstream_node(n)

        self.assertIn(n, node.downstream_nodes)
        self.assertEqual(len(node.downstream_nodes), 1,
                         'The downstream nodes list contains duplicates')

    def test_add_upstream_node(self):
        '''
        Test that nodes are correctly added to the list of upstream
        nodes and check that duplicates are prevented.
        '''
        node = trixy.TrixyNode()
        n = trixy.TrixyNode()
        node.add_upstream_node(n)
        node.add_upstream_node(n)

        self.assertIn(n, node.upstream_nodes)
        self.assertEqual(len(node.upstream_nodes), 1,
                         'The upstream nodes list contains duplicates')

    def test_connect_node(self):
        '''
        Test that the connect_mode method creates a bi-directional link
        between two nodes.
        '''
        n1 = trixy.TrixyNode()
        n2 = trixy.TrixyNode()
        n1.connect_node(n2)

        self.assertIn(n2, n1.upstream_nodes)
        self.assertIn(n1, n2.downstream_nodes)

    def test_forward_packet_down(self):
        '''
        Test that the forward_packet_down() method calls the
        handle_downstream_packet method on all downstream nodes.
        '''
        data = b'test data packet'

        node = trixy.TrixyNode()
        downstream = [trixy.TrixyNode(), trixy.TrixyNode()]
        for each in downstream:
            each.handle_packet_down = unittest.mock.MagicMock()
            node.add_downstream_node(each)

        node.forward_packet_down(data)

        for each in downstream:
            each.handle_packet_down.assert_called_with(data)

    def test_forward_packet_up(self):
        '''
        Test that the forward_packet_up() method calls the
        handle_upstream_packet method on all downstream nodes.
        '''
        data = b'test data packet'

        node = trixy.TrixyNode()
        upstream = [trixy.TrixyNode(), trixy.TrixyNode()]
        for each in upstream:
            each.handle_packet_up = unittest.mock.MagicMock()
            node.add_upstream_node(each)

        node.forward_packet_up(data)

        for each in upstream:
            each.handle_packet_up.assert_called_with(data)

    def test_handle_close_down(self):
        '''
        Test that the handle_close() method propagates changes in the
        downward direction.
        '''
        node = trixy.TrixyNode()
        child = unittest.mock.MagicMock()
        node.add_downstream_node(child)

        node.handle_close('down')
        args, kwargs = child.handle_close.call_args
        self.assertTrue(args == ('down',) or
                        ('direction' in kwargs and kwargs['direction'] == 'down'))

    def test_handle_close_up(self):
        '''
        Test that the handle_close() method propagates changes in the
        upnward direction.
        '''
        node = trixy.TrixyNode()
        child = unittest.mock.MagicMock()
        node.connect_node(child)

        node.handle_close('up')
        args, kwargs = child.handle_close.call_args
        self.assertTrue(args == ('up',) or
                        ('direction' in kwargs and kwargs['direction'] == 'up'))
