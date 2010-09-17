
import time
from autocache.core import *

def test_basic():
    
    store = {}
    records = []
    cache = Cache(store)

    def func(*args, **kwargs):
        records.append((args, kwargs))
        return len(records)

    # Only should get called once.
    assert cache.get('key', func) == 1
    assert cache.get('key', func) == 1
    
    # Keys should expire.
    assert cache.get('expires', func, maxage=0.05) == 2
    assert cache.get('expires', func, maxage=0.05) == 2
    assert cache.exists('expires')
    time.sleep(0.06)
    assert not cache.exists('expires')
    assert cache.get('expires', func, maxage=0.05) == 3

def test_decorator():
    
    store = {}
    record = []
    cache = Cache(store)
    
    @cache
    def func_1(arg=1):
        record.append(arg)
        return arg
    
    assert func_1(1) == 1
    assert len(record) == 1
    assert func_1(1) == 1
    assert len(record) == 1
    assert func_1(2) == 2
    assert len(record) == 2


def test_region():
    
    store_a = {}
    store_b = {}
    cache = Cache({})
    cache.regions.update(
        a=dict(store=store_a),
        b=dict(store=store_b),
    )
    
    @cache(region='a')
    def func1():
        return 1
    @cache(region='b')
    def func2():
        return 2
    
    assert func1() == 1
    assert len(store_a) == 1
    assert len(store_b) == 0
    
    assert func2() == 2
    assert len(store_b) == 1
    
    print 'default', cache.regions['default']['store']
    print 'a', store_a
    print 'b', store_b


def test_region_parents():
    
    store = {}
    cache = Cache(store, namespace='master')
    cache.regions['a'] = dict(namespace='a', expiry=1)
    cache.regions['b'] = dict(namespace='b', parent='a')
    
    cache.get('key', str)
    assert 'master:key' in store
    assert store['master:key'][EXPIRY_INDEX] == None
    
    cache.get('key', str, region='a')
    print store['a:key']
    assert store['a:key'][EXPIRY_INDEX] == 1
    
    cache.get('key', str, region='b')
    assert store['b:key'][EXPIRY_INDEX] == 1
    
    cache.get('key', str, region='b', namespace=None)
    print store
    assert store['key'][EXPIRY_INDEX]== 1
    


def test_func_keys():
    
    cache = Cache({})
    
    @cache
    def f(a, b=2, *args, **kwargs):
        pass
    
    assert f.key((1, 2, 3), {})   == __name__ + '.f(1, 2, 3)'
    assert f.key((2, 3), {'a':1}) == __name__ + '.f(1, 2, 3)'
    assert f.key((3, 4), {'a':1, 'b':2, 'c':5}) == __name__ + '.f(1, 2, 3, 4, c=5)'
    assert f.key((1, ), {})   == __name__ + '.f(1, 2)'
    
    @cache('key')
    def h():
        pass
    
    assert h.key((), {}) == "'key':" + __name__ + '.h()'
    
    @cache('key', 'sub')
    def g(a=1, b=2):
        pass
    
    assert g.key((), {})         == "'key','sub':" + __name__ + '.g(1, 2)'
    assert g.key((3, ), {})      == "'key','sub':" + __name__ + '.g(3, 2)'
    assert g.key((3, ), {'a':2}) == "'key','sub':" + __name__ + '.g(2, 3)'


def test_namespace():

    store = {}
    cache = Cache(store, namespace='ns')
    cache.get('key', lambda: 'value')
    assert 'ns:key' in store

    @cache
    def f(): pass
    f()
    assert'ns:%s.f()' % __name__ in store
    f.delete()
    assert'ns:%s.f()' % __name__ not in store
    
    @cache(namespace='ns2')
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
    cache = Cache(store, lock=Lock)
    
    @cache
    def f(*args, **kwargs):
        stack.append(('call', args, kwargs))
    
    f(1, 2, 3)
    assert stack == [('lock', 'test_main.f(1, 2, 3)'), ('call', (1, 2, 3), {}), ('unlk', 'test_main.f(1, 2, 3)')]
    


def test_etag():
    
    store = {}
    cache = Cache(store)
    
    def func():
        func.count += 1
        return func.count
    func.count = 0
    
    assert cache.get('key', func) == 1
    assert cache.etag('key') is None
    
    assert cache.get('key', func, etag='a') == 2
    assert cache.etag('key') == 'a'
    
    assert cache.get('key', func, etag='b') == 3
    assert cache.etag('key') == 'b'
    
    # It does not go up here.
    assert cache.get('key', func) == 3


def test_etagger():
    
    store = {}
    cache = Cache(store)
    state = []
    
    def etagger():
        return len(state)
    
    @cache(etagger=etagger)
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
    cache = Cache(store)
    
    def func():
        func.count += 1
        return func.count
    func.count = 0
    
    assert cache.get('key', func, maxage=10) == 1
    assert cache.get('key', func, maxage=10) == 1
    
    # This will not recalculate as 1 second has not passed.
    assert cache.get('key', func, maxage=1) == 1
    
    time.sleep(0.01)
    
    # This should recalculate.
    assert cache.get('key', func, maxage=0.005) == 2
    
    
    
    
    