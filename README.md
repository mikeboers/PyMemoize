

This is a (relatively) simple Python memoizing module (ie. a function cache).

Anything dict-like can be used as the actual storage object. We will only ever supply string keys (although they may be unicode), and 2-tuple values (the first element being the actual value that may be of any type, the second being a float of the unix time at which the value expires).


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


Store Interface
---------------

There is a relatively minimal interface that a store must offer to be used with this package.

### On keys

Keys are ALWAYS strings.

### On stored values

The valued stored are ALWAYS 2-tuples: the first item is the actual value to be cached, and the second is either None, or a float of the unix time at which the value will expire.

### Store.__getitem__(key)

Return the requested data tuple. MUST raise a KeyError, or return None of the key does not exist.

### Store.__setitem__(key, data_tuple)

Store the data tuple. This may optionally set an expiry time with the store's native method. If the native method does not support float times, then round up to the next usable time so that the store does not expire a value before we
intend it to.

ie. If using a store that has second resolution, set the expiry time to: `math.ceil(expiry)`.

### Store.__delitem__(key)

Delete the data tuple. MAY throw an KeyError.

### Store.lock(key) *optional*

Return a lock object as specified by the locking section below.

### Store.ttl(key) *optional*

Return the time-to-live of the given key as a float, or None if it does not exist or will not expire. If the native expiry mechanism does not support float times then take care that the returned value is less than the "real" expiry time.

ie. If using a store that has second resolution, return: `native_ttl - 1`.


Locking
-------

It is possible that two threads will attempt to generate content at the same time, but that can be a waste of resources. Ergo, you (or the `store`) can provide a locking implementation to attempt to stem this waste.

If the `store` has a `lock` method, that will be used. You can also provide a `lock` function as an option that will override the store's native lock.

You may provide a float `timeout` option as well to override the default.

The lock constructor will be called with the key for which a value is about to be calculated. The function MUST return an object with an `acquire(timeout)` and a `release()` method.

The `acquire` method will be called with a single float representing the maximum amount of time to block waiting for a lock, and the boolean value of the return value MUST indicate if the lock was acquired. Any exceptions thrown will not be caught. The `release` method will be called only if the lock was acquired.






