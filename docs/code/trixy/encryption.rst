trixy.encryption
================

The Trixy encryption module holds inputs and outputs that have support for encryption that applications might expect. For example, the :py:class:`trixy.encryption.TrixySSLInput` can be used to trick a browser into thinking it is creating an encrypted connection, but the connection can then be re-routed through an unencrypted :py:class:`trixy.TrixyOutput` for easier monitoring.

.. automodule:: trixy.encryption
   :members:
