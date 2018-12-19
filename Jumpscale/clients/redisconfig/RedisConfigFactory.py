from Jumpscale import j

from .RedisConfig import RedisConfig


JSConfigBase = j.application.JSFactoryBaseClass


class RedisConfigFactory(JSConfigBase):

    def __init__(self):
        if not hasattr(self, '__jslocation__'):
            self.__jslocation__ = "j.clients.redis_config"
        JSConfigBase.__init__(self, RedisConfig)
        self._tree = None

    def configure(self, instance="core", ipaddr="localhost",
                  port=6379, password="", unixsocket="",
                  ardb_patch=False, set_patch=False,
                  ssl=False, ssl_keyfile=None, ssl_certfile=None):

        data = {}
        data["addr"] = ipaddr
        data["port"] = port
        data["password_"] = password
        data["unixsocket"] = unixsocket
        data["ardb_patch"] = ardb_patch
        data["set_patch"] = set_patch
        data["ssl"] = ssl
        if ssl_keyfile and ssl_certfile:
            # check if its a path, if yes load
            data["ssl"] = True
            # means path will be used for sslkey at redis client
            data["sslkey"] = True

        r = self.get(instance=instance, data=data)

        if ssl_keyfile and ssl_certfile:
            # check if its a path, if yes safe the key paths into config
            r.ssl_keys_save(ssl_keyfile, ssl_certfile)

        return r

    def test(self):
        j.clients.redis.core_get()
        cl = self.configure(instance="test", port=6379)
        assert cl.redis.ping()
