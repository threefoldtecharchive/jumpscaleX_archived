from Jumpscale import j


class BuilderZdb(j.builder.system._BaseClass):

    def _init(self):
        self.git_url = 'https://github.com/threefoldtech/0-db.git'

    def build(self, reset=False, branch='development'):
        """
        build zdb
        :return:
        """
        if self._done_get('build') and reset is False:
            return

        j.builder.system.package.mdupdate()
        j.builder.system.package.ensure("git")
        path = j.builder.tools.joinpaths(j.sal.fs.getTmpDirPath(), '0-db')
        dest = j.clients.git.pullGitRepo(self.git_url, dest=path, ssh=False)

        self._done_set('build')
        return dest

    def install(self, branch="development", reset=False):
        """
        Installs the zdb binary to the correct location
        """

        if self._done_get('install') and reset is False:
            return

        base_dir = self.build(branch=branch, reset=reset)
        c = """
        cd {}
        make
        """.format(base_dir)

        j.sal.process.execute(c)
        zdb_bin_path = j.builder.tools.joinpaths(base_dir, 'bin/zdb')

        j.core.tools.dir_ensure("{DIR_BIN}")
        j.builder.tools.file_copy(zdb_bin_path, "{DIR_BIN}/")

        self._done_set('install')

    def start(self, destroydata=False):
        """
        start zdb in tmux using this directory
        will only start when the server is not life yet
        """

        return j.servers.zdb.start(destroydata)

    def stop(self):
        """
        stop zdb in tmux
        """
        return j.servers.zdb.stop()

    def isrunning(self):
        """
        check zdb binary is running or not
        """

        return j.servers.zdb.isrunning()
