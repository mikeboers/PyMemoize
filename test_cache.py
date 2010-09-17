
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
    
