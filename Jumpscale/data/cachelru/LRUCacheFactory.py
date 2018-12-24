from .LRUCache import LRUCache
from .RWCache import RWCache
from Jumpscale import j
JSBASE = j.application.JSBaseClass


class LRUCacheFactory(j.builder._BaseClass):

    def __init__(self):
        self.__jslocation__ = "j.data.cachelru"
        JSBASE.__init__(self)

    def getRWCache(self, nrItemsReadCache, nrItemsWriteCache=50, maxTimeWriteCache=2000, writermethod=None):
        return RWCache(nrItemsReadCache, nrItemsWriteCache, maxTimeWriteCache, writermethod=writermethod)

    def getRCache(self, nritems):
        """
        Least-Recently-Used (LRU) cache.
        Written by http://evan.prodromou.name/Software/Python/LRUCache

        Instances of this class provide a least-recently-used (LRU) cache. They
        emulate a Python mapping type. You can use an LRU cache more or less like
        a Python dictionary, with the exception that objects you put into the
        cache may be discarded before you take them out.

        Some example usage::

        cache = LRUCache(32) # new cache
        cache['foo'] = get_file_contents('foo') # or whatever

        if 'foo' in cache: # if it's still in cache...
            # use cached version
            contents = cache['foo']
        else:
            # recalculate
            contents = get_file_contents('foo')
            # store in cache for next time
            cache['foo'] = contents

        print cache.size # Maximum size

        print len(cache) # 0 <= len(cache) <= cache.size

        cache.size = 10 # Auto-shrink on size assignment

        for i in range(50): # note: larger than cache size
            cache[i] = i

        if 0 not in cache: print 'Zero was discarded.'

        if 42 in cache:
            del cache[42] # Manual deletion

        for j in cache:   # iterate (in LRU order)
            print j, cache[j] # iterator produces keys, not values
        """
        return LRUCache(nritems)
