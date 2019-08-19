import unittest
import subprocess
from loguru import logger

class BaseTest(unittest.TestCase):
    LOGGER = logger
    LOGGER.add("Config_manager_{time}.log")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def info(message):
        BaseTest.LOGGER.info(message)
        


    




