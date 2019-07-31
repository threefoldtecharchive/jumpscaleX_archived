from .base_test import BaseTest
import uuid


class TestInstallationInDocker(BaseTest):
    def setUp(self):
        self.CONTAINER_NAME = str(uuid.uuid4()).replace("-", "")[:10]
        self.info(
            "Install container jumpscale from {} branch in {} os type".format(self.get_js_branch(), self.get_os_type())
        )
        output, error = self.jumpscale_installation("container-install", "-n {}".format(self.CONTAINER_NAME))
        self.assertFalse(error)
        self.assertIn("installed successfully", output.decode())

    def tearDown(self):
        self.info("Delete jumpscale created container.")
        command = "docker rm {}".format(self.CONTAINER_NAME)
        self.os_command(command)

        command = "rm -rf /sandbox; rm -rf ~/sandbox"
        self.os_command(command)

    def Test01_verify_container_kosmos_option(self):
        """
        TC54

        ** Test installation of container jumpscale on linux or mac depending on os_type **

        *Test libs builers sandbox*
        #. Install jumpscale from specific branch
        #. Run container-kosmos ,should succeed
        """
        self.info("Run container_kosmos ,should succeed")
        command = "/tmp/jsx container-kosmos"
        output, error = self.os_command(command)
        self.assertFalse(error)
        self.assertIn("BCDB INIT DONE", output.decode())

    def Test02_verify_container_stop_start_options(self):
        """
        TC48,TC55
        ** test  container-stop and container-start options on mac or linux depending on os_type **

        #. Check that js container exist ,should succeed.
        #. Run container stop.
        #. Check that container stopped successfully.
        #. Run container started.
        #. Check that container started successfully

        """
        self.info(" Running on {} os type".format(self.os_type))

        self.info("Run container stop ")
        command = "/tmp/jsx container-stop"
        self.os_command(command)

        self.info("Check that container stopped successfully")
        command = "docker ps -a -f status=running  | grep {}".format(self.CONTAINER_NAME)
        output, error = self.os_command(command)
        self.assertFalse(output)

        self.info("Run container started ")
        command = "/tmp/jsx container-start"
        self.os_command(command)

        self.info("Check that container started successfully")
        command = "docker ps -a -f status=running  | grep {}".format(self.CONTAINER_NAME)
        output, error = self.os_command(command)
        self.assertIn(self.CONTAINER_NAME, output.decode())

    def Test03_verify_jsx_working_inside_docker(self):
        """
        TC51,TC56
        ** test jumpscale inside docker on mac or linux depending on os_type. **

        #. Run kosmos command inside docker, should start kosmos shell .
        #. Run js_init generate command inside docker, sshould run successfully.
        #. Check the branch of jumpscale code, should be same as installation branch.
        """
        self.info("Run kosmos command inside docker,should start kosmos shell")
        command = "source /sandbox/env.sh && kosmos"
        output, error = self.docker_command(command)
        self.assertIn("BCDB INIT DONE", output.decode())

        self.info("Run js_init generate ")
        command = "source /sandbox/env.sh && js_init generate"
        output, error = self.docker_command(command)
        self.assertFalse(error)
        self.assertIn("process", output.decode())

        self.info(" Check the branch of jumpscale code, should be same as installation branch.")
        command = "cat /sandbox/code/github/threefoldtech/jumpscaleX/.git/HEAD"
        output, _ = self.docker_command(command)
        branch = output.decode()[output.decode().find("head") + 6 : -2]
        self.assertEqual(branch, self.js_branch)

        self.info("check  that ssh-key loaded in docker successfully")
        command = "cat /root/.ssh/authorized_keys"
        output, error = self.docker_command(command)
        self.assertEqual(output.decode().strip("\n"), self.get_loaded_key())

    def test04_verify_container_delete_option(self):
        """

        **Verify that container-delete option will delete the running container**
        """
        self.info("Delete the running jsx container using container-delete")
        command = "/tmp/jsx container-delete"
        self.os_command(command)

        command = "docker ps -a | grep {}".format(self.CONTAINER_NAME)
        output, error = self.os_command(command)
        self.assertFalse(output)


class TestInstallationInSystem(BaseTest):
    def tearDown(self):
        self.info("Clean the installation")
        command = "rm -rf ~/sandbox/ /tmp/jsx /tmp/jumpscale/ /tmp/InstallTools.py"
        self.os_command(command)

    def test01_install_jumpscale_insystem_no_interactive(self):
        """
        test TC63, TC64
        ** Test installation of Jumpscale using insystem non-interactive option on Linux or mac OS **
        #. Install jumpscale from specific branch
        #. Run kosmos ,should succeed
        """

        self.info("Install jumpscale from {} branch on {}".format(self.js_branch, self.os_type))
        output, error = self.jumpscale_installation("install")
        self.assertFalse(error)
        self.assertIn("installed successfully", output.decode())

        self.info("Run kosmos shell,should succeed")
        command = "source /sandbox/env.sh && kosmos"
        output, error = self.os_command(command)
        self.assertFalse(error)
        self.assertIn("BCDB INIT DONE", output.decode())

    def test02_verify_insystem_installation_with_r_option(self):
        """
        test TC65, TC66
        ** Test installation of Jumpscale using insystem non-interactive and re_install option on Linux or mac OS **
        #. Install jumpscale from specific branch
        #. Run kosmos ,should succeed
        """

        self.info(
            "Install jumpscale from {} branch on {} using no_interactive and re-install".format(
                self.js_branch, self.os_type
            )
        )
        output, error = self.jumpscale_installation("install", "-r")
        self.assertFalse(error)
        self.assertIn("installed successfully", output.decode())

        self.info(" Run kosmos shell,should succeed")
        command = "source /sandbox/env.sh && kosmos"
        output, error = self.os_command(command)
        self.info("Check the re-installation has been done successfully")
        self.assertFalse(error)
        self.assertIn("Distributor ID", output.decode())
        self.assertIn("BCDB INIT DONE", output.decode())
