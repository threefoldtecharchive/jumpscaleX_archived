from Jumpscale import j
from base_test import BaseTest
from loguru import logger
import unittest, time


class db_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("db_tests_{time}.log")
        logger.debug("Starting of db testcases.")

    def test001_zbd(self):
        """ BLD-016
        *Test zdb builer sandbox*
        """
        logger.debug("Zdb builder: run build method.")
        j.builders.db.zdb.build(reset=True)
        logger.debug("zdb builder: run install method.")
        j.builders.db.zdb.install()
        logger.debug("zdb builder: run start method.")
        j.builders.db.zdb.start()
        logger.debug("check that zdb server started successfully.")
        self.assertEqual(1, len(j.sal.process.getProcessPid("zdb")))
        logger.debug("zdb builder: run stop method.")
        j.builders.db.zdb.stop()
        logger.debug("check that zdb server stopped successfully.")
        self.assertEqual(0, len(j.sal.process.getProcessPid("zdb")))

    def test002_etcd(self):
        """ BLD-017
        *Test etcd builer sandbox*
        """
        logger.debug("ETCD builder: run build method. ")
        j.builders.db.etcd.build(reset=True)
        logger.debug("ETCD builder: run install method. ")
        j.builders.db.etcd.install()
        logger.debug("ETCD builder: run start method. ")
        j.builders.db.etcd.start()
        time.sleep(10)
        logger.debug("check that etcd builder is started successfully. ")
        self.assertTrue(len(j.sal.process.getProcessPid("etcd")))
        logger.debug("ETCD builder: run stop method. ")
        j.builders.db.etcd.stop()
        time.sleep(10)
        logger.debug("check that etcd builder is stopped successfully. ")
        self.assertEqual(0, len(j.sal.process.getProcessPid("etcd")))

    def test003_redis(self):
        """ BLD-018
        *Test redis builer sandbox*
        """
        logger.debug("Redis builder: run build method. ")
        j.builders.db.redis.build(reset=True)
        logger.debug("Redis builder: run install method. ")
        j.builders.db.redis.install()
        logger.debug("Redis builder: run start method. ")
        j.builders.db.redis.start()
        logger.debug("check that Redis builder is started successfully")
        self.assertEqual(2, len(j.sal.process.getProcessPid("redis-server")))
        logger.debug("Redis builder: run stop method. ")
        j.builders.db.redis.stop()
        logger.debug("check that Redis builder is stopped successfully")
        self.assertEqual(1, len(j.sal.process.getProcessPid("redis-server")))

    def test004_ardb(self):
        """ BLD-020
        *Test ardb builer sandbox*
        """
        logger.debug("ardb builder: run build method. ")
        j.builders.db.ardb.build(reset=True)
        logger.debug("ardb builder: run install method. ")
        j.builders.db.ardb.install()
        logger.debug("ardb builder: run start method. ")
        j.builders.db.ardb.start()
        logger.debug("check that ardb builder is started successfully. ")
        self.assertTrue(j.sal.process.getProcessPid("ardb"))
        logger.debug("ardb builder: run stop method. ")
        j.builders.db.ardb.stop()
        logger.debug("check that ardb builder is stopped successfully. ")
        self.assertFalse(j.sal.process.getProcessPid("ardb"))

    def test005_postgres(self):
        """ BLD-021
        *Test postgress builer sandbox*
        """
        logger.debug("PostgresDB builder: run build method. ")
        j.builders.db.postgres.build(reset=True)
        logger.debug("PostgresDB builder: run install method. ")
        j.builders.db.postgres.install()
        logger.debug("PostgresDB builder: run start method. ")
        j.builders.db.postgres.start()
        logger.debug("check that postgres builder is started correctly")
        self.assertTrue(j.sal.process.getProcessPid("postgres"))
        logger.debug("PostgresDB builder: run stop method. ")
        j.builders.db.postgres.stop()
        logger.debug("check that postgres builder is stopped correctly")
        self.assertFalse(j.sal.process.getProcessPid("postgres"))

    def test006_influx(self):
        """ BLD-022
        *Test influx builer sandbox*
        """
        logger.debug("influxDB builder: run build method. ")
        j.builders.db.influxdb.build(reset=True)
        logger.debug("influxDB builder: run install method. ")
        j.builders.db.influxdb.install()
        logger.debug("influxDB builder: run start method. ")
        j.builders.db.influxdb.start()
        logger.debug("check that influxdb builder is started correctly")
        self.assertTrue(j.sal.process.getProcessPid("influx"))
        logger.debug("influxDB builder: run stop method. ")
        j.builders.db.influxdb.stop()
        logger.debug("check that influxdb builder is started correctly")
        self.assertFalse(j.sal.process.getProcessPid("influx"))

    def test007_mongodb(self):
        """ BLD-023
        *Test mongodb builer sandbox*
        """
        logger.debug("mongodb builder: run build method.")
        j.builders.db.mongodb.build(reset=True)
        logger.debug("mongodb builder: run install method.")
        j.builders.db.mongodb.install()
        logger.debug("mongodb builder: run start method.")
        j.builders.db.mongodb.start()
        logger.debug("check that mongodb started successfully.")
        self.assertTrue(j.sal.process.getProcessPid("mongod"))
        logger.debug("mongodb builder: run stop method.")
        j.builders.db.mongodb.stop()
        logger.debug("check that mongodb stopped successfully.")
        self.assertFalse(j.sal.process.getProcessPid("mongod"))

