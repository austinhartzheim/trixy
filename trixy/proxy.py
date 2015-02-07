'''
The Trixy proxy inputs speak a variety of common proxy protocols, such
as SOCKS4, SOCKS4a, and SOCKS5. Their default behavior is to act as a
normal proxy and open a connection to the desired endpoint. However,
this behavior can be overridden to create different results.

Additionally, the proxy outputs allow a connection to be subsequently
made to a proxy server. This allows intercepted traffic to be easily
routed on networks that require a proxy. It also makes it easier to
route traffic into the Tor network.
'''
import struct
import socket
import trixy


class Socks4Input(trixy.TrixyInput):
    '''
    Implements the SOCKS4 protocol as defined in this document:
    http://www.openssh.com/txt/socks4.protocol
    '''
    # TODO: decide if binding will be allowed. Probably off by default
    #   but can be enabled by an option in __init__?
    def __init__(self, sock, addr):
        super().__init__(sock, addr)
        self.first_packet = True

    def handle_packet_down(self, data):
        if self.first_packet:
            self.handle_proxy_request(data)
            self.first_packet = False
            return
        self.forward_packet_down(data)

    def handle_proxy_request(self, data):
        '''
        In SOCKS4, the first packet in a connection is a request to
        either initiate a connection to a remote host and port, or it
        is a request to bind a port. This method is responsible for
        processing those requests.
        '''
        if data.startswith(b'\x04\x01'):  # CONNECT request
            port = struct.unpack('!H', data[2:4])[0]
            addr = socket.inet_ntoa(data[4:8])
            userid = data[8:-1]

            self.handle_connect_request(addr, port, userid)

        elif data.startswith(b'\x04\x02'):  # BIND request
            pass  # TODO: implement binding behavior; see note above.

    def handle_connect_request(self, addr, port, userid):
        '''
        The application connecting to this SOCKS4 input has requested
        that a connection be made to a remote host. At this point, that
        request can be accepted, modified, or declined.

        The default behavior is to accept the request as-is.
        '''
        self.connect_node(trixy.TrixyOutput(addr, port))

        # TODO: need functionality to detect if the connection fails to
        #   notify the application accordingly.
        self.reply_request_granted(addr, port)

    def reply_request_granted(self, addr, port):
        '''
        Send a reply stating that the connection or bind request has
        been granted and that the connection or bind attempt was
        successfully completed.
        '''
        # 90 is the response for a granted request
        self.send(struct.pack('!BBH4s', 0x00, 90, port,
                              socket.inet_aton(addr)))

    def reply_request_failed(self, addr, port):
        '''
        Send a reply stating that the request was rejected (perhaps due
        to a firewall rule forbidding the connection or binding) or
        that it failed (i.e., the remote host could not be connected to
        or the requested port could not be bound).
        '''
        # 91 is the response for a rejected or failed request
        self.send(struct.pack('!BBH4s', 0x00, 91, port,
                              socket.inet_aton(addr)))

    def reply_request_rejected(self, addr, port):
        '''
        Send a reply saying that the request was rejected because the
        SOCKS server could not connect to the client's identd server.
        '''
        # 92 is the response for a request being rejected because the SOCKS
        #   server cannot connect to identd on the client.
        self.send(struct.pack('!BBH4s', 0x00, 92, port,
                              socket.inet_aton(addr)))

    def reply_request_rejected_id_mismatch(self, addr, port):
        '''
        Send a reply saying that the request was rejected because the
        SOCKS server was sent an ID by the client that did not match
        the ID returned by identd on the client's computer.
        '''
        # 93 is the response for rejections due to the client program and
        #   identd reporting different user-ids.
        self.send(struct.pack('!BBH4s', 0x00, 93, port,
                              socket.inet_aton(addr)))


class Socks4aInput(Socks4Input):
    '''
    Implements the SOCKS4a protocol, which is the same as the SOCKS4
    protocol except for the addition of DNS resolution as described
    here: http://www.openssh.com/txt/socks4a.protocol
    '''
    # TODO: decide if binding will be allowed. Probably off by default
    #   but can be enabled by an option in __init__?
    def __init__(self, sock, addr):
        super().__init__(sock, addr)
        print('Got connect')
        self.first_packet = True

    def handle_proxy_request(self, data):
        '''
        In SOCKS4, the first packet in a connection is a request to
        either initiate a connection to a remote host and port, or it
        is a request to bind a port. This method is responsible for
        processing those requests.
        '''
        print('handle_proxy_request: ', data)
        if data.startswith(b'\x04\x01'):  # CONNECT request
            port = struct.unpack('!H', data[2:4])[0]
            addr = socket.inet_ntoa(data[4:8])
            userid = data[8:-1]

            # TODO: test if the address is invalid, which suggests that
            #   we need to resolve the hostname contained later in the data.

            print('  ', addr, ':', port, ' username: ', userid)

            self.handle_connect_request(addr, port, userid)

        elif data.startswith(b'\x04\x02'):  # BIND request
            pass  # TODO: implement binding behavior; see note above.

    def handle_connect_request(self, addr, port, userid):
        '''
        The application connecting to this SOCKS4 input has requested
        that a connection be made to a remote host. At this point, that
        request can be accepted, modified, or declined.

        The default behavior is to accept the request as-is.
        '''
        print('Handling a connect request:', addr, ':', port, userid)
        self.connect_node(trixy.TrixyOutput(addr, port))

        # TODO: need functionality to detect if the connection fails to
        #   notify the application accordingly.
        self.reply_request_granted(addr, port)


