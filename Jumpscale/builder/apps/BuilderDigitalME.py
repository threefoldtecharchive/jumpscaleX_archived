from Jumpscale import j
import textwrap

builder_method = j.builder.system.builder_method


class BuilderDigitalME(j.builder.system._BaseClass):
    """
    specs:

        - build all required components (only work on ub 1804) using self.build
        - sandbox to sandbox dir
        - create flist
        - in self.test_zos() start the created flist & do the network tests for the openresty

    """
    NAME = "digitalme"

    @builder_method()
    def _init(self):
        pass

    @builder_method()
    def build(self, reset=False):
        """
        kosmos 'j.tools.sandboxer.sandbox_build()'

        will build python & openresty & copy all to the right git sandboxes works for Ubuntu only
        :return:
        """
        j.builder.runtimes.python.build(reset=reset)
        j.builder.runtimes.lua.build()  # will build openresty & lua & openssl
        j.clients.git.pullGitRepo(url="https://github.com/threefoldtech/digitalmeX.git", branch="3bot_registeration")

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        j.builder.runtimes.python.sandbox(reset=reset)
        j.builder.runtimes.lua.sandbox(reset=reset)
        j.tools.sandboxer.copyTo(j.builder.runtimes.python.DIR_SANDBOX, "{}/sandbox".format(self.DIR_SANDBOX))
        j.tools.sandboxer.copyTo(j.builder.runtimes.lua.DIR_SANDBOX,  self.DIR_SANDBOX)
        git_repo_path = "/sandbox/code/github/threefoldtech/digitalmeX"
        j.tools.sandboxer.copyTo(git_repo_path, j.sal.fs.joinPaths(self.DIR_SANDBOX, git_repo_path[1:]))

    @property
    def startup_cmds(self):
        cmd = j.tools.startupcmd.get("openresty", "openresty", cmd_stop="openresty -s stop", path="/sandbox/bin")
        return [cmd]


    def gslides(self):
        """
        kosmos 'j.builder.apps.digitalme.gslides()'
        google slides option
        :return:
        """
        j.shell()
        "google-api-python-client,google-auth-httplib2,google-auth-oauthlib"

    def test(self, zos_client=None):
        """
        j.builder.apps.digitalme.test()
        test locally, start openresty and do network check
        :return:
        """
        self.sandbox()
        self.start()
        assert j.sal.nettools.waitConnectionTest("localhost", 8081, timeoutTotal=10)
        self._log_info("TEST OK FOR DIGITAL ME BUILDING")

    def test_zos(self, zos_client, zhubclient):
        flist = self.sandbox(zhub_client=zhubclient)
        container_id = zos_client.container.create(flist, name="test_digitalme").get()
        container_client = zos_client.cotainer.client(container_id)
        assert container_client.ping()
        # TODO: find a way to check if openresty started on the container


