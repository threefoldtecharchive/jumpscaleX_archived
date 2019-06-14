from Jumpscale import j

from .RDBClient import RDBClient

#
JSBASE = j.application.JSBaseClass


class RDBFactory(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.clients.rdb"
        JSBASE.__init__(self)

    def client_get(self, nsname="test", redisconfig_name="core", **kwargs):
        """
        :param nsname: namespace name
        :param redisconfig_name: name of the redis config client see j.clients.redis_config
        :return:
        """
        cl = j.clients.redis_config.get_client(redisconfig_name)
        cl.redisconfig_name = redisconfig_name
        return RDBClient(nsname=nsname, redisclient=cl)

    def test(self):
        """
        kosmos 'j.clients.rdb.test()'

        """

        self._test_run(name="base")
