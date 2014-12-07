import socket
import ssl
import trixy


class TrixySSLInput(trixy.TrixyInput):
    def __init__(self, sock, addr, **kwargs):
        super().__init__(sock, addr)
        self.socket = ssl.wrap_socket(self.socket, server_side=True, **kwargs)


class TrixySSLOutput(trixy.TrixyOutput):
    def __init__(self, host, port, autoconnect=True, **kwargs):
        super().__init__(host, port, autoconnect=False, **kwargs)

        if autoconnect:
            self.connect((host, port))

    def setup_socket(self, host, port, autoconnect, **kwargs):
        addr_info = socket.getaddrinfo(host, port)
        sock = ssl.wrap_socket(socket.socket(addr_info[0][0], addr_info[0][1])
                               ** kwargs)
        self.set_socket(sock)
