from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest, time
from parameterized import parameterized


class DB_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("db_tests_{time}.log")
        logger.debug("Starting of db testcases.")

    @parameterized.expand(
        [
            ("zdb", "zdb"),
            ("etcd", "etcd"),
            ("redis", "redis-server"),
            ("ardb", "ardb"),
            ("postgres", "postgres"),
            ("influxdb", "influx"),
            ("mongodb", "mongod"),
            ("mariadb", "mysql"),
        ]
    )
    def test_db_builders(self, builder, process):
        """ BLD-001
        *Test db builers sandbox*
        """
        skipped_builders = {"mariadb": "https://github.com/threefoldtech/jumpscaleX/issues/652"}
        if builder in skipped_builders:
            self.skipTest(skipped_builders[builder])
        logger.info("%s builder: run build method." % builder)
        getattr(j.builders.db, builder).build()
        logger.info("%s builder: run install  method." % builder)
        getattr(j.builders.db, builder).install()
        logger.info("%s builder: run start method." % builder)
        getattr(j.builders.db, builder).start()
        logger.info("check that %s server started successfully." % builder)
        time.sleep(10)
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        logger.info("%s builder: run stop method." % builder)
        getattr(j.builders.db, builder).stop()
        logger.info("check that %s server stopped successfully." % builder)
        time.sleep(10)
        self.assertFalse(len(j.sal.process.getProcessPid(process)))
