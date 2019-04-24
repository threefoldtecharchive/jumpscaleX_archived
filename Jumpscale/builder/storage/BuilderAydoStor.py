from Jumpscale import j




# TODO: is this still correct, maybe our docker approach better, need to check


class BuilderAydoStor(j.builder.system._BaseClass):

    NAME = 'stor'

    def build(self, addr='0.0.0.0:8090', backend="{DIR_VAR}/aydostor", start=True, install=True, reset=False):
        """
        Build and Install aydostore
        @input addr, address and port on which the service need to listen. e.g. : 0.0.0.0:8090
        @input backend, directory where to save the data push to the store
        """
        if self.isInstalled() and not reset:
            self._log_info('Aydostor is already installed, pass reinstall=True parameter to reinstall')
            return

        j.builder.system.package.mdupdate()
        j.builder.system.package.ensure('build-essential')

        j.builder.tools.dir_remove("%s/src" % #j.builder.sandbox.env_get('GOPATH'))
        j.builder.runtimes.golang.get("github.com/g8os/stor")

        if install:
            self.install(addr, backend, start)

    def install(self, addr='0.0.0.0:8090', backend="{DIR_VAR}/aydostor", start=True):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        j.core.tools.dir_ensure('{DIR_BIN}')
        j.builder.tools.file_copy(j.builder.tools.joinpaths(
            j.builder.tools.dir_paths['GODIR'], 'bin', 'stor'), '{DIR_BIN}', overwrite=True)
        #j.builder.sandbox.path_add("{DIR_BASE}/bin")

        pm = j.builder.system.processmanager.get()
        pm.stop("stor")  # will also kill

        j.core.tools.dir_ensure("{DIR_BASE}/cfg/stor")
        backend = self._replace(backend)
        j.core.tools.dir_ensure(backend)
        config = {
            'listen_addr': addr,
            'store_root': backend,
        }
        content = j.data.serializers.toml.dumps(config)
        j.core.tools.dir_ensure('{DIR_VAR}/templates/cfg/stor', recursive=True)
        j.sal.fs.writeFile("{DIR_VAR}/templates/cfg/stor/config.toml", content)

        if start:
            self.start(addr)

    def start(self, addr):
        res = addr.split(":")
        if len(res) == 2:
            addr, port = res[0], res[1]
        else:
            addr, port = res[0], '8090'

            j.builder.ufw.allowIncoming(port)
            if j.builder.system.process.tcpport_check(port, ""):
                raise RuntimeError(
                    "port %d is occupied, cannot start stor" % port)

        j.core.tools.dir_ensure("{DIR_BASE}/cfg/stor/", recursive=True)
        j.builder.tools.file_copy("{DIR_VAR}/templates/cfg/stor/config.toml", "{DIR_BASE}/cfg/stor/")
        cmd = #j.builder.sandbox.cmd_path_get("stor")
        pm = j.builder.system.processmanager.get()
        pm.ensure("stor", '%s --config {DIR_BASE}/cfg/stor/config.toml' % cmd)
