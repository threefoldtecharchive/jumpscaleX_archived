import redis
import os
import json
from .RedisQueue import RedisQueue
from Jumpscale import j


# NOTE: We don't use J here because this file
# is imported during the bootstrap process where J is not available

class RedisDict(dict):

    def __init__(self, client, key):
        self._key = key
        self._client = client

    def __getitem__(self, key):
        value = self._client.hget(self._key, key)
        return json.loads(value)

    def __setitem__(self, key, value):
        value = json.dumps(value)
        self._client.hset(self._key, key, value)

    def __contains__(self, key):
        return self._client.hexists(self._key, key)

    def __repr__(self):
        return repr(self._client.hgetall(self._key))

    def copy(self):
        result = dict()
        allkeys = self._client.hgetalldict(self._key)
        for key, value in list(allkeys.items()):
            result[key] = json.loads(value)
        return result

    def pop(self, key):
        value = self._client.hget(self._key, key)
        self._client.hdel(self._key, key)
        return json.loads(value)

    def keys(self):
        return self._client.hkeys(self._key)

    def iteritems(self):
        allkeys = self._client.hgetalldict(self._key)
        for key, value in list(allkeys.items()):
            yield key, json.loads(value)


class Redis(redis.Redis):
    hgetalldict = redis.Redis.hgetall
    dbtype = 'RDB'

    def getDict(self, key):
        return RedisDict(self, key)

    def getQueue(self, name, namespace="queues", newconnection=False):
        """
        get redis queue

        :param name: name of the queue
        :param namespace: namespace of the queue
        :param newconnection: if True will create a new connection, if False will use an existing connection from the pool
        """
        if not newconnection:
            return RedisQueue(self, name, namespace=namespace)
        else:
            client = redis.Redis(**self.connection_pool.connection_kwargs)
            return RedisQueue(client, name, namespace=namespace)

    def createStoredProcedure(self, path):
        """
        create stored procedure from path

        :param path: the path where the stored procedure exist

        :raises Exception when we can not find the stored procedure on the path
        """
        if not os.path.exists(path):
            path0 = os.path.join(os.getcwd(), path)
        if not os.path.exists(path0, followlinks=True):
            raise Exception("cannot find stored procedure on path:%s" % path)
        lua = ''
        with open(path) as f:
            lua = f.read()

        return self.register_script(lua)
