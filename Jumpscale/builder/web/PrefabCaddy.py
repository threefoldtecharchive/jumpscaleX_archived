from Jumpscale import j





class BuilderCaddy(j.builder.system._BaseClass):
    NAME = "caddy"

    def _init(self):
        self.BUILDDIR_ = j.core.tools.text_replace("{DIR_VAR}/build/caddy")

    def reset(self):
        self.stop()
        app.reset(self)
        self._init()
        j.builder.tools.dir_remove(self.BUILDDIR_)
        j.builder.tools.dir_remove("{DIR_BIN}/caddy")

    def build(self, reset=False, plugins=None):
        """
        Get/Build the binaries of caddy itself.
        :param reset: boolean to reset the build process
        :param plugins: list of plugins names to be installed
        :return:
        """
        # if not j.builder.tools.isUbuntu:
        #     raise j.exceptions.RuntimeError("only ubuntu supported")

        if self._done_check('build', reset):
            return

        j.builder.system.installbase.install(upgrade=True)
        golang = j.builder.runtimes.golang
        golang.install()

        # build caddy from source using our caddyman
        j.clients.git.pullGitRepo("https://github.com/incubaid/caddyman", dest="/tmp/caddyman")
        j.sal.process.execute("cd /tmp/caddyman && chmod u+x caddyman.sh")
        if not plugins:
            plugins = ["iyo"]
        cmd = "/tmp/caddyman/caddyman.sh install {plugins}".format(plugins=" ".join(plugins))
        j.sal.process.execute(cmd)
        self._done_set('build')

    def install(self, plugins=None, reset=False, configpath="{DIR_CFG}/caddy.cfg"):
        """
        will build if required & then install binary on right location
        """
        self.build(plugins=plugins, reset=reset)

        if self._done_check('install', reset):
            return

        j.builder.tools.file_copy('/opt/go_proj/bin/caddy', '{DIR_BIN}/caddy')
        j.builder.sandbox.profileDefault.addPath('{DIR_BIN}')
        j.builder.sandbox.profileDefault.save()

        configpath = j.core.tools.text_replace(configpath)

        if not j.builder.tools.exists(configpath):
            # default configuration, can overwrite
            self.configure(configpath=configpath)

        fw = not j.sal.process.execute("ufw status 2> /dev/null", die=False)[0]

        port = self.getTCPPort(configpath=configpath)

        # Do if not  "ufw status 2> /dev/null" didn't run properly
        if fw:
            j.builder.security.ufw.allowIncoming(port)

        if j.builder.system.process.tcpport_check(port, ""):
            raise RuntimeError(
                "port %s is occupied, cannot install caddy" % port)

        self._done_set('install')

    def reload(self, configpath="{DIR_CFG}/caddy.cfg"):
        configpath = j.core.tools.text_replace(configpath)
        for item in j.builder.system.process.info_get():
            if item["process"] == "caddy":
                pid = item["pid"]
                j.sal.process.execute("kill -s USR1 %s" % pid)
                return True
        return False

    def configure(self, ssl=False, wwwrootdir="{{DATADIR}}/www/", configpath="{DIR_CFG}/caddy.cfg",
                  logdir="{{LOGDIR}}/caddy/log", email='replaceme', port=8000):
        """
        @param caddyconfigfile
            template args available DATADIR, LOGDIR, WWWROOTDIR, PORT, TMPDIR, EMAIL ... (using mustasche)
        """
        vhosts_dir = j.core.tools.text_replace("{DIR_CFG}/vhosts")
        j.builder.tools.dir_ensure(vhosts_dir)
        C = """
        #tcpport:{{PORT}}
        import {{VHOSTS_DIR}}/*
        """

        configpath = j.core.tools.text_replace(configpath)
        args = {
            "PORT": str(port),
            "VHOSTS_DIR": vhosts_dir
        }
        C = j.core.tools.text_replace(C, args)
        j.sal.fs.writeFile(configpath, C)

    def getTCPPort(self, configpath="{DIR_CFG}/caddy.cfg"):
        configpath = j.core.tools.text_replace(configpath)
        C = j.builder.tools.file_read(configpath)
        for line in C.split("\n"):
            if "#tcpport:" in line:
                return line.split(":")[1].strip()
        raise RuntimeError(
            "Can not find tcpport arg in config file, needs to be '#tcpport:'")

    def start(self, configpath="{DIR_CFG}/caddy.cfg", agree=True, expect="done."):
        """
        @expect is to see if we can find this string in output of caddy starting
        """

        configpath = j.core.tools.text_replace(configpath)

        if not j.builder.tools.exists(configpath):
            raise RuntimeError(
                "could not find caddyconfigfile:%s" % configpath)

        # tcpport = int(self.getTCPPort(configpath=configpath))

        # TODO: *1 reload does not work yet
        # if self.reload(configpath=configpath) == True:
        #     self._logger.info("caddy already started, will reload")
        #     return

        self.stop()  # will also kill

        if j.builder.platformtype.isMac:
            cmd = "caddy"
        else:
            cmd = j.core.tools.text_replace("{DIR_BIN}/caddy")

        if agree:
            agree = " -agree"

        cmd = 'ulimit -n 8192; %s -conf=%s %s' % (cmd, configpath, agree)
        # wait 10 seconds for caddy to generate ssl certificate before returning error
        j.builder.system.processmanager.get().ensure("caddy", cmd, wait=10, expect=expect)

    def stop(self):
        j.builder.system.processmanager.get().stop("caddy")

    def add_website(self, name, cfg, configpath="{DIR_CFG}/caddy.cfg"):
        file_contents = j.builder.tools.file_read(configpath)
        vhosts_dir = j.core.tools.text_replace("{DIR_CFG}/vhosts")
        if vhosts_dir not in file_contents:
            file_contents = "import {}/*\n".format(vhosts_dir) + file_contents
        j.sal.fs.writeFile(configpath, file_contents)
        j.builder.tools.dir_ensure(vhosts_dir)
        cfg_path = "{}/{}.conf".format(vhosts_dir, name)
        j.sal.fs.writeFile(cfg_path, cfg)
        self.stop()
        self.start()
