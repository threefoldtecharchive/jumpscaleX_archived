from Jumpscale import j
builder_method = j.builder.system.builder_method


class BuilderRedis(j.builder.system._BaseClass):
    NAME = "redis-server"

    @builder_method()
    def build(self):
        if j.core.platformtype.myplatform.isUbuntu:
            j.builder.system.package.mdupdate()
            j.builder.system.package.ensure("build-essential")

            j.builder.tools.dir_remove("{DIR_TEMP}/build/redis")

            C = """
            #!/bin/bash
            set -ex
            mkdir -p {DIR_TEMP}/build/redis
            cd {DIR_TEMP}/build/redis
            wget http://download.redis.io/redis-stable.tar.gz
            tar xzf redis-stable.tar.gz
            cd redis-stable
            make

            rm -f /usr/local/bin/redis-server
            rm -f /usr/local/bin/redis-cli
            """
            self._execute(C)

        else:
            raise j.exceptions.NotImplemented(message="only ubuntu supported for building redis")

    @builder_method()
    def install(self):
        """
         will build if required & then install binary on right location
        :return:
        """
        self.build()
        j.builder.tools.file_copy('{DIR_TEMP}/build/redis/redis-stable/src/redis-server', '{DIR_BIN}', overwrite=True)
        j.builder.tools.file_copy('{DIR_TEMP}/build/redis/redis-stable/src/redis-cli', '{DIR_BIN}', overwrite=True)
        j.builder.tools.dir_remove('{DIR_BASE}/apps/redis')

    @property
    def startup_cmds(self):
        cmds = [j.tools.startupcmd.get(name="redis_server", cmd='redis-server')]
        return cmds
  
    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        bin_dest = j.sal.fs.joinPaths("/sandbox/var/build", "{}/sandbox".format(self.DIR_SANDBOX))
        self.tools.dir_ensure(bin_dest)
        redis_server_bin_path = self.tools.joinpaths("{DIR_BIN}", self.NAME)
        redis_client_bin_path = self.tools.joinpaths("{DIR_BIN}", "redis-cli")
        self.tools.file_copy(redis_server_bin_path, bin_dest)
        self.tools.file_copy(redis_client_bin_path, bin_dest)


