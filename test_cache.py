
import time
from cache import Cache

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
    assert store['master:key'] == ('', None)
    
    cache.get('key', str, region='a')
    assert store['a:key'] == ('', 1)
    
    cache.get('key', str, region='b')
    assert store['b:key'] == ('', 1)
    
    cache.get('key', str, region='b', namespace=None)
    print store
    assert store['key'] == ('', 1)
    


def test_func_keys():
    
    cache = Cache({})
    
    @cache
    def f(a, b=2, *args, **kwargs):
        pass
    
    assert f.get_key((1, 2, 3), {})   == __name__ + '.f(1, 2, 3)'
    assert f.get_key((2, 3), {'a':1}) == __name__ + '.f(1, 2, 3)'
    assert f.get_key((3, 4), {'a':1, 'b':2, 'c':5}) == __name__ + '.f(1, 2, 3, 4, c=5)'
    assert f.get_key((1, ), {})   == __name__ + '.f(1, 2)'
    
    @cache('key')
    def h():
        pass
    
    assert h.get_key((), {}) == "'key':" + __name__ + '.h()'
    
    @cache('key', 'sub')
    def g(a=1, b=2):
        pass
    
    assert g.get_key((), {})         == "'key','sub':" + __name__ + '.g(1, 2)'
    assert g.get_key((3, ), {})      == "'key','sub':" + __name__ + '.g(3, 2)'
    assert g.get_key((3, ), {'a':2}) == "'key','sub':" + __name__ + '.g(2, 3)'


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
    assert stack == [('lock', 'test_cache.f(1, 2, 3)'), ('call', (1, 2, 3), {}), ('unlk', 'test_cache.f(1, 2, 3)')]
    
    
    