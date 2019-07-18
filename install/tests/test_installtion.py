from .base_test import BaseTest


class Test_instaltion(BaseTest):
    def setUp(self):
        pass

    def test01_install_jumpscale_on_linux_inside_docker(self):
        """
        test TCR337
        *Test libs builers sandbox*
        #. Install jumpscale from specific branch
        #. Run container_kosmos ,should succeed
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
        #. Check that js container exist ,should succeed.
        #. Run container stop.
        #. Check that container stopped successfully.
        #. Run container started.
        #. Check that container started successfully

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
        command = "docker ps -a -f status=running  | grep {}".format(self.js_container)
        output, error = self.linux_os(command)
        self.assertFalse(output)

        self.info("Run container started ")
        command = "/tmp/jsx container_start"
        output, error = self.linux_os(command)

        self.info("Check that container started successfully")
        command = "docker ps -a -f status=running  | grep {}".format(self.js_container)
        output, error = self.linux_os(command)
        self.assertIn(self.js_container, output.decode())

    def Test03_jumpscale_installtion_inside_jumpscale_docker_Linux_os(self):
        """
        test TCR338
        #. Run kosmos command inside docker, should start kosmos shell .
        #. Run js_init generate command inside docker, sshould run successfully.
        #. Check the branch of jumpscale code, should be same as installtion branch.

        """
        self.info("Run kosmos command inside docker,should start kosmos shell")
        command = "docker exec -i {} /bin/bash -c 'source /sandbox/env.sh && kosmos'".format(self.js_container)
        output, error = self.linux_os(command)
        self.assertIn("BCDB INIT DONE", output)
        self.info("Run js_init generate ")
        command = "docker exec -i {} /bin/bash -c 'source /sandbox/env.sh && js_init generate'".format(
            self.js_container
        )
        output, error = self.linux_os(command)
        self.assertIn("process", output.decode())
        self.assertFalse(error)

        self.info(" Check the branch of jumpscale code, should be same as installtion branch.")
        command = "docker exec -i {} /bin/bash -c 'cd /sandbox/code/github/threefoldtech/jumpscaleX && cat .git/HEAD'".format(
            self.js_container
        )
        output, error = self.linux_os(command)
        branch = output.decode()[output.decode().find("head") + 6 : -2]
        self.assertEqual(branch, self.js_branch)

