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

If you don't extend the `pyCacheBack` class any objects created from the class
will behave like a dictionary with an LRU size-limiting mechanism.  If you
want to use the on-disk backing store feature you must extend the `pyCacheBack`
class.

####An in-memory `pyCacheBack`

To use just the in-memory cache part of `pyCacheBack`, do this:
``` python
import pycacheback
my_cache = pycacheback.pyCacheBack()

my_cache['key'] = 'value'
my_value = my_cache['key']
# etc
```

Note that no backing store is used in the above example, it's just an in-memory
cache with an LRU mechanism to limit memory usage.

The dictionary can contain a maximum number of items.  This limit is rather
arbitrarily set at 1000 by default.  You can change the maximum number of items
when you create a `pyCacheBack` instance:
``` python
import pycacheback
my_cache = pycacheback.pyCacheBack(max_lru=100000)
```

If you put more than the limit of items into a `pyCacheBack` instance the
number of items will be maintained at no more than the `max_lru` limit
by deleting older items.

####Using `pyCacheBack` with an on-disk persistent cache

If you want the persistent on-disk cache, you must create your own class
inheriting from `pyCacheBack` and override the `_put_to_back()` and
`_get_from_back()` methods.  In this example we assume the key has the form
_(x, y)_ and we store the value in a file _x/y_ under a known directory.
The overridden methods must create the backing file from the _key_ and _value_
objects and return the _value_ given the _key_:

``` python
from pycacheback import pyCacheBack

# override the backing functions in pyCacheBack
class my_cache(pyCacheBack):
    def _put_to_back(self, key, value):
       # note that self._tiles_dir is the saved directory from the constructor
       # key (x, y) saves as file <dir>/x/y
        (x, y) = key
        dir_path = os.path.join(_tiles_dir, str(x))
        try:
            os.mkdir(dir_path)
        except OSError:
            pass
        file_path = os.path.join(dir_path, str(y))
        with open(file_path, 'wb') as f:
            f.write(str(value))

    def _get_from_back(self, key):
        (x, y) = key
        file_path = os.path.join(_tiles_dir, str(x), str(y))
        try:
            with open(file_path, 'rb') as f:
                value = f.read()
        except IOError:
            raise KeyError, str(key)
        return value
```

Now when we create an instance of the `my_cache` class we specify the tile
directory we want to use, along with an optional LRU maximum limit:
```python
    backing_cache = my_cache(tile_dir='./tiles', max_lru=100)
```

Note that the in-memory representation of the thing we are caching may not be
writable to disk in the in-memory form.  If any translation of an object is
required before writing to disk the `_put_to_back()` method must do this.
Similarly, the `_get_from_back()` method must reconstruct the in-memory
representation from the on-disk data.  The example above is crude and probably
isn't what you need.

In a real zoomable tiled map display we would actually have a key that also
contains the zoom level.  We leave this out in the code above so the example
is simple.

###Notes

Since things like OpenStreetMap tiles are crowd-edited we should have some
method of *aging* tiles so we pick up OSM tiles that might have changed.
This could be an external batch process which might just delete older tiles
in the on-disk cache, or it could check for changes in the OSM tile repository
and update or delete only out of date local tiles.
Alternatively, we could modify the code that retrieves tiles from the on-disk
cache to check the saved tile date and retrieve the 'net tile again if the tile
is older than a set date.  The existing on-disk tile would be returned as the
found tile.  If the tile retrieved from the 'net is different from the on-disk
copy we could use the 'callback' mechanism to update the user-visible display.

Similarly, if we want an on-disk LRU mechanism to control disk usage we
could have a periodic batch job checking disk usage which deletes older on-disk
tiles.
