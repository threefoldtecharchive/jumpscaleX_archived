from Jumpscale import j

from .RedisConfig import RedisConfig


JSConfigBase = j.application.JSFactoryBaseClass


class RedisConfigFactory(JSConfigBase):
    __jslocation__ = "j.clients.redis_config"
    _CHILDCLASS = RedisConfig

    def _init(self):
        self._tree = None

    def get(self, name=None, id=None, die=True, create_new=True, childclass_name=None, ssl_keyfile=None, ssl_certfile=None, **kwargs):
        '''Create a new redis config client

        :param id: id of the obj to find, is a unique id
        :param name: of the object, can be empty when searching based on id or the search criteria (kwargs)
        :param search criteria (if name not used) or data elements for the new one being created
        :param die, means will give error when object not found
        :param create_new, if True it will automatically create a new one
        :param childclass_name, if different typen of childclass, specify its name, needs to be implemented in _childclass_selector

        :param ssl_keyfile: [description], defaults to None
        :type ssl_keyfile: [type], optional
        :param ssl_certfile: [description], defaults to None
        :type ssl_certfile: [type], optional
        :return: client
        '''
        if ssl_keyfile and ssl_certfile:
            # check if its a path, if yes load
            kwargs['ssl'] = True
            # means path will be used for sslkey at redis client
            kwargs['sslkey'] = True

        r = JSConfigBase.get(self, name=name, id=id, die=die, create_new=create_new, childclass_name=childclass_name, **kwargs)

        if ssl_keyfile and ssl_certfile:
            # check if its a path, if yes safe the key paths into config
            r.ssl_keys_save(ssl_keyfile, ssl_certfile)

        return r

    def test(self):
        j.clients.redis.core_get()
        cl = self.get(name="test_config", port=6379)
        assert cl.redis.ping()
