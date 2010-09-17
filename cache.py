

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
            del store[key]
        except KeyError:
            pass
    
    def expire_at(self, key, expiry, **opts):
        self._expand_opts(opts)
        store = opts['store']
        pair = store.get(key)
        if pair is not None:
            store[key] = (pair[0], expiry)
        else:
            raise KeyError(key)
    
    def expire(self, key, maxage, **opts):
        self.expire_at(key, time.time() + maxage, **opts)
    
    def ttl(self, key, **opts):
        self._expand_opts(opts)
        store = opts['store']
        pair = store.get(key)
        if pair is None:
            return None
        value, expiry = pair
        if expiry is not None:
            return max(0, expiry - time.time()) or None
    
    def exists(self, key, **opts):
        self._expand_opts(opts)
        store = opts['store']
        return key in store
    
    
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
        
        return CachedFunction(self, func, master_key, opts)


class CachedFunction(object):
    
    def __init__(self, cache, func, master_key, opts):
        self.cache = cache
        self.func = func
        self.master_key = master_key
        self.opts = opts
    
    def __repr__(self):
        return '<%s of %s via %s>' % (self.__class__.__name__, self.func, self.cache)
    
    def get_key(self, args, kwargs):
        frozen_kwargs = tuple(sorted(kwargs.items()))
        return (self.master_key, args, frozen_kwargs)
            
    def __call__(self, *args, **kwargs):
        return self.cache.get(self.get_key(args, kwargs), self.func, args, kwargs, **self.opts)
    
    def delete(self, args=(), kwargs={}):
        self.cache.delete(self.get_key(args, kwargs))
    
    def expire(self, maxage, args=(), kwargs={}):
        self.cache.expire(self.get_key(args, kwargs), maxage)
        
    def expire_at(self, maxage, args=(), kwargs={}):
        self.cache.expire_at(self.get_key(args, kwargs), maxage)
        
    def ttl(self, args=(), kwargs={}):
        return self.cache.ttl(self.get_key(args, kwargs))
        
    def exists(self, args=(), kwargs={}):
        return self.cache.exists(self.get_key(args, kwargs))













