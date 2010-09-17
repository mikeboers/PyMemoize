

This is a very configurable Python memoizing module.

Anything dict-like can be used as the actual storage object. We will only ever
supply string keys (although they may be unicode), and 2-tuple values (the
first element being the actual value, the second being a float of the unix
time at which the value expires).

Any store which has its own expiry mechanism should use the second item to set
the native expiry time. If the native mechanism does not support float expiry
times (ie. only ints like redis) then take care to make sure the native expiry
is after the given one.


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



Locking
-------

It is possible that two threads will attempt to generate content at the same time, but that can be a waste of resources. Ergo, you (or the `store`) can provide a locking implementation to attempt to stem this waste.

If the `store` has a `lock` method, that will be used. You can also provide a `lock` option that will override the store's native lock. You can provide a float `timeout` option as well.

The function is the lock constructor, and it will be called with the key for which a value is about to be calculated. The function MUST return an object with an `acquire(timeout)` and a `release()` method. The `acquire` method will be called with a single float representing the maximum amount of time to block waiting for a lock, and the boolean value of the return value MUST indicate if the lock was acquired. Any exceptions thrown will not be caught. The `release` method will be called if the lock was acquired.






