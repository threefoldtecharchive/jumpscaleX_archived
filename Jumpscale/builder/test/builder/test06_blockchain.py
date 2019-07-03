from Jumpscale import j
from .base_test import BaseTest
from loguru import logger
import unittest


class Blockchain_TestCases(BaseTest):
    @classmethod
    def setUpClass(cls):
        logger.add("blockchain_tests_{time}.log")
        logger.debug("Starting of blockchain testcases.")

    def test001_bitcoin(self):
        """ BLD-014
        *Test bitcoin builer sandbox*
        """
        j.builders.blockchain.bitcoin.build(reset=True)
        j.builders.blockchain.bitcoin.install()
        j.builders.blockchain.bitcoin.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("bitcoind")))
        j.builders.blockchain.bitcoin.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("bitcoind")))

    def test002_ethereum(self):
        """ BLD-015
        *Test ethereum builer sandbox*
        """
        j.builders.blockchain.ethereum.build(reset=True)
        j.builders.blockchain.ethereum.install()
        j.builders.blockchain.ethereum.start()
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("ethereum")))
        j.builders.blockchain.ethereum.stop()
        self.assertEqual(0, len(j.sal.process.getProcessPid("ethereum")))

    @unittest.skip("https://github.com/threefoldtech/jumpscaleX/issues/677"):
    def test003_ripple(self):
        """ BLD-035
        *Test ripple builer sandbox*
        """
        logger.debug("Ripple builder: run build method.")
        j.builders.blockchain.ripple.build(reset=True)
        logger.debug("libffi builder: run install method.")
        j.builders.blockchain.ripple.install(reset=True)
        logger.debug("ripple builder: run start method.")
        j.builders.blockchain.ripple.start()
        logger.debug("check that ripple server started successfully.")
        self.assertGreaterEqual(1, len(j.sal.process.getProcessPid("ripple")))
        logger.debug("ripple builder: run stop method.")
        j.builders.blockchain.ripple.stop()
        logger.debug("check that ripple server started successfully.")
        self.assertGreaterEqual(0, len(j.sal.process.getProcessPid("ripple")  
