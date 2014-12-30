import socket
import ssl
import trixy


class TrixySSLInput(trixy.TrixyInput):
    '''
    Acts like a normal TrixyInput, but uses Python's ssl.wrap_socket()
    code to speak the SSL protocol back to applications that expect it.
    '''
    def __init__(self, sock, addr, **kwargs):
        super().__init__(sock, addr)
        self.socket = ssl.wrap_socket(self.socket, server_side=True, **kwargs)


class TrixySSLOutput(trixy.TrixyOutput):
    '''
    Acts like a normal TriyOutput, but uses Python's ssl.wrap_socket()
    code to speak the SSL protocol to servers that expect it.

    By default this class allows for SSL2 and SSL3 connections in
    addition to TLS. If you want to specify different settings, you can
    pass your own context to setup_socket().
    '''
    default_protocol = ssl.PROTOCOL_SSLv23

    def __init__(self, host, port, autoconnect=True, **kwargs):
        super().__init__(host, port, autoconnect=False, **kwargs)

        if autoconnect:
            self.connect((host, port))

    def setup_socket(self, host, port, autoconnect, context=None, **kwargs):
        '''
        :param str host: The hostname the output should connect to.
        :param int port: The port this output should connect to.
        :param bool autoconnect: Should the connection be established
          when the __init__ method is called?
        :param ssl.SSLContext context: this optional parameter allows
          for custom security settings such as certificate verification
          and alternate SSL/TLS versions upport.
        :param **kwargs: Anything else that should be passed to the
          SSLContext's wrap_socket method.
        '''
        addr_info = socket.getaddrinfo(host, port)
        if not context:
            context = ssl.SSLContext(self.default_protocol)
        sock = context.wrap_socket(socket.socket(addr_info[0][0],
                                                 addr_info[0][1]), **kwargs)
        self.set_socket(sock)


class TrixyTLSOutput(trixy.TrixyOutput):
    '''
    Acts identical to a TrixySSLOutput, but defaults to only accepting
    TLS for security reasons. This makes it slightly easier to prevent
    downgrade attacks, especially when doing hasty testing rather than
    full development.
    '''
    default_protocol = ssl.PROTOCOL_TLSv1  # Allows for TLSv1 and up
