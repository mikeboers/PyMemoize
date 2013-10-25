from unittest import TestCase as Base

from memoize.core import *
from memoize.time import time, sleep
from memoize import Memoizer


class TestCase(Base):

    memo_kwargs = {}

    def setUp(self):
        self.store = {}
        self.memo = Memoizer(self.store, **self.memo_kwargs)

