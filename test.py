#! /usr/bin/env python3
'''
Run unit tests on Trixy.
'''
import sys
import unittest

# Warn people that test.py might eventually be gone. Or, at least that
# it is annoying to maintain.
print('''
WARNING: test.py is deprecated. It might be gone some day because it is
a real pain to update the lists of tests below. It is much easier to
just use nosetests which implements test discovery automatically.

So, you should switch to nosetests soon.
''')

sys.path.insert(1, 'trixy')  # Load trixy from local src directory
sys.path.insert(1, 'tests')  # Allow tests to be run stand-alone from IDE

from tests.test_chaining import *
from tests.test_closing import *
from tests.test_proxy import *


if __name__ == '__main__':
    unittest.main()
