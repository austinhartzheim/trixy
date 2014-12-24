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
        print('Got connect')
        self.first_packet = True

    def handle_packet_down(self, data):
        print('pd: ', data)
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
        print('handle_proxy_request: ', data)
        if data.startswith(b'\x04\x01'):  # CONNECT request
            port = struct.unpack('!H', data[2:4])[0]
            addr = socket.inet_ntoa(data[4:8])
            userid = data[8:-1]

            print('DEBUG: Got SOCKS4 connect request:')
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

    def reply_request_granted(self, addr, port):
        '''
        Send a reply stating that the connection or bind request has
        been granted and that the connection or bind attempt was
        successfully completed.
        '''
        # 90 is the response for a granted request
        self.send(struct.pack('!BBH4p', 0x00, 90, port,
                              socket.inet_aton(addr)))

    def reply_request_failed(self, addr, port):
        '''
        Send a reply stating that the request was rejected (perhaps due
        to a firewall rule forbidding the connection or binding) or
        that it failed (i.e., the remote host could not be connected to
        or the requested port could not be bound).
        '''
        # 91 is the response for a rejected or failed request
        self.send(struct.pack('!BBH4p', 0x00, 91, port,
                              socket.inet_aton(addr)))

    def reply_request_rejected(self, addr, port):
        '''
        Send a reply saying that the request was rejected because the
        SOCKS server could not connect to the client's identd server.
        '''
        # 92 is the response for a request being rejected because the SOCKS
        #   server cannot connect to identd on the client.
        self.send(struct.pack('!!BBH4p', 0x00, 92, port,
                              socket.inet_aton(addr)))

    def reply_request_rejected_id_mismatch(self, addr, port):
        '''
        Send a reply saying that the request was rejected because the
        SOCKS server was sent an ID by the client that did not match
        the ID returned by identd on the client's computer.
        '''
        # 93 is the response for rejections due to the client program and
        #   identd reporting different user-ids.
        self.send(struct.pack('!!BBH4p', 0x00, 93, port,
                              socket.inet_aton(addr)))


class Socks4aInput(trixy.TrixyInput):
    '''
    Implements the SOCKS4a protocol, which is the same as the SOCKS4
    protocol except for the addition of DNS resolution as described
    here: http://www.openssh.com/txt/socks4a.protocol
    '''
    pass


class Socks5Input(trixy.TrixyInput):
    pass


class Socks4Output(trixy.TrixyOutput):
    pass


class Socks4aOutput(trixy.TrixyOutput):
    pass


class Socks5Output(trixy.TrixyOutput):
    pass
