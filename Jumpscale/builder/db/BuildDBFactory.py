from Jumpscale import j

from .BuilderEtcd import BuilderEtcd
from .BuilderMariadb import BuilderMariadb


class BuildDBFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.db"

    def _init(self):
        self._logger_enable()
        self.etcd = BuilderEtcd()
        self.mariadb = BuilderMariadb()

