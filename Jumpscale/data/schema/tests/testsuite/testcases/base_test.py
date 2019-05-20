from Jumpscale.data.schema.tests.testsuite.framework.schema import Schema
from Jumpscale import j
from unittest import TestCase
from uuid import uuid4


class BaseTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = Schema

    def SetUp(self):
        pass

    def tearDown(self):
        pass

    def log(self, msg):
        j.core.tools.log(msg, level=20)

    def random_string(self):
        return "s" + str(uuid4()).replace("-", "")[:10]
