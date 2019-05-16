from Jumpscale import j
from .EtcdClient import EtcdClient


JSConfigs = j.application.JSBaseConfigsClass


class EtcdFactory(JSConfigs):

    __jslocation__ = "j.clients.etcd"
    _CHILDCLASS = EtcdClient

    def test(self):
        """

        :return:
        """

        # check is ubuntu 1804
        # build etcd
        # start etcd
        # make client connection to it
