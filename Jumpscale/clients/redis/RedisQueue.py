from Jumpscale import j
JSBASE = j.application.JSBaseClass


class RedisQueue(JSBASE):
    """Simple Queue with Redis Backend"""

    def __init__(self, redis, name, namespace='queue'):
        """The default connection parameters are: host='localhost', port=9999, db=0"""
        JSBASE.__init__(self)
        self.__db = redis
        self.key = '%s:%s' % (namespace, name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    @property
    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def reset(self):
        """
        make empty
        :return:
        """
        while self.empty == False:
            self.get_nowait()

    def put(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    def get(self, timeout=20):
        """Remove and return an item from the queue."""
        if timeout > 0:
            item = self.__db.blpop(self.key, timeout=timeout)
            if item:
                item = item[1]
        else:
            item = self.__db.lpop(self.key)
        return item

    def fetch(self, block=True, timeout=None):
        """ Like get but without remove"""
        if block:
            item = self.__db.brpoplpush(self.key, self.key, timeout)
        else:
            item = self.__db.lindex(self.key, 0)
        return item

    def set_expire(self, time):
        self.__db.expire(self.key, time)

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)
