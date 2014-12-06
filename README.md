# Trixy

Some software requires the ability to take input data from a network socket, act on that data, and the send it on to a remote host (possibly in a modified state). The Trixy module allows that to be done through a simple interface. Simply create a trixy server with a handler that does what is desired. Here is an example that tunnels unmodified data to a remote host:

```python
# /usr/bin/env python3
import asyncore
import trixy

class CustomInput(trixy.TrixyInput):
    def __init__(self, sock, addr):
        super().__init__(sock, addr)

        # This output class connects to this hostname/port by default
        output = trixy.TrixyOutput('austinhartzheim.me', 80)
        self.connect_node(output)

if __name__ == '__main__':
    # Run the Trixy server on localhost, port 8080
    server = trixy.TrixyServer(CustomInput, '127.0.0.1', 8080)
    asyncore.loop()
```

## Running Unit Tests
The best way to run the unit tests is to use nosetests for Python 3. Alternatively, you can run the test.py script included in the repository.