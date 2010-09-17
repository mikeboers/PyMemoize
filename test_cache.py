
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
    time.sleep(0.06)
    assert cache.get('expires', func, maxage=0.05) == 3


def test_namespace():
    
    store = {}
    cache = Cache(store, namespace='ns')
    cache.get('key', lambda: 'value')
    assert ('ns', 'key') in store


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
    
