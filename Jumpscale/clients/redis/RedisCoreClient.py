from Jumpscale import j

# import gevent


class RedisCoreClient(j.application.JSBaseClass):

    __jslocation__ = "j.clients.credis_core"

    def _init(self):

        self._client_fallback = j.clients.redis.core_get()

        try:
            self._credis = True
            from credis import Connection

            self._client = Connection(path="/sandbox/var/redis.sock")
            self._client.connect()
        except Exception as e:
            self._credis = False
            self._client = j.clients.redis.core_get()

        if self._credis:
            assert self.execute("PING") == b"PONG"
        else:
            assert self.execute("PING")

    def execute(self, *args):
        if self._credis:
            return self._client.execute(*args)
        else:
            return self._client.execute_command(*args)

    def get(self, *args):
        return self.execute("GET", *args)

    def set(self, *args):
        return self.execute("SET", *args)

    def hset(self, *args):
        return self.execute("HSET", *args)

    def hget(self, *args):
        return self.execute("HGET", *args)

    def hdel(self, *args):
        return self.execute("HDEL", *args)

    def keys(self, *args):
        return self.execute("KEYS", *args)

    def hkeys(self, *args):
        return self.execute("HKEYS", *args)

    def delete(self, *args):
        return self.execute("DEL", *args)

    def incr(self, *args):
        return self.execute("INCR", *args)
