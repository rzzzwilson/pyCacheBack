##pyCacheBack
A python in-memory cache with on-disk backing store.

In the pySlip application we have a python application that displays a map
using `OpenStreetMap` tiles.  The way to get some speed in this sort of
application is to keep an in-memory cache of tiles.  We also implement an
LRU mechanism to keep memory usage under control.

This has a problem when we restart the application as we have to refetch
the tiles that were in the in-memory cache that has gone away.  The smart
approach is to have a in-memory cache in front of an on-disk cache.  The
in-memory cache has an LRU mechanism but the on-disk cache is infinite.

###Using `pyCacheBack`

To use just the in-memory cache part of `pyCacheBack`, do this:
```
    import pycacheback
    my_cache = pycacheback.pyCacheBack()

    my_cache['key'] = 'value'
    my_value = my_cache['key']
    # etc
```

Note that no backing store is used in the above example, it's just an in-memory cache.

###Using `pyCacheBack` with an on-disk persistent cache

If you want the persistent on-disk cache, you must create your own class
inheriting from `pyCacheBack` and override the `_put_to_back()` and
`_get_from_back()` methods.  In this example we assume the key has the form
_(x, y)_ and we store the value in a file _x/y_ under a known directory.
The overridden methods must create the backing file from the _key_ and _value_
objects and return the _value_ given the _key_:

``` python
    from pycacheback import pyCacheBack

    test_dir = './test_dir'

    # override the backing functions in pyCacheBack
    class my_cache(pyCacheBack):
        def _put_to_back(self, key, value):
	    # key (x, y) saves as file <dir>/x/y
	    (x, y) = key
	    dir_path = os.path.join(test_dir, str(x))
	    try:
	        os.mkdir(dir_path)
	    except OSError:
	        pass
	    file_path = os.path.join(dir_path, str(y))
	    with open(file_path, 'wb') as f:
	        f.write(str(value))

        def _get_from_back(self, key):
	    (x, y) = key
	    file_path = os.path.join(test_dir, str(x), str(y))
	    try:
	        with open(file_path, 'rb') as f:
		    value = f.read()
            except IOError:
                raise KeyError, str(key)
            return value
```

Note that if any translation of an object is required before writing to disk is
required the `_put_to_back()` method must do this.
Similarly, the `_get_from_back()` method must reconstruct the in-memory
representation.

In a real zoomable tiled map display we would actually have a key that also
contains the zoom level.  We leave this out in the code above so the example
is simple.

###Notes

When this is used to cache things like OSM map tiles we should have some method
of *aging* tiles so we pick up tiles that might change.  This could be an
external batch process which might just delete older tiles in the on-disk cache,
or it could check for changes in the OSM tile repository and update or delete
only out of date local tiles.