class Socks5Input(trixy.TrixyInput):
    '''
    Implements the SOCKS5 protocol as defined in RFC1928. At present,
    only CONNECT requests are supported.
    '''

    STATE_WAITING_FOR_METHODS = 0
    STATE_WAITING_FOR_AUTH = 1
    STATE_WAITING_FOR_REQUEST = 2
    STATE_PROXY_ACTIVE = 255

    SUPPORTED_METHODS = [b'\x00']

    def __init__(self, sock, addr):
        super().__init__(sock, addr)
        self.state = self.STATE_WAITING_FOR_METHODS

    def handle_packet_down(self, data):
        if self.state == self.STATE_PROXY_ACTIVE:
            self.forward_packet_down(data)

        elif self.state == self.STATE_WAITING_FOR_METHODS:
            if data.startswith(b'\x05') and len(data) > 2:
                nmethods = data[1]
                methods = data[2:]

                # Truncate method list if nmethods smaller, but attempt to
                # work regardless of a method count and actual count mismatch.
                # TODO: truncating is fingerpritable; is this desired?
                #   Is there another implementation to copy?
                if len(methods) > nmethods:
                    methods = methods[0:nmethods]
                self.handle_method_select(methods)

        elif self.state == self.STATE_WAITING_FOR_REQUEST:
            if not data.startswith(b'\x05'):  # Invalid
                self.close()  # Disconnect
                return

            if data[1] == 0x01:  # CONNECT request
                if data[3] == 0x01:  # IPv4 address
                    dst_addr = socket.inet_ntoa(data[4:8])
                    port = struct.unpack('!H', data[8:10])[0]
                elif data[3] == 0x03:  # Domain name
                    dst_addr_len = data[4]
                    dst_addr = data[5:5 + dst_addr_len].decode('ascii')
                    port = data[5 + dst_addr_len:7 + dst_addr_len]
                    port = struct.unpack('!H', port)[0]
                elif data[3] == 0x04:  # IPv6 address
                    dst_addr = socket.inet_ntop(socket.AF_INET6, data[4:20])
                    port = struct.unpack('!H', data[20:22])[0]
                else:
                    self.close()  # Disconnect; unsupported address type
                    return

                self.handle_connect_request(dst_addr, port, data[3:4])

            else:
                self.close()  # Disconnect
                return

    def handle_method_select(self, methods):
        '''
        Select the preferred authentication method from the list of
        client-supplied supported methods. The byte object of length
        one should be sent to self.reply_method to notify the client
        of the method selection.
        '''
        for method in self.SUPPORTED_METHODS:
            if method in methods:
                self.reply_method(method)
                self.state = self.STATE_WAITING_FOR_REQUEST
            else:
                self.close()  # Disconnect

    def handle_connect_request(self, addr, port, addrtype):
        '''
        The application connecting to this SOCKS4 input has requested
        that a connection be made to a remote host. At this point, that
        request can be accepted, modified, or declined.

        The default behavior is to accept the request as-is.
        '''
        self.connect_node(trixy.TrixyOutput(addr, port))

        # TODO: need functionality to detect if the connection fails to
        #   notify the application accordingly.
        self.reply_request_granted(addr, port, addrtype)
        self.state = self.STATE_PROXY_ACTIVE

    def reply_request_granted(self, addr, port, addrtype):
        '''
        Send a reply stating that the connection or bind request has
        been granted and that the connection or bind attempt was
        successfully completed.
        '''
        pkt = b'\x05\x00\x00' + addrtype
        if addrtype == b'\x01':  # IPv4
            pkt += socket.inet_aton(addr)
        elif addrtype == b'\x03':  # Domain name
            pkt += bytes((len(addr),))
            pkt += addr.encode('ascii')
        elif addrtype == b'\x04':  # IPv6
            pkt += socket.inet_pton(socket.AF_INET6, addr)
        else:
            raise Exception('Invalid address mode given')

        pkt += struct.pack('!H', port)

        self.send(pkt)

    def reply_method(self, method):
        '''
        Send a reply to the user letting them know which authentication
        method the server has selected. If the method 0xff is selected,
        close the connection because no method is supported.
        '''
        self.send(b'\x05' + method)
        if method == b'\xff':
            self.handle_close()


class Socks4Output(trixy.TrixyOutput):
    # TODO: implement assumed connections (useful for SOCKS over SSL)
    supports_assumed_connections = False


