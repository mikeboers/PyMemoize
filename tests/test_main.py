import time
from memoize.core import *


def test_basic():
    store = {}
    records = []
    memo = Memoizer(store)

    def func(*args, **kwargs):
        records.append((args, kwargs))
        return len(records)

    # Only should get called once.
    assert memo.get('key', func) == 1
    assert memo.get('key', func) == 1

    # Keys should expire.
    assert memo.get('expires', func, max_age=0.05) == 2
    assert memo.get('expires', func, max_age=0.05) == 2
    assert memo.exists('expires')
    time.sleep(0.06)
    assert not memo.exists('expires')
    assert memo.get('expires', func, max_age=0.05) == 3


def test_decorator():
    store = {}
    record = []
    memo = Memoizer(store)

    @memo
    def func_1(arg=1):
        record.append(arg)
        return arg

    assert func_1(1) == 1
    assert len(record) == 1
    assert func_1(1) == 1
    assert len(record) == 1
    assert func_1(arg=2) == 2
    assert len(record) == 2


def test_region():
    store_a = {}
    store_b = {}
    memo = Memoizer({})
    memo.regions.update(
        a=dict(store=store_a),
        b=dict(store=store_b),
    )

    @memo(region='a')
    def func1():
        return 1

    @memo(region='b')
    def func2():
        return 2

    assert func1() == 1
    assert len(store_a) == 1
    assert len(store_b) == 0

    assert func2() == 2
    assert len(store_b) == 1

    # print 'default', memo.regions['default']['store']
    # print 'a', store_a
    # print 'b', store_b


def test_region_parents():
    store = {}
    memo = Memoizer(store, namespace='master')
    memo.regions['a'] = dict(namespace='a', expiry=1)
    memo.regions['b'] = dict(namespace='b', parent='a')

    memo.get('key', str)
    assert 'master:key' in store
    assert store['master:key'][EXPIRY_INDEX] is None

    memo.get('key', str, region='a')
    # print store['a:key']
    assert store['a:key'][EXPIRY_INDEX] == 1

    memo.get('key', str, region='b')
    assert store['b:key'][EXPIRY_INDEX] == 1

    memo.get('key', str, region='b', namespace=None)
    # print store
    assert store['key'][EXPIRY_INDEX] == 1


def test_func_keys():

    memo = Memoizer({})

    @memo
    def f(a, b=2, *args, **kwargs):
        pass

    assert f.key((1, 2, 3), {}) == __name__ + '.f(1, 2, 3)'
    assert f.key((2, 3), {'a': 1}) == __name__ + '.f(1, 2, 3)'
    assert f.key((3, 4), {'a': 1, 'b': 2, 'c': 5}) == __name__ + '.f(1, 2, 3, 4, c=5)'
    assert f.key((1, ), {}) == __name__ + '.f(1, 2)'

    @memo('key')
    def h():
        pass

    assert h.key((), {}) == "'key':" + __name__ + '.h()'

    @memo('key', 'sub')
    def g(a=1, b=2):
        pass

    assert g.key((), {}) == "'key','sub':" + __name__ + '.g(1, 2)'
    assert g.key((3, ), {}) == "'key','sub':" + __name__ + '.g(3, 2)'
    assert g.key((3, ), {'a': 2}) == "'key','sub':" + __name__ + '.g(2, 3)'


def test_namespace():

    store = {}
    memo = Memoizer(store, namespace='ns')
    memo.get('key', lambda: 'value')
    assert 'ns:key' in store

    @memo
    def f():
        pass

    f()
    assert'ns:%s.f()' % __name__ in store
    f.delete()
    assert'ns:%s.f()' % __name__ not in store

    @memo(namespace='ns2')
    def g(*args): pass
    g(1, 2, 3)
    assert'ns2:%s.g(1, 2, 3)' % __name__ in store


def test_lock():

    stack = []

    class Lock(object):
        def __init__(self, key):
            self.key = key

        def acquire(self, timeout):
            stack.append(('lock', self.key))
            return True

        def release(self, *args):
            stack.append(('unlk', self.key))

    store = {}
    memo = Memoizer(store, lock=Lock)

    @memo
    def f(*args, **kwargs):
        stack.append(('call', args, kwargs))

    f(1, 2, 3)
    assert stack == [('lock', 'test_main.f(1, 2, 3)'), ('call', (1, 2, 3), {}), ('unlk', 'test_main.f(1, 2, 3)')]


def test_etag():

    store = {}
    memo = Memoizer(store)

    def func():
        func.count += 1
        return func.count
    func.count = 0

    assert memo.get('key', func) == 1
    assert memo.etag('key') is None

    assert memo.get('key', func, etag='a') == 2
    assert memo.etag('key') == 'a'

    assert memo.get('key', func, etag='b') == 3
    assert memo.etag('key') == 'b'

    # It does not go up here.
    assert memo.get('key', func) == 3


def test_etagger():

    store = {}
    memo = Memoizer(store)
    state = []

    def etagger():
        return len(state)

    @memo(etagger=etagger)
    def state_sum():
        state_sum.count += 1
        return sum(state, 0)
    state_sum.count = 0

    assert state_sum() == 0
    assert state_sum() == 0
    assert state_sum.count == 1

    state.extend((1, 2, 3))

    assert state_sum() == 6
    assert state_sum.count == 2


def test_dynamic_maxage():

    store = {}
    memo = Memoizer(store)

    def func():
        func.count += 1
        return func.count

    func.count = 0

    assert memo.get('key', func, max_age=10) == 1
    assert memo.get('key', func, max_age=10) == 1

    # This will not recalculate as 1 second has not passed.
    assert memo.get('key', func, max_age=1) == 1

    time.sleep(0.01)

    # This should recalculate.
    assert memo.get('key', func, max_age=0.005) == 2


def test_method_decorator():

    store = {}
    memo = Memoizer(store)

    class A(object):

        def __init__(self):
            self.records = []

        @memo
        def append(self, *args, **kwargs):
            self.records.append((args, kwargs))
            return len(self.records)

    a = A()
    b = A()
    assert not a.append.exists((1, ))
    assert a.append(1) == 1
    assert a.append.exists((1, ))
    assert a.append(1) == 1
    assert a.append(2) == 2
    assert b.append(1) == 1

