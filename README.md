# Trixy

Some software requires the ability to take input data from a network socket, act on that data, and the send it on to a remote host (possibly in a modified state). The Trixy module allows that to be done through a simple interface. Simply create a trixy server with a handler that does what is desired. Here is an example that tunnels unmodified data to a remote host:

```python
import asyncio
import trixy


class CustomInput(trixy.TrixyInput):
    def __init__(self, loop):
        super().__init__(loop)

        to = trixy.TrixyOutput(loop)
        coro = loop.create_connection(lambda: to,
                                      '127.0.0.1', 9999)
        asyncio.async(coro)
        self.connect_node(to)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_server(lambda: CustomInput(loop),
                              '127.0.0.1', 9997)
    loop.create_task(coro)
    loop.run_forever()
```

## Running Unit Tests
The best way to run the unit tests is to use nosetests for Python 3. Alternatively, you can run the test.py script included in the repository.