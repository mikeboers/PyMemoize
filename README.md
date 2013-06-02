Memoize
=================

[![Test Status](https://secure.travis-ci.org/mikeboers/PyMemoize.png)](http://travis-ci.org/mikeboers/PyMemoize)

This is a (relatively) simple Python memoizing module (ie. a function cache), in which any dict-like can be used as the actual storage object.

Basics
------

Lets walk through a simple example. First we need somewhere to cache values. We will use a simple dictionary for this, but you can use anything with a dict-like interface (see lower for the specification), including persistent storage mechanisms.

    # Make a store.
    store = {}

Now we create the `Memoizer` object itself. Any keyword arguments will be stored as options to the "default" region (more on this later).

	# Initialize the cache object.
    from memoize import Memoizer
	memo = Memoizer(store)

There is a direct API for retrieving a value. We pass it the key we want, and a function that is used to calculate it.

    def basic_func():
        print 'called'
        return 123

	# Manually retrieve a value.
	memo.get('basic', basic_func)
	# stdout > called
	# return > 123

	# If we ask for the same key it will not run the function again.
	memo.get('basic', basic_func)
	# return > 123

You can check for a given key, and manually remove something from the cache if you want:

    memo.exists('basic')
    # return > True

    memo.delete('basic')
    memo.exists('basic')
    # return > False

    memo.get('basic', basic_func)
    # stdout > called
    # return > 123


Function arguments
------------------

You can specify the positional and keyword arguments to call the function with:

    def adder_func(a, b):
        print called
        return a + b

    # Passing args...
    memo.get('adder-1', adder_func, (1, 2))
    # stdout > called
    # return > 3

    memo.get('adder-1', adder_func, (1, 2))
    # return > 3

    # And kwargs...
    memo.get('adder-2', adder_func, (), {'a':3, 'b':4})
    # stdout > called
    # return > 7

Expiring values
---------------

Values need not live forever; we can easily supply maximum ages or expiry times for the data.

    memo.get('expires', basic_func, max_age=1)
    # stdout > called
    # return > 123

    memo.get('expires', basic_func, max_age=1)
    # return > 123

    # Let us wait for this to expire...
    import time
    time.sleep(1.1)

    # The function will get called again!
    memo.get('expires', basic_func, max_age=1)
    # stdout > called
    # return > 123

Alternatively you can pass a `expire` which is the explicit unix time for the data to expire at.

You can see how much time is left until something expires, or set an expiration manually:

    memo.get('expires', basic_func, max_age=60)
    # stdout > called
    # return > 123

    memo.ttl('expires')
    # return > something slightly less than 60

    # Wait a bit and see what happens...
    time.sleep(1)
    memo.ttl('expires')
    # return > something slightly less than 59

    # Manually set the remaining ttl of the data.
    memo.expire('expires', 10)
    memo.ttl('expires')
    # return > something slightly less than 10

    # Set an explicit expiry time.
    memo.expire_at('expires', time.time() + 3600)
    memo.ttl('expires')
    # return > something slightly less than 3600

Etags
-----

If you need to regenerate your content based off an external resource that is not reflected by the arguments of the function when called, then you can use etags.

An etag is any object that represents the current state of the resources that will be drawn upon to generate the final value. If the etag changes then it is assumed that the value is out of date. Note that not providing an etag will not trigger a regeneration.

    store = {}
    memo = Memoizer(store)

    memo.get('etagged', basic_func, etag='a')
    # stdout > called

    # Doesnt call the function again if the etag is the same.
    memo.get('etagged', basic_func, etag='a')

    # Change the etag.
    memo.get('etagged', basic_func, etag='b')
    # stdout > called

You can also supply a function that is called with the same arguments that the function will be called with, and its return value is used as the etag.

    state = []
    def get_etag():
        return len(state)

    memo.get('etagged', basic_func, etagger=get_etag)


Decoration
----------

The `Memoizer` object can be applied as a decorator to a function, which will automatically cache its return values keyed on the function name, and arguments provided. This is only reliable as long as the `repr` of the arguments is deterministic (ie. no dicts which can change order).

The inclusion of arguments into the key is the primary difference between the direct get method, and using the decorator; functions have effectively been memoized!

You can manually specify a key as a positional argument if there will be a name collision by another function with the same name.

***Note:*** Most options we have used previously are perfectly valid to use in the decorator declaration, with an obvious exception of arguments as those are handled by calling the function. Features that we will explain on the decorators (ie. regions, locks, etc) apply equally to the direct get method.

Basic usage:

    @memo
    def cached_func():
        print 'called'
        return 456

    cached_func()
    # stdout > called
    # return > 456

    cached_func()
    # return > 456

Using options:

    # This should be obvious as to what it does...
    @memo(max_age=60)
    def one_minute():
        return 'value'

    one_minute()
    # return > 'value'

Many of the Memoizer methods have been applied to the wrapped function as well!

    one_minute.exists()
    # return > True

    one_minute.ttl()
    # return > slightly less than 60

    one_minute.expire(10)
    one_minute.ttl()
    # return > slightly less than 10

    one_minute.delete()
    one_minute.exists()
    # return > False

Since the cache for the function is keyed by the arguments, you must provide all of the positional and keyword arguments that you are checking against to these methods.

    @memo
    def adder(a, b):
        return a + b

    adder(1, 2)
    # return > 3

    # This will not work as expected!
    adder.exists()
    # return > False

    # But this does...
    adder.exists((1, 2))
    # return > True

Care has been taken to key this keeping in mind how the arguments will be accepted by the function. Ergo you can specify positional arguments by a keyword and it will still use the same key.

    # Note that this results in the same argument values.
    adder.exists((2, ), {'a': 1})
    # return > True


Namespaces
----------

A namespace a simply a string prefix for the final key. The prefixed key is only ever seen by the store itself.

    store = {}
    memo = Memoizer(store, namespace='master')

    memo.get('key', str)
    store.keys()
    # return > ['master:key']

    store.clear()
    memo.get('key2', str, namespace='2')
    store.keys()
    # return > ['2:key2']

    store.clear()
    @memo(namespace='3')
    def func():
        pass
    func()
    store.keys()
    # return > ['3:__main__.func()']


Regions
-------

Regions are sets of default values. A region named "default" is initially created and populated with keyword arguments passed to the constructor.

A region is simply a dictionary within the Memoizer.regions dictionary (mapped by name). It is referenced by name as an kwarg in all methods.

    store = {}
    memo = Memoizer(store)
    memo.regions['short'] = {'max_age': 60}
    memo.regions['long'] = {'max_age': 3600}

    memo.get('key1', str)
    memo.get('key2', str, region='short')
    memo.get('key3', str, region='long')

    memo.ttl('key1')
    # return > None
    memo.ttl('key2')
    # return > ~60
    memo.ttl('key3')
    # return > ~3600

A simple form a region inheritance may exist by a region naming another region as its "parent" (again, by name). Please see the tests for a demonstration.

Alternative stores
------------------

You can specify the store to use on a global, region, or individual bases.

    primary = {}
    secondary = {}
    tertiary = {}
    memo = Memoizer(default)
    memo.regions['secondary'] = {'store': secondary}

    memo.get('key1', str)
    memo.get('key2', str, region='secondary')
    memo.get('key3', str, store=tertiary)

    primary.keys()
    # return > 'key1'
    secondary.keys()
    # return > 'key2'
    tertiary.keys()
    # return > 'key3'


Locking
-------

It is possible that two threads will attempt to generate content at the same time, but that can be a waste of resources. Ergo, you (or the `store`) can provide a locking implementation to attempt to stem this waste.

If the `store` has a `lock` method, that will be used. You can also provide a `lock` function as an option that will override the store's native lock.

You may provide a float `timeout` option as well to override the default.

The lock constructor will be called with the key for which a value is about to be calculated. The function MUST return an object with an `acquire(timeout)` and a `release()` method.

The `acquire` method will be called with a single float representing the maximum amount of time to block waiting for a lock, and the boolean value of the return value MUST indicate if the lock was acquired. Any exceptions thrown will not be caught. The `release` method will be called only if the lock was acquired.


Redis
-----

We have provided a small wrapper and lock implementation for use with Redis.

    from redis import Redis
    db = Redis()

    import memoize.redis
    store = memoize.redis.wrap(db)

    memo = memoize.Memoizer(store)

    # Use!


Store Interface
---------------

There is a relatively minimal interface that a store must offer to be used with this package.

### On keys

Keys are ALWAYS strings.

### On stored values

The valued stored are ALWAYS tuples. The first item is in integer representing the current protocol version (currently 1). For protocol 1 the fields are:

    0: protocol version (always 1, thus far)
    1: creation time
    2: expiry time
    3: etag
    4: value

There are constants in `memoize.core` that hold the index values so you will
not have to hardcode these (ie. `CREATION_INDEX`, and `ETAG_INDEX`).

### Method: `Store.__getitem__(key)`

Return the requested data tuple. MUST raise a KeyError, or return None of the key does not exist.

### Method: `Store.get(key)`

Return the requested data tuple. MUST return None if the key does not exist.

### Method: `Store.__setitem__(key, data_tuple)`

Store the data tuple. This may optionally set an expiry time with the store's native method. If the native method does not support float times, then round up to the next usable time so that the store does not expire a value before we
intend it to.

ie. If using a store that has second resolution, set the expiry time to: `math.ceil(expiry)`.

### Method: `Store.__delitem__(key)`

Delete the data tuple. MAY throw an KeyError.

### Method: `Store.lock(key)` *optional*

Return a lock object as specified by the locking section below.

### Method: `Store.ttl(key)` *optional*

Return the time-to-live of the given key as a float, or None if it does not exist or will not expire. If the native expiry mechanism does not support float times then take care that the returned value is less than the "real" expiry time.

ie. If using a store that has second resolution, return: `native_ttl - 1`.







