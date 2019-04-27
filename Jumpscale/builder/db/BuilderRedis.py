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

            C = j.builder.tools.replace(C)
            C = self._replace(C)
            j.sal.process.execute(C)

            # move action
            C = """
            set -ex
            mkdir -p {DIR_BIN}
            cp -f {DIR_TEMP}/build/redis/redis-stable/src/redis-server {DIR_BIN}
            cp -f {DIR_TEMP}/build/redis/redis-stable/src/redis-cli {DIR_BIN}
            rm -rf {DIR_BASE}/apps/redis
            """
            C = j.builder.tools.replace(C)
            C = self._replace(C)
            j.sal.process.execute(C)
        else:
            raise j.exceptions.NotImplemented(message="only ubuntu supported for building redis")

        self._done_set("build")

        if start is True:
            self.start()

    def isInstalled(self):
        return j.builder.tools.command_check('redis-server') and j.builder.tools.command_check('redis-cli')

    def install(self, reset=False):
        return self.build(reset=reset)

    def start(self, name="main", ip="localhost", port=6379, max_ram="50mb", append_only=True,
              snapshot=False, slave=(), is_master=False, password=None, unixsocket=None):
        if unixsocket is not None:
            redis_socket = j.sal.fs.getParent(unixsocket)
            j.core.tools.dir_ensure(redis_socket)

        self.configure_instance(name,
                                ip,
                                port,
                                max_ram=max_ram,
                                append_only=append_only,
                                snapshot=snapshot,
                                slave=slave,
                                is_master=is_master,
                                password=password,
                                unixsocket=unixsocket)
        # return if redis is already running
        if self.is_running(ip_address=ip, port=port, path='{DIR_BIN}', password=password, unixsocket=unixsocket):
            self._log_info('Redis is already running!')
            return

        _, c_path = self._get_paths(name)

        cmd = "{DIR_BIN}/redis-server %s" % c_path
        cmd = self._replace(cmd)
        pm = j.builder.system.processmanager.get()
        pm.ensure(name="redis_%s" % name, cmd=cmd,
                  env={}, path='{DIR_BIN}', autostart=True)

        # Checking if redis is started correctly with port specified
        if not self.is_running(ip_address=ip, port=port, path='{DIR_BIN}', unixsocket=unixsocket, password=password):
            raise j.exceptions.RuntimeError(
                'Redis is failed to start correctly')

    def stop(self, name='main'):
        pm = j.builder.system.processmanager.get()
        pm.stop(name="redis_%s" % name)

    def is_running(self, ip_address='localhost', port=6379, path='{DIR_BIN}', password=None, unixsocket=None):
        if ip_address != '' and port != 0:
            ping_cmd = '%s/redis-cli -h %s -p %s ' % (path, ip_address, port)
        elif unixsocket is not None:
            ping_cmd = '%s/redis-cli -s %s ' % (path, unixsocket)
        else:
            raise j.exceptions.RuntimeError("can't connect to redis")

        ping_cmd = self._replace(ping_cmd)
        if password is not None and password.strip():
            ping_cmd += ' -a %s ' % password
        ping_cmd += ' ping'
        rc, out, err = j.sal.process.execute(ping_cmd, die=False)
        return not rc and out == 'PONG'

    def _get_paths(self, name):
        d_path = j.sal.fs.joinPaths(
            j.builder.tools.dir_paths["VARDIR"], 'redis', name)
        c_path = j.sal.fs.joinPaths(d_path, "redis.conf")
        return d_path, c_path

    def empty_instance(self, name):
        d_path, _ = self._get_paths(name)
        j.builder.tools.dir_remove(d_path)
        j.core.tools.dir_ensure(d_path)

    def configure_instance(self, name, ip="localhost", port=6379, max_ram="1048576", append_only=True,
                           snapshot=False, slave=(), is_master=False, password=None, unixsocket=False):

        cmd = 'sysctl vm.overcommit_memory=1'
        j.sal.process.execute(cmd, die=False, showout=False)

        self.empty_instance(name)

        config = j.sal.fs.read_file("%s/REDISCONFIG.conf"%self._dirpath)

        #TODO: clearly not working yet

        self.install()

        j.builder.tools.file_copy('{DIR_TEMP}/build/redis/redis-stable/src/redis-server', '{DIR_BIN}', overwrite=True)
        j.builder.tools.file_copy('{DIR_TEMP}/build/redis/redis-stable/src/redis-cli', '{DIR_BIN}', overwrite=True)
        j.builder.tools.dir_remove('{DIR_BASE}/apps/redis')

    @property
    def startup_cmds(self):
        cmds = [j.tools.startupcmd.get(name="redis_server", cmd='redis-server')]
        return cmds

