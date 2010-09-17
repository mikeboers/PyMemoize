
import time

class Cache(object):
    """
    
    Anything dict-like can be used as the actual storage object as long as it
    supports standard key types (ie, strings, ints, tuples of these).
    
    Keys will be nested tuples. Values will be a tuple of (value, expiry_time)
    
    # Initialize the cache object.
    cache = Cache(default_store, namespace='namespace')
    
    # Manually get something.
    # Key: 'namespace:key'
    cache.get('key', func, args=(), kwargs={}, maxage=None)
    
    # Manually remove something.
    cache.del(key)
    cache.expire(key, ttl)
    cache.expire_at(key, time)
    cache.ttl(key)
    
    # Clear everything
    cache.clear()
    
    # Decorate a function.
    # Key: ('namespace', '__module__.__name__', (), ())
    @cache(maxage=60, args=(1, 2))
    def expensive_function(a, b):
        return a + b
    
    # The decorator adds a method to the object to clear the cache.
    expensive_function.clear_cache()
    
    # Key: ('namespace', ('key1', 'key2'))
    @cache('key1', 'key2')
    def allow_multiple_keys():
        return True
    
    # We can specify a store
    store = {}
    x = cache.get('manual-store', lambda: None, store=store)
    
    # Add a region. Regions simply provide different default values.
    cache.regions['short'] = {'maxage': 60}
    cache.get('something', func, region='short')
    
    # Key: ('namespace', ('something', ('short-key')))
    short = cache.partial('short-key', region='flickr')
    @short
    def func():
        pass

    """
    
    def __init__(self, store, **kwargs):
        kwargs['store'] = store
        self.regions = dict(default=kwargs)
    
    def get(self, key, func, args=(), kwargs={}, **opts):
        region = kwargs.get('region', 'default')
        for k, v in self.regions[region].iteritems():
            opts.setdefault(k, v)
        store = opts['store']
        
        try:
            value, expiry = store[key]
            if expiry is None or expiry > time.time():
                return value
            # This must be covered by the parent KeyError as well.
            del store[key]
        except KeyError:
            pass
        
        value = func(*args, **kwargs)
        
        expiry = opts.get('expiry')
        maxage = opts.get('maxage')
        if maxage is not None:
            expiry = (expiry or time.time()) + maxage
        store[key] = (value, expiry)
        
        return value



store = {}
cache = Cache(store)


def func(*args, **kwargs):
    print 'func(*%r, **%r)' % (args, kwargs)
    return 'done'

x = cache.get('key', func)
print x
print x













