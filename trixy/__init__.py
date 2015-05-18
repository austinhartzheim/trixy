# Trixy: Create network listeners, tunnels, and outbound connections in a
# modular way allowing interception and modification of the traffic.
#
# Copyright (C) 2014-2015  Austin Hartzheim
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import socket


class TrixyNode():
    '''
    A base class for TrixyNodes that implements some default packet
    forwarding and node linking.
    '''

    def __init__(self):
        self.downstream_nodes = []
        self.upstream_nodes = []

    def add_downstream_node(self, node):
        '''
        Add a one direction downstream link to the node parameter.

        :param TrixyNode node: The downstream node to create a
          unidirectional link to.
        '''
        self.downstream_nodes.append(node)

    def add_upstream_node(self, node):
        '''
        Add a one direction upstream link to the node parameter.

        :param TrixyNode node: The upstream node to create a
          unidirectional link to.
        '''
        self.upstream_nodes.append(node)

    def connect_node(self, node):
        '''
        Create a bidirectional connection between the two nodes with
        the downstream node being the parameter.

        :param TrixyNode node: The downstream node to create a
          bidirectional connection to.
        '''
        self.add_upstream_node(node)
        node.add_downstream_node(self)

    def forward_packet_down(self, data):
        '''
        Forward data to all downstream nodes.

        :param bytes data: The data to forward.
        '''
        for node in self.downstream_nodes:
            node.handle_packet_down(data)

    def forward_packet_up(self, data):
        '''
        Forward data to all upstream nodes.

        :param bytes data: The data to forward.
        '''
        for node in self.upstream_nodes:
            node.handle_packet_up(data)

    def handle_close(self, direction='down'):
        '''
        The connection has closed on one end. So, shutdown what we are
        doing and notify the nodes we are connected to.

        :param str direction: 'down' or 'up' depending on if downstream
          nodes need to be closed, or upstream nodes need to be closed.
        '''
        if direction == 'down':
            for node in self.downstream_nodes:
                node.handle_close()
        elif direction == 'up':
            for node in self.upstream_nodes:
                node.handle_close(direction='up')

    def handle_packet_down(self, data):
        '''
        Hadle data moving downwards. TrixyProcessor children should
        perform some action on `data` whereas `TrixyOutput` children
        should send the data to the desired output location.

        Generally, the a child implementation of this method should
        be implemented such that it calls self.forward_packet_down
        with the data (post-modification if necessary) to forward the
        data to other processors in the chain. However, if the
        processor is a filter, it may drop the packet by omitting that
        call.

        :param bytes data: The data that is being handled.
        '''
        self.forward_packet_down(data)

    def handle_packet_up(self, data):
        '''
        Hadle data moving upwards. TrixyProcessor children should
        perform some action on `data` whereas `TrixyOutput` children
        should send the data to the desired output location.

        Generally, the a child implementation of this method should
        be implemented such that it calls self.forward_packet_down
        with the data (post-modification if necessary) to forward the
        data to other processors in the chain. However, if the
        processor is a filter, it may drop the packet by omitting that
        call.

        :param bytes data: The data that is being handled.
        '''
        self.forward_packet_up(data)


class TrixyServer():
    '''
    Main server to grab incoming connections and forward them.
    '''
    # TODO: evaluate if there is a place for a server class or if
    #  asyncio should be used (loop.create_server) instead.

    def __init__(self, tinput, host, port, loop=None):
        '''
        :param TrixyInput tinput: instantiated every time an incoming
          connection is grabbed.
        :param str host: the hostname to bind to.
        :param int port: the port number to bind to.
        :param loop: you may optionally specify your own event loop.
        '''
        super().__init__()
        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

        self.tinput = tinput
        self.host = host
        self.port = port

        self.managing_loop = False

        coro = self.loop.create_server(lambda: self.tinput(self.loop),
                                       self.host, self.port)
        #asyncio.async(coro)
        self.server = self.loop.run_until_complete(coro)

    def close(self):
        '''
        Shutdown the server.
        '''
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())

    def run_loop(self):
        '''
        Run the event loop so that the server functions.
        '''
        self.managing_loop = True
        self.loop.run_forever()

    def connectikon_lost(self):
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
        self.loop.close()


class TrixyInput(TrixyNode, asyncio.Protocol):
    '''
    Once a connection is open, establish an output chain.
    '''
    #def __init__(self, transport):
    def __init__(self, loop):
        super().__init__()
        #self.transport = transport
        self.loop = loop

        self.recvsize = 16384

    def handle_close(self, direction='down'):
        super().handle_close(direction)
        self.transport.close()

    def handle_packet_down(self, data):
        self.transport.write(data)

    def data_received(self, data):
        self.handle_packet_up(data)

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, ex):
        self.handle_close('down')


class TrixyProcessor(TrixyNode):
    '''
    Perform processing on data moving through Trixy.
    '''
    pass


class TrixyOutput(TrixyNode, asyncio.Protocol):
    '''
    Output the data, generally to another network service.
    '''

    def __init__(self, loop):
        '''
        :param loop: The asyncio event loop.
        '''
        super().__init__()

        self.loop = loop
        self.transport = None

    def handle_close(self, direction='down'):
        super().handle_close(direction)
        self.transport.close()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.handle_packet_down(data)

    def handle_packet_up(self, data):
        self.transport.write(data)
