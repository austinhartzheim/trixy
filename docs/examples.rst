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

The following code creates a Trixy proxy server on a local port and then sends the output to austinhartzheim.me on port 80::

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

This example was taken from the `README file <https://github.com/austinhartzheim/Trixy/blob/master/README.md>`_.


.. _changing_website_responses:

Changing Website Responses
==========================

The following example takes an incoming connection on a local port, redirects it to a remove webserver on port 80 (specifically, the example.com server), and then modifies the response from example.com::

   #! /usr/bin/env python3
   import asyncore
   import trixy
   
   REMOTE_ADDR = '93.184.216.119' # IP for example.com
   REMOTE_PORT = 80


   class ExampleReplacer(trixy.TrixyProcessor):
   
       def handle_packet_up(self, data):
           data = data.replace(b'Example Domain', b'Win Domain!')
           self.forward_packet_up(data)
        
   
   class CustomInput(trixy.TrixyInput):
       def __init__(self, sock, addr):
           super().__init__(sock, addr)
   
           processor = ExampleReplacer()
           self.connect_node(processor)

           output = trixy.TrixyOutput(REMOTE_ADDR, REMOTE_PORT)
           processor.connect_node(output)
           print(processor.upstream_nodes)

   
   if __name__ == '__main__':
       server = trixy.TrixyServer(CustomInput, '0.0.0.0', 80)
       asyncore.loop()

This example was originally posted `on the developer's website <http://austinhartzheim.me/projects/python3-trixy/>`_.

More Eamples Soon
=================

More examples are on their way! But, if you write one first, feel free to send a pull request on `Github <https://github.com/austinhartzheim/Trixy/>`_.
