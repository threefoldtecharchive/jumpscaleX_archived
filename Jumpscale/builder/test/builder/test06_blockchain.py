from Jumpscale import j
from base_test import BaseTest
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
