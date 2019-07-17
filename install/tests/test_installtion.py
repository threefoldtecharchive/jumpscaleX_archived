from .base_test import BaseTest


class Test_instaltion(BaseTest):
    def setUp(self):
        pass

    def test01_install_jumpscale_on_linux_inside_docker(self):
        """
        test TCR337
        *Test libs builers sandbox*
        #. Install jumpscale from specific branch
        """

        self.info("Install jumpscale from {} branch".format(self.js_branch))
        output, error = self.jumpscale_installtion()
        self.assertIn("install succesfull", output)

        self.info(" Run container_kosmos ,should succeed")
        command = "/tmp/jsx container_kosmos"
        output, error = self.linux_os(command)
        self.assertIn("BCDB INIT DONE", output)
        self.assertFalse(error)

    def Test02_container_stop_and_container_start_options_Linux_os(self):
        """
        test TCR338
        """
        self.info(" Check that js container exist ,should succeed")
        command = "/tmp/jsx container_kosmos"
        output, error = self.linux_os(command)
        if error:
            output, error = self.jumpscale_installtion()
            self.assertIn("install succesfull", output)

        self.info("Run container stop ")
        command = "/tmp/jsx container_stop"
        output, error = self.linux_os(command)

        self.info("Check that container stopped successfully")
        command = "docker ps -a -f status=running  | grep {}".format(self.jsname)
        output, error = self.linux_os(command)
        self.assertFalse(output)

        self.info("Run container started ")
        command = "/tmp/jsx container_start"
        output, error = self.linux_os(command)

        self.info("Check that container started successfully")
        command = "docker ps -a -f status=running  | grep {}".format(self.jsname)
        output, error = self.linux_os(command)
        self.assertIn(self.jsname, output.decode())
