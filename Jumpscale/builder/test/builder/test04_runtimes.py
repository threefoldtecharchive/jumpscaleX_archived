import time
from Jumpscale import j
from .base_test import BaseTest
from parameterized import parameterized

class Runtimes_TestCases(BaseTest):
    @parameterized.expand([("lua", "openresty"), ("php", "php-fpm")])
    def test_runtimes_builders(self, builder, process):
        """ BLD-001
        *Test runtimes builers sandbox*
        """
        self.info("%s builder: run build method." % builder)
        getattr(j.builders.runtimes, builder).build()
        self.info(" * {} builder: run install  method.".format(builder))
        getattr(j.builders.runtimes, builder).install()
        self.info(" * {} builder: run start method.".format(builder))
        getattr(j.builders.runtimes, builder).start()
        self.info(" Check that {} server started successfully.".format(builder))
        self.small_sleep()
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        self.info(" * {} builder: run stop method.".format(builder))
        getattr(j.builders.runtimes, builder).stop()
        self.info(" Check that {} server stopped successfully.".foramt(builder))
        self.small_sleep()
        self.assertFalse(len(j.sal.process.getProcessPid(process)))