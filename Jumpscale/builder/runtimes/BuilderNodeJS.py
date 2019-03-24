from Jumpscale import j




class BuilderNodeJS(j.builder.system._BaseClass):
    NAME = 'nodejs'

    def _init(self):
        self._bowerDir = ""

    @property
    def npm(self):
        return j.core.tools.text_replace('{DIR_BASE}/node/bin/npm')

    @property
    def NODE_PATH(self):
        return j.core.tools.text_replace('{DIR_BASE}/node/lib/node_modules')

    def bowerInstall(self, name):
        """
        @param name can be a list or string
        """
        if self._bowerDir == "":
            self.install()
            j.core.tools.dir_ensure("{DIR_TEMP}/bower")
            self._bowerDir = j.core.tools.text_replace("{DIR_TEMP}/bower")
        if j.data.types.list.check(name):
            for item in name:
                self.bowerInstall(item)
        else:
            self._log_info("bower install %s" % name)
            j.sal.process.execute(
                "cd %s;bower --allow-root install  %s" % (self._bowerDir, name), profile=True)

    def isInstalled(self):
        rc, out, err = j.sal.process.execute(
            "npm version", die=False, showout=False)
        if rc > 0:
            return False
        installedDict = j.data.serializers.yaml.loads(out)
        if "npm" not in installedDict or "node" not in installedDict:
            return False
        if j.core.text.strToVersionInt(installedDict["npm"]) < 5000000:
            self._log_info("npm too low version, need to install.")
            return False
        if j.core.text.strToVersionInt(installedDict["node"]) < 7000000:
            self._log_info("node too low version, need to install.")
            return False

        if self._done_get("install") is False:
            return False
        return True

    def phantomjs(self, reset=False):
        """
        headless browser used for automation
        """
        if self._done_get("phantomjs") and reset is False:
            return
        if j.core.platformtype.myplatform.isUbuntu:

            url = 'https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2'
            cdest = j.builder.tools.file_download(
                url, expand=True, overwrite=False, to="{DIR_TEMP}/phantomjs", removeTopDir=True, deletedest=True)

            j.builder.tools.run("mv %s/bin/phantomjs /opt/bin/phantomjs" % cdest)
            j.builder.tools.run("rm -rf %s" % cdest)

            j.builder.tools.package_install("libfontconfig")

        elif j.core.platformtype.myplatform.isMac:
            j.builder.tools.package_install("phantomjs")

        else:
            raise RuntimeError("phantomjs only supported don ubuntu or osx")

        self._done_set("phantomjs")

    def npm_install(self, name, global_=True, reset=False):
        """
        @PARAM cmdname is the optional cmd name which will be used to put in path of the env (as alias to the name)
        """
        self._log_info("npm install:%s" % name)
        key = "npm_%s" % name
        if self._done_get(key) and not reset:
            return

        if global_:
            if j.core.platformtype.myplatform.isMac:
                sudo = "sudo "
            else:
                sudo = ""
            cmd = "cd /tmp;%snpm install -g %s --unsafe-perm=true --allow-root" % (sudo, name)
        else:
            cmd = "cd %s;npm i %s" % (self.NODE_PATH, name)

        j.sal.process.execute(cmd)

        # cmdpath = "%s/nodejs_modules/node_modules/%s/bin/%s" % (
        #     j.dirs.VARDIR, name, name)

        # from IPython import embed
        # embed(colors='Linux')

        # if j.sal.fs.exists(srcCmd):
        #     j.sal.fs.chmod(srcCmd, 0o770)
        #     j.sal.fs.symlink(srcCmd, "/usr/local/bin/%s" %
        #                      name, overwriteTarget=True)
        #     j.sal.fs.chmod(srcCmd, 0o770)

        # if j.sal.fs.exists(cmdpath):
        #     j.sal.fs.symlink(cmdpath, "/usr/local/bin/%s" %
        #                      name, overwriteTarget=True)

        self._done_set(key)

    def install(self, reset=False):
        """
        """
        if self.isInstalled() and not reset:
            return

        j.builder.tools.file_unlink("{DIR_BIN}/node")
        j.builder.tools.dir_remove("{DIR_BASE}/apps/npm")

        # version = "7.7.1"
        version = "8.4.0"

        if reset is False and j.builder.tools.file_exists('{DIR_BIN}/npm'):
            return

        if j.core.platformtype.myplatform.isMac:
            url = 'https://nodejs.org/dist/v%s/node-v%s-darwin-x64.tar.gz' % (
                version, version)
        elif j.core.platformtype.myplatform.isUbuntu:
            url = 'https://nodejs.org/dist/v%s/node-v%s-linux-x64.tar.gz' % (
                version, version)

        else:
            raise j.exceptions.Input(message="only support ubuntu & mac")

        cdest = j.builder.tools.file_download(
            url, expand=True, overwrite=False, to="{DIR_TEMP}/node")

        j.builder.tools.run("rm -rf {DIR_BASE}/node;mv %s {DIR_BASE}/node" % (cdest))

        # if j.core.platformtype.myplatform.isMac:
        #     j.builder.tools.run('mv {DIR_BASE}/node/%s/* {DIR_BASE}/node' %
        #                   j.sal.fs.getBaseName(url.strip('.tar.gz')))


        rc, out, err = j.sal.process.execute("npm -v", profile=True)
        if out != '5.3.0':  # 4.1.2
            # needs to be this version because is part of the package which was downloaded
            # j.sal.process.execute("npm install npm@4.1.2 -g", profile=True)
            raise RuntimeError("npm version error")

        rc, initmodulepath, err = j.sal.process.execute(
            "npm config get init-module", profile=True)
        j.builder.tools.file_unlink(initmodulepath)
        j.sal.process.execute("npm config set global true -g", profile=True)
        j.sal.process.execute(j.core.tools.text_replace(
            "npm config set init-module {DIR_BASE}/node/.npm-init.js -g"), profile=True)
        j.sal.process.execute(j.core.tools.text_replace(
            "npm config set init-cache {DIR_BASE}/node/.npm -g"), profile=True)
        j.sal.process.execute("npm config set global true ", profile=True)
        j.sal.process.execute(j.core.tools.text_replace(
            "npm config set init-module {DIR_BASE}/node/.npm-init.js "), profile=True)
        j.sal.process.execute(j.core.tools.text_replace(
            "npm config set init-cache {DIR_BASE}/node/.npm "), profile=True)
        j.sal.process.execute("npm install -g bower", profile=True, shell=True)

        # j.sal.process.execute("npm install npm@latest -g", profile=True)

        self._done_set("install")
