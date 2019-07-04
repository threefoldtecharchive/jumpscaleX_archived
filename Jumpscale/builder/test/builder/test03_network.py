from Jumpscale import j
from .base_test import BaseTest
from parameterized import parameterized


class Network_TestCases(BaseTest):
    @parameterized.expand([("coredns", "coredns"), ("zerotier", "zerotier-one")])
    def test_network_builders(self, builder, process):
        """ BLD-001
        *Test network builers sandbox*
        """
        self.info(" %s builder: run build method.".format(builder))
        getattr(j.builders.network, builder).build()
        self.info(" %s builder: run install  method.".format(builder))
        getattr(j.builders.network, builder).install()
        self.info(" %s builder: run start method.".format(builder))
        try:
            getattr(j.builders.network, builder).start()
        except RuntimeError as e:
            self.fail(e)

        self.info(" check that %s server started successfully.".format(builder))
        self.small_sleep()
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        self.info(" %s builder: run stop method.".format(builder))
        try:
            getattr(j.builders.network, builder).stop()
        except RuntimeError as e:
            self.fail(e)

        self.info(" check that %s server stopped successfully.".format(builder))
        self.small_sleep()
        self.assertFalse(len(j.sal.process.getProcessPid(process)))
