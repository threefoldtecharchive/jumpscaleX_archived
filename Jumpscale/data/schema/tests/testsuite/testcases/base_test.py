from Jumpscale.data.schema.tests.testsuite.framework.schema import Schema
from Jumpscale import j
from unittest import TestCase
from uuid import uuid4

logger = j.logger.get('testsuite.log')

class BaseTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.schema = Schema

    def SetUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def log(self, msg):
        self._log_info(msg)

    def random_string(self):
        return 's' + str(uuid4()).replace('-', '')[:10]
