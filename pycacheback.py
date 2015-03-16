"""
An extended dictionary offering limited LRU entries in the dictionary
and an interface to an unlimited backing store.

https://code.google.com/p/rzzzwilson/wiki/pyCacheBack
"""

__license__ = """
Copyright (C) 2012 rzzzwilson@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


class pyCacheBack(dict):
    """Extend the dictionary class to become an LRU dictionary with a limited
    number of dictionary keys, fronting for a unlimited backing store."""

    # maximum number of key/value pairs for pyCacheBack
    maxLRU = 1000

    def __init__(self, *args, **kwargs):
        self._lru_list = []
        self._max_lru = kwargs.pop('max_lru', self.maxLRU)
        super(pyCacheBack, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        if key in self:
            value = super(pyCacheBack, self).__getitem__(key)
        else:
            value = self._get_from_back(key)
        self._reorder_lru(key)
        return value

    def __setitem__(self, key, value):
        super(pyCacheBack, self).__setitem__(key, value)
        self._put_to_back(key, value)
        self._reorder_lru(key)
        self._enforce_lru_size()

    def __delitem__(self, key):
        super(pyCacheBack, self).__delitem__(key)
        self._reorder_lru(key, remove=True)

    def clear(self):
        super(pyCacheBack, self).clear()
        self._lru_list = []

    def pop(self, *args):
        k = args[0]
        try:
            self._lru_list.remove(k)
        except ValueError:
            pass
        return super(pyCacheBack, self).pop(*args)

    def popitem(self):
        kv_return = super(pyCacheBack, self).popitem()
        try:
            self._lru_list.remove(kv_return[0])
        except ValueError:
            pass
        return kv_return

    def _reorder_lru(self, key, remove=False):
        """Move key in LRU (if it exists) to 'recent' end.

        If 'remove' is True just remove from the LRU.
        """

        try:
            self._lru_list.remove(key)
        except ValueError:
            pass
        if remove:
            return
        self._lru_list.insert(0, key)

    def _enforce_lru_size(self):
        """Enforce LRU size limit in cache dictionary."""

        # if a limit was defined and we have blown it
        if self._max_lru and len(self) > self._max_lru:
            # make sure in-memory dictionary doesn't get bigger
            for key in self._lru_list[self._max_lru:]:
                super(pyCacheBack, self).__delitem__(key)
            # also truncate the LRU list
            self._lru_list = self._lru_list[:self._max_lru]

    #####
    # override the following two methods to implement the backing cache
    #####

    def _put_to_back(self, key, value):
        """Store 'value' in backing store, using 'key' to access."""

        pass

    def _get_from_back(self, key):
        """Retrieve value for 'key' from backing storage.

        Raises KeyError if key not in backing storage.
        """

        raise KeyError

