import socket
import ssl
import trixy


class TrixySSLInput(trixy.TrixyInput):
    pass  # TODO: implement


class TrixySSLOutput(trixy.TrixyOutput):
    def __init__(self, host, port, autoconnect=True):
        super().__init__(host, port, autoconnect=False)

        if autoconnect:
            self.connect((host, port))

    def setup_socket(self, host, port, autoconnect):
        addr_info = socket.getaddrinfo(host, port)
        sock = ssl.wrap_socket(socket.socket(addr_info[0][0], addr_info[0][1]))
        self.set_socket(sock)
