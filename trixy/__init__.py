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
import re
import socket


class TrixyProxyServer(asyncore.dispatcher):
    '''
    Main server for the Trixy proxy. It binds a port and listens there.
    '''

    def __init__(self, handler, host, port):
        asyncore.dispatcher.__init__(self)
        self.handler = handler

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        handler = self.handler(sock)


class TrixyProxyOutbound(asyncore.dispatcher_with_send):
    '''
    Intermediate class to hold an outbound connection and tunnel the data
    between a TrixyProxy instance and a remote host.
    '''
    def __init__(self):
        asyncore.dispatcher_with_send.__init__(self)
        self.ibuffer = []
        self.obuffer = b''

        self.listener = None  # Remote listener object

    def handle_close(self):
        if self.listener:
            self.listener.close()
        self.close()

    def handle_read(self):
        self.listener.send(self.recv(16384))

    def link(self, listener):
        self.listener = listener

    def remote(self, addr, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.create_socket(family, type)
        self.connect(addr)


class TrixyProxy(asyncore.dispatcher_with_send):
    '''
    A base implementation of the asyncore functions needed for the
    other, child proxies.
    '''
    outbound_class = TrixyProxyOutbound

    def __init__(self, sock):
        self.initiate()
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.ibuffer = []
        self.obuffer = b''

        self.remote_addr = None

    def collect_incomming_data(self, data):
        self.ibuffer.append(data)

    def remote(self, addr, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.output = self.outbound_class()
        self.output.link(self)
        self.output.remote(addr)

    def found_terminator(self):
        raise Exception('Must be implemented by child proxy')

    def handle_close(self):
        self.output.handle_close()
        self.close()

    def initiate(self):
        '''
        If the server needs to send data to welcome the client, this is
        where it should be done. This method is called as soon as the
        incoming connection is sent to the TrixyProxy child class.
        '''
        pass

    def set_destination(self, addr):
        self.remote_addr = addr

    def block(self):
        # Run proxy until connection termination
        raise Exception('Must be implemented by child proxy')


class TrixyTunnel(TrixyProxy, asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(16384)
        self.output.send(data)

    def initiate(self):
        raise Exception('Must be overridden by subclass')
        # self.remote(('127.0.0.1', 80))
