from Jumpscale import j
from .base_test import BaseTest
from parameterized import parameterized


class VirtualizationTestCases(BaseTest):
    @parameterized.expand([("docker", "containerd")])
    def test_virtualization_builders(self, builder, process):
        """ BLD-001
        *Test virtualization builers sandbox*
        """
        skipped_builders = {"docker": "https://github.com/threefoldtech/jumpscaleX/issues/664"}
        if builder in skipped_builders:
            self.skipTest(skipped_builders[builder])
        self.info(" %s builder: run build method.".format(builder))
        getattr(j.builders.virtualization, builder).build()
        self.info(" %s builder: run install  method.".format(builder))
        getattr(j.builders.virtualization, builder).install()
        self.info(" %s builder: run start method.".format(builder))
        getattr(j.builders.virtualization, builder).start()
        self.info(" check that %s server started successfully.".format(builder))
        self.small_sleep()
        self.assertTrue(len(j.sal.process.getProcessPid(process)))
        self.info(" %s builder: run stop method.".format(builder))
        getattr(j.builders.virtualization, builder).stop()
        self.info(" check that %s server stopped successfully.".format(builder))
        self.small_sleep()
        self.assertFalse(len(j.sal.process.getProcessPid(process)))

