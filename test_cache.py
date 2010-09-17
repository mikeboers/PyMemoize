
from cache import Cache

def test_basic():
    
    store = {}
    records = []
    cache = Cache(store)

    def func(*args, **kwargs):
        records.append((args, kwargs))
        return len(records)

    assert cache.get('key', func) == 1
    assert cache.get('key', func) == 1
