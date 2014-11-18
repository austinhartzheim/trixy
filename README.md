# Trixy

Some software requires the ability to take input data from a network socket, act on that data, and the send it on to a remote host (possibly in a modified state). The Trixy module allows that to be done through a simple interface. Simply create a trixy server with a handler that does what is desired. Here is an example that tunnels unmodified data to a remote host:

```python
#! /usr/bin/env python3
import asyncore
import trixy


class TrixyTunnel(trixy.SimpleTunnel):
    def initiate(self):
        # Determine which host to connect to
        self.remote(('austinhartzheim.me', 80))  # Tunnel to this web server

# Run the tunnel from a port on localhost
server = trixy.TrixyProxyServer(TrixyTunnel, 'localhost', 80)
asyncore.loop()
```

## Running Unit Tests
The best way to run the unit tests is to use nosetests for Python 3. Alternatively, you can run the tests.py script included in the repository.