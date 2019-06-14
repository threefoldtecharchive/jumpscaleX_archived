from Jumpscale import j
import redis

JSBASE = j.application.JSBaseClass


class RDBClient(j.application.JSBaseClass):
    def __init__(self, nsname, redisclient):
        """
        is connection to RDB
        """
        JSBASE.__init__(self)
        self._redis = redisclient
        self.type = "RDB"
        self.nsname = nsname.lower().strip()
        self._logger_enable()
        self._hsetkey = "rdb:%s" % self.nsname
        assert self.ping()

    def _key_encode(self, key):
        return key

    def _key_decode(self, key):
        return key

    def set(self, data, key=None):
        if not key:
            # need to increment
            j.shell()
            key = ""
        return self._redis.execute_command("HSET", self._hsetkey, key, data)

    def get(self, key):
        if not key or not isinstance(key, int):
            raise ValueError("key must be provided, and must be an int")
        return self._redis.execute_command("HGET", self._hsetkey, key)

    def exists(self, key):
        if not key or not isinstance(key, int):
            raise ValueError("key must be provided, and must be an int")
        return self._redis.execute_command("HEXISTS", self._hsetkey, key) == 1

    def delete(self, key):
        if not key or not isinstance(key, int):
            raise ValueError("key must be provided, and must be an int")
        self._redis.execute_command("HDEL", self._hsetkey, key)

    def _flush(self):
        j.shell()

    def flush(self, meta=None):
        """
        will remove all data from the database DANGEROUS !!!!
        :return:
        """
        if meta:
            data = meta._data
            self._flush()
            # recreate the metadata table
            meta.reset()
            # copy the old data back
            meta._data = data
            # now make sure its back in the db
            meta._save()
        else:
            self._flush()

    @property
    def nsinfo(self):
        return {}

    def list(self, key_start=None, reverse=False):
        """
        list all the keys in the namespace

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                        if False, walk from older to newer keys
                        if True walk from newer to older keys
                        defaults to False
        :param reverse: bool, optional
        :return: list of keys
        :rtype: [str]
        """
        result = []
        for key, data in self.iterate(key_start=key_start, reverse=reverse, keyonly=True):
            result.append(key)
        return result

    def iterate(self, key_start=None, reverse=False, keyonly=False):
        """
        walk over all the namespace and yield (key,data) for each entries in a namespace

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                if False, walk from older to newer keys
                if True walk from newer to older keys
                defaults to False
        :param reverse: bool, optional
        :param keyonly: [description], defaults to False
        :param keyonly: bool, optional
        :raises e: [description]
        """

        next = None
        data = None

        if key_start is not None:
            next = self._redis.execute_command("KEYCUR", self._key_encode(key_start))
            if not keyonly:
                data = self.get(key_start)
            yield (key_start, data)

        CMD = "SCANX" if not reverse else "RSCAN"

        while True:
            try:
                if not next:
                    response = self._redis.execute_command(CMD)
                else:
                    response = self._redis.execute_command(CMD, next)
                # format of the response
                # see https://github.com/threefoldtech/0-db/tree/development#scan
            except redis.ResponseError as e:
                if e.args[0] == "No more data":
                    return
                raise e

            (next, results) = response
            for item in results:
                keyb, size, epoch = item
                key_new = self._key_decode(keyb)
                data = None
                if not keyonly:
                    data = self._redis.execute_command("GET", keyb)
                yield (key_new, data)

    @property
    def count(self):
        """
        :return: return the number of entries in the namespace
        :rtype: int
        """
        j.shell()
        return self.nsinfo["entries"]

    def ping(self):
        """
        :return:
        """
        return self._redis.ping()
