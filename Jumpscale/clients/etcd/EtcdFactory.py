from Jumpscale import j
from .EtcdClient import EtcdClient


JSConfigs = j.application.JSBaseConfigsClass


class EtcdFactory(JSConfigs):

    __jslocation__ = "j.clients.etcd"
    _CHILDCLASS = EtcdClient
