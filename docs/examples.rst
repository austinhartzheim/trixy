.. _examples:

********
Examples
********

.. toctree::
   :maxdepth: 2


Here are some examples of how to use Trixy:

.. _passthrough_proxy:

Passthrough Proxy
=================

The following code creates a Trixy proxy server on local port 8080 and then sends the output to austinhartzheim.me on port 80::

   # /usr/bin/env python3
   import asyncio
   import trixy

   class CustomInput(trixy.TrixyInput):
       def __init__(self, loop):
            super().__init__(loop)

            # This output class automatically connects to austinhartzheim.me
            output = trixy.TrixyOutput(loop, 'austinhartzheim.me', 80)
            self.connect_node(output)

   if __name__ == '__main__':
       # Run the Trixy server on localhost, port 8080
       loop = asyncio.get_event_loop()
       coro = loop.create_server(lambda: CustomInput(loop),
                                 '127.0.0.1', 8080)
       loop.create_task(coro)
       loop.run_forever()


This example was modified from the `README file <https://github.com/austinhartzheim/Trixy/blob/master/README.md>`_.


.. _changing_website_responses:

Changing Website Responses
==========================

The following example takes an incoming connection on a localhost port 8080, redirects it to example.com on port 80, and then modifies the response from example.com::

   #! /usr/bin/env python3
   import asyncio
   import trixy

   REMOTE_ADDR = '93.184.216.34'  # IP for example.com
   REMOTE_PORT = 80


   class ExampleReplacer(trixy.TrixyProcessor):

       def handle_packet_up(self, data):
           '''
           The HTTP headers will show that we are connecting to 127.0.0.1
           on port 8080, which will cause example.com to return an error.
           So, we fix this to show the expected header.
           '''
           data = data.replace(b'127.0.0.1:8080', b'example.com')
           self.forward_packet_up(data)

       def handle_packet_down(self, data):
           '''
           Check all incoming packets; replace some basic information on
           the page with our own information. For example, replace the
           "Example Domain" heading with the text "Trixy Example Domain".
           '''
           data = data.replace(b'Example Domain', b'Trixy Example Domain')
           data = data.replace(b'://www.iana.org/domains/example',
                               b's://github.com/austinhartzheim/Trixy')
           self.forward_packet_down(data)


   class CustomInput(trixy.TrixyInput):

       def __init__(self, loop):
           super().__init__(loop)

           processor = ExampleReplacer()
           self.connect_node(processor)

           output = trixy.TrixyOutput(loop, REMOTE_ADDR, REMOTE_PORT)
           processor.connect_node(output)


   if __name__ == '__main__':
       # Bind to localhost, port 8080
       loop = asyncio.get_event_loop()
       coro = loop.create_server(lambda: CustomInput(loop),
                                 '127.0.0.1', 8080)
       loop.create_task(coro)
       loop.run_forever()

This example was originally posted `on the developer's website <http://austinhartzheim.me/projects/python3-trixy/>`_.

More Eamples Soon
=================

More examples are on their way! But, if you write one first, feel free to send a pull request on `Github <https://github.com/austinhartzheim/Trixy/>`_.
