.. Trixy documentation master file, created by
   sphinx-quickstart on Mon Dec 22 23:44:09 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Trixy documentation!
====================

.. toctree::
   :maxdepth: 2

   getting_started.rst
   examples.rst
   code.rst

What is Trixy?
--------------

Trixy is designed to be used in a variety of situations involving network traffic interception, injection, and modification. The software allows you to easily get your code running between two endpoints of a network connection. This allows you to easily:

* Log protocols for reverse engineering.
* Modify packets on bidirectional connections.
* Inject traffic into a network connection.
* Develop and test protocol parsers.
* Monitor applications for suspicious network activity.
* Sanitize traffic, removing any undesired information.
* Develop application level firewalls.  

Here are some practical examples of the above:

* Cheating at video games:

  * Exploit server-client trust by modifying packets indicating how much money a player has.
  * Drop packets that indicate damage to a player.

* Removing advertising and trackers from webpages.
* Performing man-in-the-middle attacks.

Other Documentation
-------------------

If you are stuck, you should also check the following sources for information about Trixy:

* `The developer's website <http://austinhartzheim.me/projects/python3-trixy/>`_
* `The Github repository <https://github.com/austinhartzheim/Trixy/>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

