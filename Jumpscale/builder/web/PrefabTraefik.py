from Jumpscale import j





class BuilderTraefik(j.builder.system._BaseClass):
    NAME = "traefik"

    def _init(self):
        self.BUILDDIR_ = j.core.tools.text_replace("{DIR_VAR}/build/traefik")

    def reset(self):
        self.stop()
        app.reset(self)
        self._init()
        j.builder.tools.dir_remove(self.BUILDDIR_)
        j.builder.tools.dir_remove("{DIR_BIN}/traefik")

    def install(self, plugins=None, reset=False, configpath="{DIR_CFG}/traefik.cfg"):
        """
        will build if required & then install binary on right location
        """

        raise RuntimeError("not implemented yet, now copy from caddy")

        if self._done_get('install') and reset is False and self.isInstalled():
            return

        j.builder.sandbox.profileDefault.addPath('{DIR_BIN}')
        j.builder.sandbox.profileDefault.save()

        configpath = j.core.tools.text_replace(configpath)

        if not j.builder.tools.exists(configpath):
            # default configuration, can overwrite
            self.configure(configpath=configpath)

        port = self.getTCPPort(configpath=configpath)

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
                  logdir="{{LOGDIR}}/caddy/log", email='info@threefold.tech', port=8000):
        """
        @param caddyconfigfile
            template args available DATADIR, LOGDIR, WWWROOTDIR, PORT, TMPDIR, EMAIL ... (using mustasche)
        """

        C = """
        #tcpport:{{PORT}}
        :{{PORT}}
        gzip
        log {{LOGDIR}}/access.log
        errors {
            * {{LOGDIR}}/errors.log
        }
        root {{WWWROOTDIR}}
        """

        configpath = j.core.tools.text_replace(configpath)

        args = {}
        args["WWWROOTDIR"] = j.core.tools.text_replace(wwwrootdir).rstrip("/")
        args["LOGDIR"] = j.core.tools.text_replace(logdir).rstrip("/")
        args["PORT"] = str(port)
        args["EMAIL"] = email
        args["CONFIGPATH"] = configpath

        C = j.core.tools.text_replace(C, args)

        j.core.tools.dir_ensure(args["LOGDIR"])
        j.core.tools.dir_ensure(args["WWWROOTDIR"])

        j.sal.fs.writeFile(configpath, C)

    def getTCPPort(self, configpath="{DIR_CFG}/caddy.cfg"):
        configpath = j.core.tools.text_replace(configpath)
        C = j.core.tools.file_text_read(configpath)
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

        if not j.sal.fs.exists(configpath, followlinks=True):
            raise RuntimeError(
                "could not find caddyconfigfile:%s" % configpath)

        tcpport = int(self.getTCPPort(configpath=configpath))

        # TODO: *1 reload does not work yet
        # if self.reload(configpath=configpath) == True:
        #     self._logger.info("caddy already started, will reload")
        #     return
        pm = j.builder.system.processmanager.get()
        pm.stop("caddy")  # will also kill

        cmd = j.builder.sandbox.cmdGetPath("caddy")
        if agree:
            agree = " -agree"

        print (cmd)

        # j.builder.system.processmanager.ensure(
        #     "caddy", 'ulimit -n 8192; %s -conf=%s -email=%s %s' % (cmd, args["CONFIGPATH"], args["EMAIL"], agree), wait=1)
        pm.ensure(
            "caddy", 'ulimit -n 8192; %s -conf=%s %s' % (cmd, configpath, agree), wait=1, expect=expect)

    def stop(self):
        pm = j.builder.system.processmanager.get()
        pm.stop("caddy")
