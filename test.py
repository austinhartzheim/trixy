#! /usr/bin/env python3
'''
Run unit tests on Trixy.
'''
import sys
import unittest

sys.path.insert(1, 'trixy')  # Load trixy from local src directory
sys.path.insert(1, 'tests')  # Allow tests to be run stand-alone from IDE

from tests.test_trixyproxyserver import *


if __name__ == '__main__':
    unittest.main()
