.. _getting_started:

***************
Getting Started
***************

Here are some instructions for getting started with Trixy.

.. _installing_trixy:

Installing Trixy
================

Installing Trixy is just a simple command. Note that you should use the Python 3 version::

   sudo pip install trixy

Alternatively, you can download a source tarball or zip file from `PyPI <https://pypi.python.org/pypi/Trixy/1.0.0>`_ or `Github <https://github.com/austinhartzheim/Trixy/releases>`_. Then, you can extract it and install it by running::

   sudo python3 setup.py install

.. _the_basics:

The Basics: Theory
======================

Trixy is structured into four component classes: servers, inputs, outputs, and processors. Servers are responsible for capturing incoming connections and passing them to an input class. The input class then takes these connections and builds processing chains for them. These processing chains consist of processors, which modify data passing through them, and outputs, which forward the data stream (including any modifications) to a remote host.

To use Trixy, you should import it into your Python project and create subclasses of :py:class:`trixy.TrixyInput`. Inside the :py:meth:`~__init__` method of the subclass, you should create a chain of nodes which the data should pass through. As an example::

   def __init__(self, loop):
       super().__init__(loop)

       processor = trixy.TrixyProcessor()
       self.connect_node(processor)
       processor.connect_node(trixy.TrixyOutput(loop, '127.0.0.1', 9999))

The first line creates a processor node. The default :py:class:`trixy.TrixyProcessor` class does not do anything other than forward the data, so you should create a subclass and override some of its methods to modify its behavior (covered next). The second line connects the input instance with this processor node so that the input will forward the data it gets to the processor. The last line connects the processor node to a :py:class:`trixy.TrixyOutput` instance that is created at the same time. This causes the processor to forward data it gets to the output (after making any modifications). The default output that is used in this case creates a TCP connection to localhost on port 9999 and forwards the data there.

Modifying Data: Custom Processors
=================================

Trixy is great for simply re-routing data, but its real power lies in its ability to process the data on the fly. To do this, you need to create a custom :py:class:`trixy.TrixyProcessor` subclass.

When you are creating your own custom processor, you should modify packets like so::

   class CustomProcessor(trixy.TrixyProcessor):
       def handle_packet_down(self, data):
           # Modify the data variable here
	   self.forward_packet_down(data)

       def handle_packet_up(self, data):
           # Modify the data variable here
           self.forward_packet_up(data)

The :py:meth:`!handle_packet_down` method is called to process data flowing from the output to the input. The :py:meth:`!handle_packet_up` method is used to process data moving from the input to the output. The calls to the :py:meth:`!forward_packet_down` and :py:meth:`!forward_packet_up` then send the modified data on its way to the next node(s) in the chain.

.. NOTE::
   It is also the case that you can ommit calls to :py:meth:`!forward_packet_down` and :py:meth:`!forward_packet_up` when you want to drop a packet.
