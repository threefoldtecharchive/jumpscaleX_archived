from Jumpscale import j
from time import sleep

builder_method = j.builders.system.builder_method


class BuilderMongodb(j.builders.system._BaseClass):
    NAME = "mongod"

    def _init(self):
        self.build_dir = self.tools.joinpaths(self.DIR_BUILD, "mongo_db/")

    @builder_method()
    def install(self):
        """
        install, move files to appropriate places, and create relavent configs
        """
        # install: python3 buildscripts/scons.py --prefix=/opt/mongo install
        bin_path = self.tools.joinpaths(self.build_dir, "mongod")
        self._copy(bin_path, "{DIR_BIN}")
        self.tools.dir_ensure(self._replace("{DIR_VAR}/data/mongodb"))

    @builder_method()
    def build(self):
        # needs libcurl-dev and libboost dependancies
        self.system.package.mdupdate()
        self.system.package.install(
            [
                "libcurl4-openssl-dev",
                "build-essential",
                "libboost-filesystem-dev",
                "libboost-program-options-dev",
                "libboost-system-dev",
                "libboost-thread-dev",
                "gcc-8",
                "g++-8",
                "python3-pip",
                "libssl-dev",
            ]
        )
        # update gcc
        self._execute(
            """
            update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 800 --slave /usr/bin/g++ g++ /usr/bin/g++-8
            """
        )
        # self.build_dir
        mongo_url = "https://github.com/mongodb/mongo/"
        self._remove(self.build_dir)
        j.clients.git.pullGitRepo(url=mongo_url, dest=self.build_dir, branch="master", depth=1)
        build_cmd = """
        cd {build_dir}
        pip3 install -r etc/pip/compile-requirements.txt
        python3 buildscripts/scons.py mongod MONGO_VERSION=4.2.0
        """.format(
            build_dir=self.build_dir
        )
        self._execute(build_cmd, timeout=4000)

        self._execute(
            """
            update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 700 --slave /usr/bin/g++ g++ /usr/bin/g++-7
            """
        )

    @builder_method()
    def clean(self):
        self._remove(self.build_dir)

    @builder_method()
    def reset(self):
        super().reset()
        self.clean()

    @property
    def startup_cmds(self):
        self.tools.dir_ensure(self._replace("{DIR_VAR}/data/mongodb"))
        cmd = self._replace("mongod --dbpath '{DIR_VAR}/data/mongodb'")
        cmd_start = cmd

        cmd = j.tools.startupcmd.get(self.NAME, cmd=cmd_start)
        return [cmd]

    @builder_method()
    def stop(self):
        j.sal.process.killProcessByName(self.NAME)

    @builder_method()
    def test(self):
        if self.running():
            self.stop()
        self.start()
        assert self.running()
        self.stop()
        print("TEST OK")

    @builder_method()
    def sandbox(
        self,
        reset=False,
        zhub_client=None,
        flist_create=False,
        merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
    ):
        """Copy built bins to dest_path and create flist if create_flist = True

        :param dest_path: destination path to copy files into
        :type dest_path: str
        :param sandbox_dir: path to sandbox
        :type sandbox_dir: str
        :param create_flist: create flist after copying files
        :type create_flist:bool
        :param zhub_client: hub instance to upload flist tos
        :type zhub_client:str
        """

        sandbox_dir = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox")
        self.tools.dir_ensure(sandbox_dir)

        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox", "bin")
        self.tools.dir_ensure(bin_dest)
        bins = ["mongod"]
        for bin in bins:
            self._copy("{DIR_BIN}/" + bin, bin_dest)

        lib_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox")
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self.tools.joinpaths(bin_dest, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest)

        # startup.toml
        templates_dir = self.tools.joinpaths(j.sal.fs.getDirName(__file__), "templates")
        startup_path = self._replace("{DIR_SANDBOX}/.startup.toml")
        self._copy(self.tools.joinpaths(templates_dir, "mongodb_startup.toml"), startup_path)
