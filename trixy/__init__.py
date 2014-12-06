'''
Trixy: Create network listeners, tunnels, and outbound connections in a
modular way allowing interception and modification of the traffic.

Copyright (C) 2014  Austin Hartzheim

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import asyncore
import asynchat
import socket


class TrixyNode():
    def __init__(self):
        self.downstream_nodes = []
        self.upstream_nodes = []

    def add_downstream_node(self, node):
        self.downstream_nodes.append(node)

    def add_upstream_node(self, node):
        self.upstream_nodes.append(node)

    def connect_node(self, node):
        '''
        Create a bidirectional connection between the two nodes with
        the downstream node being the parameter.

        :param TrixyNode node: The downstream node to create a
          bidirectional connection to.
        '''
        self.add_downstream_node(node)
        node.add_upstream_node(self)

    def forward_packet_down(self, data):
        for node in self.downstream_nodes:
            node.handle_packet_down(data)

    def forward_packet_up(self, data):
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
                node.handle_close()

    def handle_packet_down(self, data):
        self.forward_packet_down(data)

    def handle_packet_up(self, data):
        self.forward_packet_up(data)


class TrixyServer(asyncore.dispatcher):
    '''
    Main server to grab incoming connections and forward them.
    '''

    def __init__(self, tinput, host, port):
        '''
        :param TrixyInput tinput: instantiated every time an incoming
          connection is grabbed.
        '''
        super().__init__()
        self.tinput = tinput
        self.setup_socket(host, port)

    def setup_socket(self, host, port):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(100)

    def handle_accepted(self, sock, addr):
        handler = self.tinput(sock, addr)


class TrixyInput(TrixyNode, asyncore.dispatcher_with_send):
    '''
    Once a connection is open, establish an output chain.
    '''
    def __init__(self, sock, addr):
        super().__init__()
        asyncore.dispatcher_with_send.__init__(self, sock)

        self.recvsize = 16384

    def handle_close(self, direction='down'):
        super().handle_close(direction)
        self.close()

    def handle_read(self):
        data = self.recv(self.recvsize)
        for node in self.downstream_nodes:
            node.handle_packet_down(data)

    def handle_packet_up(self, data):
        self.send(data)


class TrixyProcessor(TrixyNode):
    '''
    Perform processing on data moving through Trixy.
    '''
    pass


class TrixyOutput(TrixyNode, asyncore.dispatcher_with_send):
    '''
    Output the data, generally to another nextwork service.
    '''
    def __init__(self, host, port):
        super().__init__()
        asyncore.dispatcher_with_send.__init__(self)

        self.recvsize = 16384

        self.host = host
        self.port = port

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def handle_close(self):
        super().handle_close()
        self.close()

    def handle_read(self):
        data = self.recv(self.recvsize)
        self.forward_packet_up(data)

    def handle_packet_down(self, data):
        self.send(data)
