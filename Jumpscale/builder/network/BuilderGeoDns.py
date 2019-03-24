from Jumpscale import j





class BuilderGeoDns(j.builder.system._BaseClass):
    NAME = "geodns"

    def reset(self):
        app.reset(self)
        self._init()

    def install(self, reset=False):
        """
        installs and builds geodns from github.com/abh/geodns
        """
        if reset is False and self.isInstalled():
            return
        # deps
        # j.builder.runtimes.golang.install(force=False)
        j.builder.system.package.mdupdate()
        j.builder.system.package.ensure(["libgeoip-dev", 'build-essential', 'pkg-config'])

        # build
        j.builder.runtimes.golang.get("github.com/abh/geodns")

        # moving files and creating config
        j.core.tools.dir_ensure('{DIR_BIN}')
        j.builder.tools.file_copy("{DIR_BASE}/go/bin/geodns", "{DIR_BIN}")
        j.core.tools.dir_ensure("{DIR_VAR}/templates/cfg/geodns/dns", recursive=True)
        profile = #j.builder.sandbox.profileDefault
        profile.addPath('{DIR_BIN}')
        profile.save()

        j.builder.tools.file_copy(
            "{DIR_VAR}/templates/cfg/geodns", "{DIR_BASE}/cfg/", recursive=True)

    def start(self, ip="0.0.0.0", port="5053", config_dir="{DIR_BASE}/cfg/geodns/dns/",
              identifier="geodns_main", cpus="1", tmux=False):
        """
        starts geodns server with given params
        """
        if j.builder.tools.dir_exists(config_dir):
            j.core.tools.dir_ensure(config_dir)
        cmd = "{DIR_BIN}/geodns -interface %s -port %s -config=%s -identifier=%s -cpus=%s" % (
            ip, str(port), config_dir, identifier, str(cpus))
        if tmux:
            pm = j.builder.system.processmanager.get("tmux")
            pm.ensure(name=identifier, cmd=cmd, env={}, path="{DIR_BIN}")
        else:
            pm = j.builder.system.processmanager.get()
            pm.ensure(name=identifier, cmd=cmd, env={}, path="{DIR_BIN}")

    def stop(self, name="geodns_main"):
        """
        stop geodns server with @name
        """
        pm = j.builder.system.processmanager.get()
        pm.stop(name)
