import asyncio
import socket
import ssl
import trixy


class TrixySSLInput(trixy.TrixyInput):
    '''
    Acts like a normal TrixyInput, but uses Python's ssl.wrap_socket()
    code to speak the SSL protocol back to applications that expect it.
    '''
    # TODO: re-write to use asyncio interface
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
    # TODO: check that a secure cipher is used by default, at least SSLv3
    supports_assumed_connections = True
    default_protocol = ssl.PROTOCOL_SSLv23

    def __init__(self, loop, host, port, autoconnect=True, **kwargs):
        super().__init__(loop, host, port, autoconnect=False, **kwargs)

        # Save the SSL Context or create a new one
        if 'context' in kwargs:
            self.context = context
        else:
            self.context = ssl.SSLContext(self.default_protocol)

        if autoconnect:
            self.connect()

    def connect(self):
        if self.context:
            coro = self.loop.create_connection(lambda: self, self.host,
                                           self.port, ssl=self.context)
        else:
            coro = self.loop.create_connection(lambda: self, self.host,
                                               self.port, ssl=True)
        task = asyncio.async(coro)


class TrixyTLSOutput(TrixySSLOutput):
    '''
    Acts identical to a TrixySSLOutput, but defaults to only accepting
    TLS for security reasons. This makes it slightly easier to prevent
    downgrade attacks, especially when doing hasty testing rather than
    full development.
    '''
    # TODO: check that the SSL context is enforced.
    default_protocol = ssl.PROTOCOL_TLSv1  # Allows for TLSv1 and up