class Socks4aOutput(trixy.TrixyOutput):
    # TODO: implement assumed connections (useful for SOCKS over SSL)
    supports_assumed_connections = False


class Socks5Output(trixy.TrixyOutput):
    '''
    Implements the SOCKS5 protocol as defined in RFC1928.
    '''

    STATE_NONE = 0
    STATE_WAITING_FOR_SERVER_METHOD_SELECT = 1
    STATE_WAITING_FOR_BIND_RESPONSE = 251
    STATE_PROXY_ACTIVE = 254
    STATE_PROXY_DISABLED = 255

    IP_TYPE_V4 = 1
    IP_TYPE_V6 = 4
    IP_TYPE_DOMAIN = 3

    # TODO: implement assumed connections (useful for SOCKS over SSL)
    supports_assumed_connections = False

    def __init__(self, host, port, autoconnect=True,
                 proxyhost='127.0.0.1', proxyport=1080):
        super().__init__(proxyhost, proxyport, autoconnect)
        self.dsthost = dsthost = host
        self.dstport = port

        self.supported_auth_methods = [b'\x00']
        self.state = self.STATE_NONE

        self.downstream_buffer = b''

        # Check if the given host is an IP address
        try:
            self.dsthost_bytes = socket.inet_pton(socket.AF_INET, dsthost)
            self.ip_type = self.IP_TYPE_V4
        except socket.error:
            try:
                self.dsthost_bytes = socket.inet_pton(socket.AF_INET6, dsthost)
                self.ip_type = self.IP_TYPE_V6
            except socket.error:
                self.dsthost_bytes = (bytes((len(dsthost),)) +
                                      bytes(dsthost, 'ascii'))
                self.ip_type = self.IP_TYPE_DOMAIN

    def add_supported_auth_method(self, method):
        if isinstance(method, (int, float)):
            method = bytes((method,))
        elif not isinstance(method, bytes):
            raise TypeError('The supplied method must be a bytes object')

        if len(method) != 1:
            raise ValueError('The supplied method must be a single byte')

        if method not in self.supported_auth_methods:
            self.supported_auth_methods.append(method)

    def remove_supported_auth_method(self, method):
        if isinstance(method, (int, float)):
            method = bytes((method,))
        elif not isinstance(method, bytes):
            raise TypeError('The supplied method must be a bytes object')

        if len(method) != 1:
            raise ValueError('The supplied method must be a single byte')

        while method in self.supported_auth_methods:
            index = self.supported_auth_methods.index(method)
            self.supported_auth_methods.pop(index)

    def handle_connect(self):
        nummethods = len(self.supported_auth_methods)
        self.send(struct.pack('!BB%ip' % nummethods, 5, nummethods,
                              b''.join(self.supported_auth_methods)))
        self.state = self.STATE_WAITING_FOR_SERVER_METHOD_SELECT

    def handle_packet_down(self, data):
        if self.state == self.STATE_PROXY_ACTIVE:
            self.send(data)
        else:
            self.downstream_buffer += data

    def handle_packet_up(self, data):
        if self.state == self.STATE_PROXY_DISABLED:
            return

        elif self.state == self.STATE_PROXY_ACTIVE:
            self.forward_packet_up(data)

        elif self.state == self.STATE_WAITING_FOR_SERVER_METHOD_SELECT:
            if len(data) == 2 and data.startswith(b'\x05'):
                selected_auth_method = data[1:2]
                if selected_auth_method not in self.supported_auth_methods:
                    # TODO: check the RFC for graceful disconnection approach
                    raise SocksProtocolError('Server selected bad auth method')

                # Authentication complete; attempt the connection
                self.send(b'\x05\x01\x00' + bytes((self.ip_type,)) +
                          self.dsthost_bytes + struct.pack('!H', self.dstport))
                self.state = self.STATE_WAITING_FOR_BIND_RESPONSE

        elif self.state == self.STATE_WAITING_FOR_BIND_RESPONSE:
            if len(data) > 7 and data.startswith(b'\x05'):
                response = data[1]
                if response == 0:  # Success
                    self.state = self.STATE_PROXY_ACTIVE
                    self.send(self.downstream_buffer)
                elif response < 9:
                    self.handle_close()
                else:
                    SocksProtocolError('Unassigned bind response used')

    def set_state(self, state):
        old_state = self.state
        self.state = state
        self.handle_state_change(oldstate=old_state, newstate=state)

    def handle_state_change(self, oldstate, newstate):
        '''
        Be able to process events when they occur. It allows easier
        detection of when events occur if it is desired to implement
        different responses. It also allows detection of when the proxy
        is ready for use and can be used to use assume_connectecd to
        transfer control to a TrixyOutput.

        :param int oldstate: The old state number.
        :param int newstate: The new state number.
        '''
        pass


class SocksProtocolError(Exception):
    '''
    Someone sent some invalid data on the wire, and this is how to deal
    with it.
    '''
    pass

