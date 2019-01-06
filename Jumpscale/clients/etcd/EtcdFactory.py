from Jumpscale import j
from .EtcdClient import EtcdClient


JSConfigFactory = j.application.JSFactoryBaseClass


class EtcdFactory(JSConfigFactory):

    __jslocation__ = "j.clients.etcd"
    _CHILDCLASS = EtcdClient
