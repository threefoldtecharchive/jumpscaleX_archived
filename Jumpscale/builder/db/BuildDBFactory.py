from Jumpscale import j


class BuildDBFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.db"

    def _init(self):
        self._etcd = None
        self._mariadb = None
        self._ardb = None
        self._cockroachdb = None
        self._redis = None
        self._tidb = None
        self._postgres = None
        self._zdb = None
        self._influxdb = None

    @property
    def etcd(self):
        if self._etcd is None:
            from .BuilderEtcd import BuilderEtcd

            self._etcd = BuilderEtcd()
        return self._etcd

    @property
    def mariadb(self):
        if self._mariadb is None:
            from .BuilderMariadb import BuilderMariadb

            self._mariadb = BuilderMariadb()
        return self._mariadb

    @property
    def zdb(self):
        if self._zdb is None:
            from .BuilderZdb import BuilderZdb

            self._zdb = BuilderZdb()
        return self._zdb

    @property
    def redis(self):
        if self._redis is None:
            from .BuilderRedis import BuilderRedis

            self._redis = BuilderRedis()
        return self._redis

    @property
    def cockroachdb(self):
        if self._cockroachdb is None:
            from .BuilderCockroachDB import BuilderCockroachDB

            self._cockroachdb = BuilderCockroachDB()
        return self._cockroachdb

    @property
    def tidb(self):
        if self._tidb is None:
            from .BuilderTIDB import BuilderTIDB

            self._tidb = BuilderTIDB()
        return self._tidb

    @property
    def postgres(self):
        if self._postgres is None:
            from .BuilderPostgresql import BuilderPostgresql

            self._postgres = BuilderPostgresql()
        return self._postgres

    @property
    def ardb(self):
        if self._ardb is None:
            from .BuilderARDB import BuilderARDB

            self._ardb = BuilderARDB()
        return self._ardb

    @property
    def influxdb(self):
        if self._influxdb is None:
            from .BuilderInfluxdb import BuilderInfluxdb

            self._influxdb = BuilderInfluxdb()
        return self._influxdb
