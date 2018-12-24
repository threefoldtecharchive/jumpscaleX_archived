from Jumpscale import j





class BuilderInfluxdb(j.builder.system._BaseClass):
    NAME = "influxd"

    def install(self, dependencies=False, start=False, reset=False):
        if self.doneCheck("install", reset):
            return

        if dependencies:
            j.builder.system.package.mdupdate()

        j.builder.core.dir_ensure('{DIR_BIN}')

        if j.core.platformtype.myplatform.isMac:
            j.builder.tools.package_install('influxdb')
            j.builder.core.dir_ensure("{DIR_VAR}/templates/cfg/influxdb")
            j.builder.core.file_copy(
                "/usr/local/etc/influxdb.conf", "{DIR_VAR}/templates/cfg/influxdb/influxdb.conf")

        elif j.builder.core.isUbuntu:
            j.builder.core.dir_ensure("{DIR_VAR}/templates/cfg/influxdb")
            C = """
            set -ex
            cd {DIR_TEMP}
            wget https://dl.influxdata.com/influxdb/releases/influxdb-1.6.0-static_linux_amd64.tar.gz
            tar xvfz influxdb-1.6.0-static_linux_amd64.tar.gz
            cp influxdb-1.6.0-1/influxd {DIR_BIN}/influxd
            cp influxdb-1.6.0-1/influx {DIR_BIN}/influx
            cp influxdb-1.6.0-1/influx_inspect {DIR_BIN}/influx_inspect
            cp influxdb-1.6.0-1/influx_stress {DIR_BIN}/influx_stress
            cp influxdb-1.6.0-1/influx_tsm {DIR_BIN}/influx_tsm
            cp influxdb-1.6.0-1/influxdb.conf {DIR_VAR}/templates/cfg/influxdb/influxdb.conf"""
            j.sal.process.execute(C, profile=True)
        else:
            raise RuntimeError("cannot install, unsuported platform")
        j.builder.sandbox.profileJS.addPath(j.core.tools.text_replace("{DIR_BIN}"))
        j.builder.sandbox.profileJS.save()
        binPath = j.builder.sandbox.cmdGetPath('influxd')
        j.builder.core.dir_ensure("{DIR_VAR}/data/influxdb")
        j.builder.core.dir_ensure("{DIR_VAR}/data/influxdb/meta")
        j.builder.core.dir_ensure("{DIR_VAR}/data/influxdb/data")
        j.builder.core.dir_ensure("{DIR_VAR}/data/influxdb/wal")
        content = j.builder.core.file_read(
            '{DIR_VAR}/templates/cfg/influxdb/influxdb.conf')
        cfg = j.data.serializers.toml.loads(content)
        cfg['meta']['dir'] = j.core.tools.text_replace("{DIR_VAR}/data/influxdb/meta")
        cfg['data']['dir'] = j.core.tools.text_replace("{DIR_VAR}/data/influxdb/data")
        cfg['data']['wal-dir'] = j.core.tools.text_replace("{DIR_VAR}/data/influxdb/wal")
        j.builder.core.dir_ensure('$CFGDIR/influxdb')
        j.sal.fs.writeFile('$CFGDIR/influxdb/influxdb.conf', j.data.serializers.toml.dumps(cfg))
        cmd = "%s -config $CFGDIR/influxdb/influxdb.conf" % (binPath)
        cmd = j.core.tools.text_replace(cmd)
        j.sal.fs.writeFile("{DIR_BIN}/start_influxdb.sh", cmd, mode=0o777)

        if start:
            self.start()

    def build(self, start=True):
        raise RuntimeError("not implemented")

    def start(self):
        binPath = j.builder.sandbox.cmdGetPath('influxd')
        cmd = "%s -config $CFGDIR/influxdb/influxdb.conf" % (binPath)
        j.builder.system.process.kill("influxdb")
        pm = j.builder.system.processmanager.get()
        pm.ensure("influxdb", cmd=cmd, env={}, path="")
