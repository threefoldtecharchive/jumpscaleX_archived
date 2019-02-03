
import redis
import os
import json
from .RedisQueue import RedisQueue
# from Jumpscale import j

import json

# NOTE: We don't use J here because this file
# is imported during the bootstrap process where J is not available

class Redis(redis.Redis):
    hgetalldict = redis.Redis.hgetall
    dbtype = 'RDB'
    _storedprocedures_to_sha = {}
    _redis_cli_path_ = None

    def __init__(self,*args,**kwargs):
        redis.Redis.__init__(self,*args,**kwargs)
        self._storedprocedures_to_sha = {}

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

    def storedprocedure_register(self, name, nrkeys, path_or_content):
        '''create stored procedure from path

        :param path: the path where the stored procedure exist
        :type path_or_content: str which is the lua content or the path
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

        tips on lua in redis:
        https://redis.io/commands/eval

        '''



        if "\n" not in path_or_content:
            f = open(path_or_content, "r")
            lua = f.read()
            path = path_or_content
        else:
            lua = path_or_content
            path = ""

        script =  self.register_script(lua)

        dd = {}
        dd["sha"] = script.sha
        dd["script"] = lua
        dd["nrkeys"] = nrkeys
        dd["path"] = path

        data = json.dumps(dd)

        self.hset("storedprocedures",name,data)
        self.hset("storedprocedures_sha",name,script.sha)

        self._storedprocedures_to_sha = {}

        # sha = self._sp_data(name)["sha"]
        # assert self.script_exists(sha)[0]

        return script

    def storedprocedure_delete(self, name):
        self.hdel("storedprocedures",name)
        self.hdel("storedprocedures_sha",name)
        self._storedprocedures_to_sha = {}


    @property
    def _redis_cli_path(self):
        if not self.__class__._redis_cli_path_:
            from Jumpscale import j
            if j.core.tools.cmd_installed("redis-cli_"):
                self.__class__._redis_cli_path_ =  "redis-cli_"
            else:
                self.__class__._redis_cli_path_ =  "redis-cli"
        return self.__class__._redis_cli_path_

    def redis_cmd_execute(self,command,debug=False,debugsync=False,keys=[],args=[]):
        """

        :param command:
        :param args:
        :return:
        """
        from Jumpscale import j
        rediscmd = self._redis_cli_path
        if debug:
            rediscmd+= " --ldb"
        elif debugsync:
            rediscmd+= " --ldb-sync-mode"
        rediscmd+= " --%s"%command
        for key in keys:
            rediscmd+= " %s"%key
        if len(args)>0:
            rediscmd+= " , "
            for arg in args:
                rediscmd+= " %s"%arg
        print(rediscmd)

        rc,out,err = j.sal.process.execute(rediscmd,interactive=True)
        return out


    def _sp_data(self,name):
        if name not in self._storedprocedures_to_sha:
            data = self.hget("storedprocedures",name)
            data2 = json.loads(data)
            self._storedprocedures_to_sha[name] = data2
        return self._storedprocedures_to_sha[name]

    def storedprocedure_execute(self,name,*args):
        """

        :param name:
        :param args:
        :return:
        """

        data = self._sp_data(name)
        sha = data["sha"]#.encode()
        assert isinstance(sha, (str))
        # assert isinstance(sha, (bytes, bytearray))
        from Jumpscale import j
        j.shell()
        return self.evalsha(sha,data["nrkeys"],*args)
        # self.eval(data["script"],data["nrkeys"],*args)
        # return self.execute_command("EVALSHA",sha,data["nrkeys"],*args)

    def storedprocedure_debug(self,name,*args):
        """
        to see how to use the debugger see https://redis.io/topics/ldb

        to break put: redis.breakpoint() inside your lua code
        to continue: do 'c'


        :param name: name of the sp to execute
        :param args: args to it
        :return:
        """
        data = self._sp_data(name)
        path = data["path"]
        if path =="":
            from pudb import set_trace; set_trace()

        nrkeys = data['nrkeys']
        args2 = args[nrkeys:]
        keys = args[:nrkeys]

        out = self.redis_cmd_execute("eval %s"%path,debug=True,keys=keys,args=args)

        return out

