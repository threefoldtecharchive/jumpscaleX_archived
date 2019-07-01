from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Db_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("db_sandbox_tests_{time}.log")
        logger.debug("Starting of db sandbox testcases.")

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/658")
    def test001_etcd(self):
        """ SAN-006
        *Test etcd builer sandbox*
        """
        logger.debug("run etcd sandbox, should succeed and upload flist on hub.")
        j.builders.db.etcd.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded etcd builder flist.")
        self.deploy_flist_container("etcd")
        logger.debug("Check that etcd flist works by run etcd command, should succeed. ")
        data = self.cont_client.system("/sandbox/bin/etcd -h")
        self.assertIn("--snapshot-count", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/658")
    def test002_zdb(self):
        """ SAN-007
        *Test zdb builer sandbox*
        """
        logger.debug("Run zdb sandbox, should succeed and upload flist on hub.")
        j.builders.db.zdb.sandbox(**self.sandbox_args)

        logger.debug("Deploy container with uploaded zdb builder flist.")
        self.deploy_flist_container("0-db")

        logger.debug("Check that zdb flist works by run zdb binary, should succeed. ")
        data = self.cont_client.system("/bin/sandbx/zdb -h").get()
        self.assertIn("Usage: /sandbox/bin/zdb", data.stdout)

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/658")
    def test003_postgresql(self):
        """ SAN-008
        *Test postgresql builer sandbox*
        """
        logger.debug("run postgresql sandbox, should succeed and upload flist on hub.")
        j.builders.db.postgres.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded postgresql builder flist.")
        self.deploy_flist_container("postgresql")
        logger.debug("Check that postgres flist works by run postgres command, should succeed. ")
        self.assertIn("PostgreSQL server", self.check_container_flist("/sandbox/bin/postgres -h"))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/658")
    def test004_redis(self):
        """ SAN-009
        *Test redis builer sandbox*
        """
        logger.debug("run redis sandbox, should succeed and upload flist on hub.")
        j.builders.db.redis.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded redis builder flist.")
        self.deploy_flist_container("redis")
        logger.debug("Check that redis flist works by run redis command, should succeed. ")
        self.assertIn("Usage: redis-cli", self.check_container_flist("/sandbox/bin/redis-cli -h"))

    def test005_influxdb(self):
        """ SAN-010
        *Test influxdb builer sandbox*
        """
        logger.debug("run influxdb sandbox, should succeed and upload flist on hub.")
        j.builders.db.influxdb.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded influxdb builder flist.")
        self.deploy_flist_container("influxdb")
        logger.debug("Check that influx flist works by run influxd command, should succeed. ")
        self.assertIn("Influx", self.check_container_flist("/sandbox/bin/influx help"))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/658")
    def test006_mongodb(self):
        """ SAN-011
        *Test mongodb builer sandbox*
        """
        logger.debug("run mongodb sandbox, should succeed and upload flist on hub.")
        j.builders.db.ardb.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded mongodb builder flist.")
        self.deploy_flist_container("mongodb")
        logger.debug("Check that mongodb flist works by run mongodb command, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/mongod -h"))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/658")
    def test007_ardb(self):
        """ SAN-012
        *Test ardb builer sandbox*
        """
        logger.debug("run ardb sandbox, should succeed and upload flist on hub.")
        j.builders.db.ardb.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded ardb builder flist.")
        self.deploy_flist_container("ardb")
        logger.debug("Check that ardb flist works by run ardb command, should succeed. ")
        self.assertIn("Usage:", self.check_container_flist("/sandbox/bin/ardb -h"))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/658")
    def test008_mariadb(self):
        """ SAN-018
        *Test mariadb builer sandbox*
        """
        logger.debug("run mariadb sandbox, should succeed and upload flist on hub.")
        j.builders.db.mariadb.sandbox(**self.sandbox_args)
        logger.debug("deploy container with uploaded mariadb builder flist.")
        self.deploy_flist_container("mariadb")
        logger.debug("Check that mariadb flist works by run mariadb command, should succeed. ")
        data = self.cont_client.system("/sandbox/usr/local/mysql -h").get()
        self.assertIn("Usage: /sandbox/bin/zdb", data.stdout)
