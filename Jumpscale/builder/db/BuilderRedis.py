from Jumpscale import j
from random import randint
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
        j.builder.tools.file_copy('{DIR_TEMP}/build/redis/redis-stable/src/redis-server', '{DIR_BIN}', overwrite=False)
        j.builder.tools.file_copy('{DIR_TEMP}/build/redis/redis-stable/src/redis-cli', '{DIR_BIN}', overwrite=False)
        j.builder.tools.dir_remove('{DIR_BASE}/apps/redis')

    @property
    def startup_cmds(self):
        cmds = [j.tools.startupcmd.get(name="redis_server", cmd='redis-server --port {}'.format(randint(6000, 7000)))]
        return cmds
  
    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        bins = ['redis-server', 'redis-cli']

        lib_dest = self.tools.joinpaths(self.DIR_SANDBOX, 'sandbox')
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            bin_path = self.tools.joinpaths(j.core.dirs.BINDIR, bin)
            j.tools.sandboxer.sandbox_chroot(bin_path, lib_dest)
