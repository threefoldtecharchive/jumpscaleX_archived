# lrucache.py -- a simple LRU (Least-Recently-Used) cache class

# Copyright 2004 Evan Prodromou <evan@bad.dynu.ca>
# Licensed under the Academic Free License 2.1

# arch-tag: LRU cache main module

"""a simple LRU (Least-Recently-Used) cache module

This module provides very simple LRU (Least-Recently-Used) cache
functionality.

An *in-memory cache* is useful for storing the results of an
'expensive' process (one that takes a lot of time or resources) for
later re-use. Typical examples are accessing data from the filesystem,
a database, or a network location. If you know you'll need to re-read
the data again, it can help to keep it in a cache.

You *can* use a Python dictionary as a cache for some purposes.
However, if the results you're caching are large, or you have a lot of
possible results, this can be impractical memory-wise.

An *LRU cache*, on the other hand, only keeps _some_ of the results in
memory, which keeps you from overusing resources. The cache is bounded
by a maximum size; if you try to add more values to the cache, it will
automatically discard the values that you haven't read or written to
in the longest time. In other words, the least-recently-used items are
discarded. [1]_

.. [1]: 'Discarded' here means 'removed from the cache'.

"""


import time
from heapq import heappush, heappop, heapify
from Jumpscale import j

JSBASE = j.application.JSBaseClass

__version__ = "0.2"
__all__ = ["CacheKeyError", "LRUCache", "DEFAULT_SIZE"]
__docformat__ = "reStructuredText en"

DEFAULT_SIZE = 16
"""Default size of a new LRUCache object, if no 'size' argument is given."""


class CacheKeyError(KeyError, JSBASE):
    """Error raised when cache requests fail

    When a cache record is accessed which no longer exists (or never did),
    this error is raised. To avoid it, you may want to check for the existence
    of a cache record before reading or deleting it."""

    def __init__(self):
        JSBASE.__init__(self)


class LRUCache(j.application.JSBaseClass):
    class __Node:
        """Record of a cached value. Not for public consumption."""

        def __init__(self, key, obj, timestamp):
            object.__init__(self)
            self.key = key
            self.obj = obj
            self.atime = timestamp
            self.mtime = self.atime

        def __cmp__(self, other):
            return cmp(self.atime, other.atime)

        def __repr__(self):
            return "<%s %s => %s (%s)>" % (self.__class__, self.key, self.obj, time.asctime(time.localtime(self.atime)))

    def __init__(self, size=DEFAULT_SIZE):
        # Check arguments
        if size <= 0:
            raise j.exceptions.Value(size)
        elif not isinstance(size, type(0)):
            raise j.exceptions.Value(size)
        object.__init__(self)
        JSBASE.__init__(self)
        self.__heap = []
        self.__dict = {}
        self.size = size
        """Maximum size of the cache.
        If more than 'size' elements are added to the cache,
        the least-recently-used ones will be discarded."""

    def __len__(self):
        return len(self.__heap)

    def __contains__(self, key):
        return key in self.__dict

    def __setitem__(self, key, obj):
        if key in self.__dict:
            node = self.__dict[key]
            node.obj = obj
            node.atime = time.time()
            node.mtime = node.atime
            heapify(self.__heap)
        else:
            # size may have been reset, so we loop
            while len(self.__heap) >= self.size:
                lru = heappop(self.__heap)
                del self.__dict[lru.key]
            node = self.__Node(key, obj, time.time())
            self.__dict[key] = node
            heappush(self.__heap, node)

    def __getitem__(self, key):
        if key not in self.__dict:
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            node.atime = time.time()
            heapify(self.__heap)
            return node.obj

    def __delitem__(self, key):
        if key not in self.__dict:
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            del self.__dict[key]
            self.__heap.remove(node)
            heapify(self.__heap)
            return node.obj

    def __iter__(self):
        copy = self.__heap[:]
        while len(copy) > 0:
            node = heappop(copy)
            yield node.key
        raise StopIteration

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        # automagically shrink heap on resize
        if name == "size":
            while len(self.__heap) > value:
                lru = heappop(self.__heap)
                del self.__dict[lru.key]

    def __repr__(self):
        return "<%s (%d elements)>" % (str(self.__class__), len(self.__heap))

    def mtime(self, key):
        """Return the last modification time for the cache record with key.
        May be useful for cache instances where the stored values can get
        'stale', such as caching file or network resource contents."""
        if key not in self.__dict:
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            return node.mtime


if __name__ == "__main__":
    cache = LRUCache(25)
    print(cache)
    for i in range(50):
        cache[i] = str(i)
    print(cache)
    if 46 in cache:
        del cache[46]
    print(cache)
    cache.size = 10
    print(cache)
    cache[46] = "46"
    print(cache)
    print((len(cache)))
    for c in cache:
        print(c)
    print(cache)
    print((cache.mtime(46)))
    for c in cache:
        print(c)
