from Jumpscale import j
from time import sleep

builder_method = j.builder.system.builder_method


class BuilderS3Scality(j.builder.system._BaseClass):
    NAME = "s3scality"

    @property
    def path(self):
        return self._replace("{DIR_BASE}/apps/%s" % self.NAME)

    @builder_method()
    def build(self, reset=False):
        j.builder.runtimes.python.build(reset=reset)
        j.builder.runtimes.nodejs.build(reset=reset)

        path = "%s/%s" % (self.DIR_BUILD, self.NAME)
        j.builder.tools.dir_remove(path, recursive=True)
        j.clients.git.pullGitRepo("https://github.com/scality/S3.git", ssh=False, dest=path)

    @builder_method()
    def install(self, reset=False, storage="{DIR_VAR}/scality/data/", meta="{DIR_VAR}/scality/meta/"):
        j.builder.runtimes.python.install(reset=reset)
        j.builder.runtimes.nodejs.install(reset=reset)
        j.builder.runtimes.nodejs.npm_install("npm-run-all")
        j.builder.system.package.mdupdate()
        j.builder.system.package.ensure("build-essential,g++")

        j.core.tools.dir_ensure(storage)
        j.core.tools.dir_ensure(meta)

        j.builder.tools.dir_remove(self.path, recursive=True)
        j.core.tools.dir_ensure("{DIR_BASE}/apps/")
        j.builder.tools.execute("mv %s/%s %s" % (self.DIR_BUILD, self.NAME, self.path))
        j.builder.tools.execute("cd %s && npm install" % self.path)

        cmd = "S3DATAPATH={data} S3METADATAPATH={meta} npm start".format(
            data=self._replace(storage), meta=self._replace(meta)
        )
        content = j.core.tools.file_text_read("%s/package.json" % self.path)
        pkg = j.data.serializers.json.loads(content)
        pkg["scripts"]["start_location"] = cmd

        content = j.data.serializers.json.dumps(pkg, indent=True)
        j.sal.fs.writeFile("%s/package.json" % self.path, content)

    @property
    def startup_cmds(self):
        path = j.builder.runtimes.nodejs.NODE_PATH
        node_path = "%s/@zenko/cloudserver/node_modules/:%s" % (path, path)
        if self.tools.profile.env_exists("NODE_PATH") and self.tools.profile.env_get("NODE_PATH") != node_path:
            self.tools.profile.env_set("NODE_PATH", node_path)

        cmd = j.tools.startupcmd.get(
            self.NAME, cmd=self._replace("cd %s && npm run start_location" % self.path), env={"NODE_PATH": node_path}
        )
        return [cmd]

    def stop(self):
        # killing the daemon
         j.tools.tmux.pane_get(self.NAME).kill()

    @builder_method()
    def test(self):
        if self.running():
            self.stop()

        self.start()
        assert self.running()

        self._log_info("TEST SUCCESS: scality is running")
