from Jumpscale import j


class BuilderRestic(j.builder.system._BaseClass):

    NAME = "restic"

    def _init(self):
        self.BUILDDIR = j.core.tools.text_replace("{DIR_VAR}/build/restic")
        self.DOWNLOAD_DEST = "{}/linux_amd64.bz2".format(self.BUILDDIR)
        self.FILE_NAME = "{}/linux_amd64".format(self.BUILDDIR)

    @property
    def CODEDIR(self):
        return "{}/src/github.com/restic/restic".format(j.builder.runtimes.golang.GOPATH)

    def reset(self):
        """
        helper method to clean what this module generates.
        """
        super().reset()
        j.sal.fs.remove(self.BUILDDIR)
        j.sal.fs.remove(self.CODEDIR)

    def quick_install(self, install=True, reset=False):
        if reset is False and (self.isInstalled() or self._done_get("quick_install")):
            return
        if not j.builder.tools.file_exists(self.DOWNLOAD_DEST):
            j.builder.tools.file_download(
                "https://github.com/restic/restic/releases/download/v0.9.0/restic_0.9.0_linux_amd64.bz2",
                self.DOWNLOAD_DEST,
            )
        j.builder.tools.file_expand(self.DOWNLOAD_DEST)
        j.sal.process.execute("chmod +x {}".format(self.FILE_NAME))

        self._done_set("quick_install")

        if install:
            self.install(source=self.FILE_NAME)

    def build(self, install=True, reset=False):
        if reset is False and (self.isInstalled() or self._done_get("build")):
            return

        if reset:
            self.reset()

        j.builder.runtimes.golang.install()

        # build
        url = "https://github.com/restic/restic/"
        j.clients.git.pullGitRepo(url, dest=self.CODEDIR, ssh=False, depth=1)

        build_cmd = "cd {dir}; go run build.go -k -v".format(dir=self.CODEDIR)
        j.sal.process.execute(build_cmd, profile=True)

        self._done_set("build")

        if install:
            self.install()

    def install(self, source=None, reset=False):
        """
        download, install, move files to appropriate places, and create relavent configs
        """

        if self._done_get("install") and not reset:
            return

        if source:
            j.builder.tools.file_copy(self.FILE_NAME, "{DIR_BIN}/restic")
        else:
            j.builder.tools.file_copy(self.CODEDIR + "/restic", "{DIR_BIN}")

        self._done_set("install")

    def getRepository(self, path, password, repo_env=None):
        """
        @param repo_env (dict) sets needed environemnt params to create/use repo
        @return ResticRepository object. If the repo doesn't exist yet, it will
                be created and initialized
        """
        return ResticRepository(path, password, self.prefab, repo_env)


class ResticRepository:
    """This class represent a restic repository used for backup"""

    def __init__(self, path, password, prefab, repo_env=None):
        self.path = path
        self.__password = password
        self.repo_env = repo_env
        self.prefab = prefab

        if not self._exists():
            self.initRepository()

    def _exists(self):
        rc, _, _ = self._run("{DIR_BIN}/restic snapshots > /dev/null", die=False)
        if rc > 0:
            return False
        return True

    def _run(self, cmd, env=None, die=True, showout=True):
        env_vars = {"RESTIC_REPOSITORY": self.path, "RESTIC_PASSWORD": self.__password}
        if self.repo_env:
            env_vars.update(self.repo_env)
        if env:
            env_vars.update(env)
        return j.sal.process.execute(cmd=cmd, env=env_vars, die=die, showout=showout)

    def initRepository(self):
        """
        initialize the repository at self.path location
        """
        cmd = "{DIR_BIN}/restic init"
        self._run(cmd)

    def snapshot(self, path, tag=None):
        """
        @param path: directory/file to snapshot
        @param tag: tag to add to the snapshot
        """
        cmd = "{DIR_BIN}/restic backup {} ".format(path)
        if tag:
            cmd += " --tag {}".format(tag)
        self._run(cmd)

    def restore_snapshot(self, snapshot_id, dest):
        """
        @param snapshot_id: id of the snapshot to restore
        @param dest: path where to restore the snapshot to
        """
        cmd = "{DIR_BIN}/restic restore --target {dest} {id} ".format(dest=dest, id=snapshot_id)
        self._run(cmd)

    def list_snapshots(self):
        """
        @return: list of dict representing a snapshot
        { 'date': '2017-01-17 16:15:28',
          'directory': '/optvar/cfg',
          'host': 'myhost',
          'id': 'ec853b5d',
          'tags': 'backup1'
        }
        """
        cmd = "{DIR_BIN}/restic snapshots"
        _, out, _ = self._run(cmd, showout=False)

        snapshots = []
        for line in out.splitlines()[2:-2]:
            ss = list(self._chunk(line))

            snapshot = {"id": ss[0], "date": " ".join(ss[1:3]), "host": ss[3]}
            if len(ss) == 6:
                snapshot["tags"] = ss[4]
                snapshot["directory"] = ss[5]
            else:
                snapshot["tags"] = ""
                snapshot["directory"] = ss[4]
            snapshots.append(snapshot)

        return snapshots

    def check_repo_integrity(self):
        """
        @return: True if integrity is ok else False
        """
        cmd = "{DIR_BIN}/restic check"
        rc, _, _ = self._run(cmd)
        if rc != 0:
            return False
        return True

    def _chunk(self, line):
        """
        passe line and yield each word separated by space
        """
        word = ""
        for c in line:
            if c == " ":
                if word:
                    yield word
                    word = ""
                continue
            else:
                word += c
        if word:
            yield word
