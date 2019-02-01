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
    _storedprocedures_to_sha = {}
    _redis-cli_path = None

    def dict_get(self, key):
        return RedisDict(self, key)

    def queue_get(self, name, namespace="queues", newconnection=False):
        '''get redis queue

        :param name: name of the queue
        :type name: str
        :param namespace: namespace of the queue, defaults to "queues"
        :type namespace: str, optional
        :param newconnection: if True will create a new connection, if False will use an existing connection from the pool, defaults to False
        :type newconnection: bool, optional
        :return: RedisQueue
        :rtype: [type]
        '''
        if not newconnection:
            return RedisQueue(self, name, namespace=namespace)
        else:
            client = redis.Redis(**self.connection_pool.connection_kwargs)
            return RedisQueue(client, name, namespace=namespace)

    def storedprocedure_register(self, name, nrkeys, path):
        '''create stored procedure from path

        :param path: the path where the stored procedure exist
        :type path: str
        :raises Exception: when we can not find the stored procedure on the path

        will return the sha

        to use the stored procedure do

        redisclient.evalsha(sha,3,"a","b","c")  3 is for nr of keys, then the args

        the stored procedure can be found in hset storedprocedures:$name has inside a json with

        is json encoded dict
         - script: ...
         - sha: ...
         - nrkeys: ...

        there is also storedprocedures_sha -> sha without having to decode json

        '''
        lua = j.sal.fs.readFile(path)

        script =  self.register_script(lua)

        sha = script.sha.encode()

        dd = {}
        dd["sha"] = sha
        dd["script"] = lua
        dd["nrkeys"] = nrkeys
        dd["path"] = path

        data =  j.data.serializers.json.dumps(dd)

        self.hset("storedprocedures",name,data)
        self.hset("storedprocedures_sha",name,sha)

        self.__class__._storedprocedures_to_sha = {}

        return dd

    def storedprocedure_delete(self, name):
        self.hdel("storedprocedures",name)
        #TODO: unload script
        j.shell()



    @property
    def _redis_cli_path(self):
        if not self._redis-cli_path:
            cmd="redis-cli_"

    def redis_cmd_execute(self,command,*args):
        rediscmd = 

    def _sp_data(self,name):
        if name not in self.__class__._storedprocedures_to_sha:
            data = self.hget("storedprocedures",name)
            data2 = j.data.serializers.json.loads(data)
            self.__class__._storedprocedures_to_sha[name] = data2
        return self.__class__._storedprocedures_to_sha[name]

    def storedprocedure_execute(self,name,*args):
        """

        :param name:
        :param args:
        :return:
        """

        data = self._sp_data(name)
        return self.evalsha(data["sha"],data["nrkeys"],*args)



    def storedprocedure_debug(self,name,*args):
        data = self._sp_data(name)
        j.shell()

