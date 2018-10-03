from memoize.options import OptionProperty

from .common import *


class TestOptionProperty(TestCase):

    class cls(object):
        opt = OptionProperty('opt')
        def __init__(self):
            self.opts = {}

    def test_set_constant(self):
        x = self.cls()
        x.opt = 3
        self.assertEqual(x.opt(), 3)

    def test_set_func(self):
        x = self.cls()
        x.opt = lambda: 4
        self.assertEqual(x.opt(), 4)

    def test_decorate(self):
        x = self.cls()
        @x.opt
        def x_opt():
            return 5
        self.assertEqual(x.opt(), 5)

    def test_multiple(self):
        x = self.cls()
        x.opt = lambda: 6
        self.assertEqual(x.opt(), 6)
        @x.opt
        def x_opt():
            return 7
        self.assertEqual(x.opt(), 7)
        x.opt = 8
        self.assertEqual(x.opt(), 8)

    def test_constant_args(self):
        x = self.cls()
        x.opt = 9
        self.assertEqual(x.opt(1), 9)

    def test_count_args(self):
        x = self.cls()
        @x.opt
        def count_args(*args, **kwargs):
            return len(args) + len(kwargs)
        self.assertEqual(x.opt(), 0)
        self.assertEqual(x.opt(1), 1)
        self.assertEqual(x.opt(a=2, b=3), 2)
        self.assertEqual(x.opt(1, a=2, b=3), 3)




