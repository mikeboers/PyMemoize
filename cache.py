"""

TODO:
    - Add locks so we dont have two processes calculating the same thing.

Anything dict-like can be used as the actual storage object as long as it
supports standard key types (ie, strings, ints, tuples of these).

Keys will be nested tuples. Values will be a tuple of (value, expiry_time)

# Initialize the cache object.
cache = Cache(default_store, namespace='namespace')

# Manually get something.
# Key: 'namespace:key'
cache.get('key', func, args=(), kwargs={}, maxage=None)

# Manually remove something.
cache.delete(key)
cache.expire(key, ttl)
cache.expire_at(key, time)
cache.ttl(key)

# Clear everything
cache.clear()

# Decorate a function.
# Key: ('namespace', '__module__.__name__', (), ())
@cache(maxage=60)
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
import time
import functools

class Cache(object):
    """

    """
    
    def __init__(self, store, **kwargs):
        kwargs['store'] = store
        self.regions = dict(default=kwargs)
    
    def _expand_opts(self, opts):
        region = opts.get('region', 'default')
        for k, v in self.regions[region].iteritems():
            opts.setdefault(k, v)
        
    def get(self, key, func, args=(), kwargs={}, **opts):
        self._expand_opts(opts)
        store = opts['store']
        
        namespace = opts.get('namespace')
        if namespace is not None:
            key = (namespace, key)
        
        pair = store.get(key)
        if pair is not None:
            value, expiry = pair
            if expiry is None or expiry > time.time():
                return value
            try:
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
    
    def delete(self, key, **opts):
        self._expand_opts(opts)
        store = opts['store']
        try:
            del store['key']
        except KeyError:
            pass
    
    def __call__(self, *args, **opts):
        """Decorator."""
        
        if args and hasattr(args[0], '__call__'):
            func = args[0]
            args = args[1:]
        else:
            # Build the decorator.
            return lambda func: self(func, *args, **opts)
        
        master_key = args
        if not master_key:
            master_key = '%s:%s' % (func.__module__, func.__name__)
        
        @functools.wraps(func)
        def _func(*args, **kwargs):
            frozen_kwargs = tuple(sorted(kwargs.items()))
            key = (master_key, args, frozen_kwargs)
            return self.get(key, func, args, kwargs, **opts)
        
        return _func
















