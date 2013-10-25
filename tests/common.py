from time import time as _time
from unittest import TestCase as Base

import memoize
from memoize import Memoizer


class Timer(object):

    def __init__(self, clock=None):
        self.offset = 0.0
        self.clock = clock or _time

    def sleep(self, offset):
        self.offset += offset

    def __call__(self):
        return self.clock() + self.offset


memoize.core.time = time = Timer()


class TestCase(Base):

    memo_kwargs = {}

    def setUp(self):
        self.store = {}
        self.memo = Memoizer(self.store, **self.memo_kwargs)

