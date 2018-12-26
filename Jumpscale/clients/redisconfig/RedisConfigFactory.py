from Jumpscale import j

from .RedisConfig import RedisConfig


JSConfigBase = j.application.JSFactoryBaseClass


class RedisConfigFactory(JSConfigBase):
    __jslocation__ = "j.clients.redis_config"
    _CHILDCLASS = RedisConfig

    def _init(self):
        self._tree = None

    def configure(self, instance="core", ipaddr="localhost",
                  port=6379, password="", unixsocket="",
                  ardb_patch=False, set_patch=False,
                  ssl=False, ssl_keyfile=None, ssl_certfile=None):

        self.addr = ipaddr
        self.port = port
        self.password_ = password
        self.unixsocket = unixsocket
        self.ardb_patch = ardb_patch
        self.set_patch = set_patch
        self.ssl = ssl
        if ssl_keyfile and ssl_certfile:
            # check if its a path, if yes load
            self.ssl = True
            # means path will be used for sslkey at redis client
            self.sslkey = True

        r = self.get(name=instance)

        if ssl_keyfile and ssl_certfile:
            # check if its a path, if yes safe the key paths into config
            r.ssl_keys_save(ssl_keyfile, ssl_certfile)

        return r

    def test(self):
        j.clients.redis.core_get()
        cl = self.configure(instance="test", port=6379)
        assert cl.redis.ping()
