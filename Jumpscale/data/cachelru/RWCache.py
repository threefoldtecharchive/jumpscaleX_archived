import time
from heapq import heappush, heappop, heapify

from Jumpscale import j
from .LRUCache import LRUCache

from operator import itemgetter, attrgetter

JSBASE = j.application.JSBaseClass


class RWCache(j.application.JSBaseClass):
    def __init__(self, nrItemsReadCache, maxNrItemsWriteCache=50, maxTimeWriteCache=2000, writermethod=None):
        self.cacheR = j.tools.cachelru.getRCache(nrItemsReadCache)
        self.cacheW = WCache(maxNrItemsWriteCache, writermethod, maxTimeWriteCache)
        JSBASE.__init__(self)

    def set(self, key, obj):
        self.cacheW[key] = obj
        self.cacheR[key] = obj

    def flush(self):
        self.cacheW.flush()


# based on LRUCache but modified for different purpose (write through cache)
class WCache:
    class __Node:
        """Record of a cached value. Not for public consumption."""

        def __init__(self, key, obj, timestamp):
            object.__init__(self)
            self.key = key
            self.obj = obj
            self.wtime = timestamp

        def __cmp__(self, other):
            return cmp(self.atime, other.atime)

        def __repr__(self):
            return "<%s %s => %s (%s)>" % (self.__class__, self.key, self.obj, time.asctime(time.localtime(self.wtime)))

    def __init__(self, size=5000, writermethod=None, maxtime=1):
        """
        @param writermethod if given then this method will be called with max size reached or when flush called for objects older than specified maxtime
        """
        # Check arguments
        if size <= 0:
            raise j.exceptions.Value(size)
        elif not isinstance(size, type(0)):
            raise j.exceptions.Value(size)
        object.__init__(self)
        JSBASE.__init__(self)
        self.__dict = {}
        self.size = size
        self.flushsize = round(float(size) * 1.2)
        self.maxtime = maxtime
        self.writermethod = writermethod

    def flush(self):
        if len(list(self.__dict.keys())) >= self.size and self.writermethod is None:
            raise j.exceptions.RuntimeError("Write cache full.")

        now = time.time()

        todelete = []
        for key in self:
            item = self.__dict[key]
            if now > item.wtime + self.maxtime:
                self.writermethod(self.__dict[key])
                todelete.append(key)

        for key2 in todelete:
            del self.__dict[key2]

        if len(list(self.__dict.keys())) < self.size:
            return
        # not enough objects flushed, sort follow latest mdate
        tosort = []
        for key in list(self.__dict.keys()):
            tosort.append([key, self.__dict[key].wtime])
        sortedItems = sorted(tosort, key=itemgetter(1))
        counter = 0
        while len(list(self.__dict.keys())) >= self.size:
            key = sortedItems[counter][0]
            counter += 1
            self.writermethod(self.__dict[key])
            del self.__dict[key]

    def __setitem__(self, key, obj):
        if key in self.__dict:
            node = self.__dict[key]
            node.obj = obj
            node.mtime = node.atime
        else:
            # size may have been reset, so we loop
            node = self.__Node(key, obj, time.time())
            self.__dict[key] = node
            if len(list(self.__dict.keys())) >= self.flushsize:
                self.flush()

    def __len__(self):
        return len(self.__heap)

    def __contains__(self, key):
        return key in self.__dict

    def __getitem__(self, key):
        if key not in self.__dict:
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            return node.obj

    def __delitem__(self, key):
        if key not in self.__dict:
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            del self.__dict[key]
            return node.obj

    def __iter__(self):
        for key in list(self.__dict.keys()):
            yield key

    # def __iter__(self):
    #     tosort=[]
    #     for key in self.__dict.keys():
    #         tosort.append([key,self[key].atime])
    #     for item in sorted(data,key=itemgetter(1)):
    #         yield key

    # def __setattr__(self, name, value):
    #     object.__setattr__(self, name, value)
    #     # automagically shrink heap on resize
    #     if name == 'size':
    #         while len(self.__heap) > value:
    #             lru = heappop(self.__heap)
    #             del self.__dict[lru.key]

    def __repr__(self):
        return "<%s (%d elements)>" % (str(self.__class__), len(list(self.__dict.keys())))

    def mtime(self, key):
        """Return the last modification time for the cache record with key.
        May be useful for cache instances where the stored values can get
        'stale', such as caching file or network resource contents."""
        if key not in self.__dict:
            raise CacheKeyError(key)
        else:
            node = self.__dict[key]
            return node.wtime
