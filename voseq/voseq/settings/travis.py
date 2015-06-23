"""
To be used in Travis CI so we can skip running the tests for NCBI blast, which
fails most of the time due to network problems.
"""

from .testing import *


print('in Travis')
TRAVIS = True
