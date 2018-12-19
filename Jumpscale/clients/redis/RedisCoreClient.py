
from Jumpscale import j
# import gevent


class RedisCoreClient(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients.credis_core"

    def __init__(self):

        j.application.JSFactoryBaseClass.__init__(self)

        self._client_fallback =  j.clients.redis.core_get()

        try:
            from credis import Connection
            self._client =  Connection(path="/sandbox/var/redis.sock")
            self._client.connect()
        except Exception as e:
            self._client = j.clients.redis.core_get()
        j.shell()
        assert self._client.execute(b"PING")==b'PONG'

    def execute(self,*args):
        try:
            print(args)
            return self._client.execute(*args)
        except Exception as e:
            raise RuntimeError("Could not execute redis execute:\nargs:%s\nerror:%s"%(args,e))

    def get(self,*args):
        return self.execute("GET",*args)

    def set(self,*args):
        return self.execute("SET",*args)

    def hset(self,*args):
        return self.execute("HSET",*args)

    def hget(self,*args):
        return self.execute("HGET",*args)

    def hdel(self,*args):
        return self.execute("HDEL",*args)

    def keys(self,*args):
        return self.execute("KEYS",*args)

    def hkeys(self,*args):
        return self.execute("HKEYS",*args)


    def delete(self,*args):
        return self.execute("DEL",*args)

    def incr(self,*args):
        return self.execute("INCR",*args)
