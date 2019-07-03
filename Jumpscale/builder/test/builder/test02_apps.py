from Jumpscale import j
from .base_test import BaseTest
from parameterized import parameterized


class AppsTestCases(BaseTest):
    @parameterized.expand([("digitalme", "openresty"), ("freeflow", "apache2"), ("hub", "hub"), ("odoo", "odoo")])
    def test_apps_builders(self, builder, process):
        """ BLD-001
        *Test web builers sandbox*
        """
        skipped_builders = {
            "digitalme": "https://github.com/threefoldtech/jumpscaleX/issues/675",
            "hub": "https://github.com/threefoldtech/jumpscaleX/issues/676",
        }
        if builder in skipped_builders:
            self.skipTest(skipped_builders[builder])
        
        self.info(" %s builder: run build method.".format(builder))
        getattr(j.builders.apps, builder).build()
        self.info(" %s builder: run install  method.".format(builder))
        getattr(j.builders.apps, builder).install()
        self.info(" %s builder: run start method.".format(builder))
        getattr(j.builders.apps, builder).start()
        self.info(" check that %s server started successfully.".format(builder))
        self.small_sleep()
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        self.info(" %s builder: run stop method.".format(builder))
        getattr(j.builders.apps, builder).stop()
        self.info(" check that %s server stopped successfully.".format(builder))
        self.small_sleep()
        self.assertFalse(len(j.sal.process.getProcessPid(process)))
