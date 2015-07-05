'''
Perform simple tests on the TrixyNode class, especially the
functionality relating to upstream and downstream nodes.
'''
import unittest
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
