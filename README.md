

This is a Python persistent memoizing module.

Anything dict-like can be used as the actual storage object as long as it
supports standard key types (ie, strings, ints, tuples of these).

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