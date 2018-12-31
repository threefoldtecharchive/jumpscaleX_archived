from Jumpscale import j


class BuilderSystemPackage(j.builder.system._BaseClass):


    def __init(self):
        self._logger_enable()

    def _repository_ensure_apt(self, repository):
        self.ensure('python-software-properties')
        j.sal.process.execute("add-apt-repository --yes " + repository)

    def _apt_wait_free(self):
        timeout = time.time() + 300
        while time.time() < timeout:
            _, out, _ = j.sal.process.execute(
                'fuser /var/lib/dpkg/lock', showout=False, die=False)
            if out.strip():
                time.sleep(1)
            else:
                return
        raise TimeoutError("resource dpkg is busy")

    def _apt_get(self, cmd):

        cmd = CMD_APT_GET + cmd
        result = j.sal.process.execute(cmd)
        # If the installation process was interrupted, we might get the following message
        # E: dpkg was interrupted, you must manually j.sal.process.execute 'run
        # dpkg --configure -a' to correct the problem.
        if "run dpkg --configure -a" in result:
            j.sal.process.execute(
                "DEBIAN_FRONTEND=noninteractive dpkg --configure -a")
            result = j.sal.process.execute(cmd)
        return result

    # def upgrade(self, package=None, reset=True):
    #     key = "upgrade_%s" % package
    #     if self._done_check(key, reset):
    #         return
    #     if j.core.platformtype.myplatform.isUbuntu:
    #         if package is None:
    #             return self._apt_get("-q --yes update")
    #         else:
    #             if type(package) in (list, tuple):
    #                 package = " ".join(package)
    #             return self._apt_get(' upgrade ' + package)
    #     elif j.builder.tools.isAlpine:
    #         j.builder.tools.run("apk update")
    #         j.builder.tools.run("apk upgrade")
    #     else:
    #         raise j.exceptions.RuntimeError(
    #             "could not install:%s, platform not supported" % package)
    #     self._done_set(key)

    def mdupdate(self, reset=False):
        """
        update metadata of system
        """
        if self._done_check("mdupdate", reset):
            return
        self._logger.info("packages mdupdate")
        if j.core.platformtype.myplatform.isUbuntu:
            j.sal.process.execute("apt-get update")
        elif j.builder.tools.isAlpine:
            j.builder.tools.run("apk update")
        elif j.core.platformtype.myplatform.isMac:
            location = j.builder.tools.command_location("brew")
            # j.sal.process.execute("run chown root %s" % location)
            j.sal.process.execute("brew update")
        elif j.builder.tools.isArch:
            j.sal.process.execute("pacman -Syy")
        self._done_set("mdupdate")

    def upgrade(self, distupgrade=False, reset=False):
        """
        upgrades system, distupgrade means ubuntu 14.04 will fo to e.g. 15.04
        """
        if self._done_check("upgrade", reset):
            return
        self.mdupdate()
        self._logger.info("packages upgrade")
        if j.core.platformtype.myplatform.isUbuntu:
            if distupgrade:
                raise NotImplementedError()
                # return self._apt_get("dist-upgrade")
            else:
                self._apt_get("upgrade -y")
        # elif j.builder.tools.isArch:
        #     j.sal.process.execute(
        #         "pacman -Syu --noconfirm;pacman -Sc --noconfirm")
        elif j.core.platformtype.myplatform.isMac:
            j.sal.process.execute("brew upgrade")
        elif j.builder.tools.isAlpine:
            j.builder.tools.run("apk update")
            j.builder.tools.run("apk upgrade")
        elif j.builder.tools.isCygwin:
            return  # no such functionality in apt-cyg
        else:
            raise j.exceptions.RuntimeError(
                "could not upgrade, platform not supported")
        self._done_set("upgrade")

    def install(self, package, reset=False):
        """
        """

        # bring to list of packages
        if j.data.types.list.check(package) == False and package.find(",") != -1:
            package = [item.strip() for item in package.split(",")]
        elif j.data.types.list.check(package) == False and package.find("\n") != -1:
            package = [item.strip() for item in package.split("\n")]
        elif not j.data.types.list.check(package):
            package = [package]

        packages = [item for item in package if item.strip() != ""]

        cmd = "set -ex\n"

        todo = []
        for package in packages:

            key = "install_%s" % package
            if self._done_check(key, reset):
                self._logger.info("package:%s already installed"%package)
                continue
            todo.append(package)
            print("+ install: %s" % package)

            self._logger.info("prepare to install:%s" % package)

            if j.core.platformtype.myplatform.isUbuntu:
                cmd += "%s install %s\n" % (CMD_APT_GET, package)

            elif j.builder.tools.isAlpine:
                cmd = "apk add %s \n" % package

            elif j.builder.tools.isArch:
                if package.startswith("python3"):
                    package = "extra/python"

                # ignore
                for unsupported in ["libpython3.5-dev", "libffi-dev", "build-essential", "libpq-dev", "libsqlite3-dev"]:
                    if unsupported in package:
                        package = 'devel'

                cmd = "pacman -S %s  --noconfirm\n" % package

            elif j.core.platformtype.myplatform.isMac:
                for unsupported in ["libpython3.4-dev", "python3.4-dev", "libpython3.5-dev", "python3.5-dev",
                                    "libffi-dev", "libssl-dev", "make", "build-essential", "libpq-dev", "libsqlite3-dev"]:
                    if 'libsnappy-dev' in package or 'libsnappy1v5' in package:
                        package = 'snappy'

                    if unsupported in package:
                        continue

                # rc,out=j.sal.process.execute("brew info --json=v1 %s"%package,showout=False,die=False)
                # if rc==0:
                #     info=j.data.serializers.json.loads(out)
                #     return #means was installed

                if "wget" == package:
                    package = "%s --enable-iri" % package

                cmd += "brew install %s || brew upgrade  %s\n" % (package, package)

            elif j.builder.tools.isCygwin:
                if package in ["run", "net-tools"]:
                    return

                installed = j.sal.process.execute(
                    "apt-cyg list&")[1].splitlines()
                if package in installed:
                    return  # means was installed

                cmd = "apt-cyg install %s\n" % package
            else:
                raise j.exceptions.RuntimeError(
                    "could not install:%s, platform not supported" % package)

            # mdupdate = False
            # while True:
            #     rc, out, err = j.sal.process.execute(cmd, die=False)

            #     if rc > 0:
            #         if mdupdate is True:
            #             raise j.exceptions.RuntimeError(
            #                 "Could not install:'%s' \n%s" % (package, out))

            #         if out.find("not found") != -1 or out.find("failed to retrieve some files") != -1:
            #             self.mdupdate()
            #             mdupdate = True
            #             continue
            #         raise j.exceptions.RuntimeError(
            #             "Could not install:%s %s" % (package, err))
            #     if rc == 0:
            #         self._done_set(key)
            #         return out

        if len(todo) > 0:
            print(cmd)
            j.builder.tools.run(cmd)

        for package in todo:
            key = "install_%s," % package
            self._done_set(key)

    # def multiInstall(self, packagelist, allow_unauthenticated=False, reset=False):
    #     """
    #     @param packagelist is text file and each line is name of package
    #     can also be list

    #     e.g.
    #         # python
    #         mongodb

    #     @param runid, if specified actions will be used to execute
    #     """
    #     # previous_run = j.sal.process.executemode
    #     # try:
    #     #     j.sal.process.executemode = True

    #     if j.data.types.string.check(packagelist):
    #         packages = packagelist.strip().splitlines()
    #     elif j.data.types.list.check(packagelist):
    #         packages = packagelist
    #     else:
    #         raise j.exceptions.Input(
    #             'packagelist should be string or a list. received a %s' % type(packagelist))

    #     to_install = []
    #     for dep in packages:
    #         dep = dep.strip()
    #         if dep is None or dep == "" or dep[0] == '#':
    #             continue
    #         to_install.append(dep)

    #     for package in to_install:
    #         self.install(
    #             package, allow_unauthenticated=allow_unauthenticated, reset=reset)

    def start(self, package):
        if j.builder.tools.isArch or j.core.platformtype.myplatform.isUbuntu or j.core.platformtype.myplatform.isMac:
            pm = j.builder.system.processmanager.get()
            pm.ensure(package)
        else:
            raise j.exceptions.RuntimeError(
                "could not install/ensure:%s, platform not supported" % package)

    def ensure(self, package, update=False):
        """Ensure apt packages are installed"""
        if j.core.platformtype.myplatform.isUbuntu:
            if isinstance(package, str):
                package = package.split()
            res = {}
            for p in package:
                p = p.strip()
                if not p:
                    continue
                # The most reliable way to detect success is to use the command status
                # and suffix it with OK. This won't break with other locales.
                rc, out, err = j.sal.process.execute(
                    "dpkg -s %s && echo **OK**;true" % p)
                if "is not installed" in err:
                    self.install(p)
                    res[p] = False
                else:
                    if update:
                        self.mdupdate(p)
                    res[p] = True
            if len(res) == 1:
                for _, value in res.items():
                    return value
            else:
                return res
        elif j.builder.tools.isArch:
            j.sal.process.execute("pacman -S %s" % package)
            return
        elif j.core.platformtype.myplatform.isMac:
            self.install(package)
            return
        else:
            raise j.exceptions.RuntimeError(
                "could not install/ensure:%s, platform not supported" % package)

        raise j.exceptions.RuntimeError("not supported platform")

    def clean(self, package=None, agressive=False):
        """
        clean packaging system e.g. remove outdated packages & caching packages
        @param agressive if True will delete full cache

        """
        if j.core.platformtype.myplatform.isUbuntu:

            if package is not None:
                return self._apt_get("-y --purge remove %s" % package)
            else:
                j.sal.process.execute("apt-get autoremove -y")

            self._apt_get("autoclean")
            C = """
            apt-get clean
            rm -rf /bd_build
            rm -rf /var/tmp/*
            rm -f /etc/dpkg/dpkg.cfg.d/02apt-speedup

            find -regex '.*__pycache__.*' -delete
            rm -rf /var/log
            mkdir -p /var/log/apt
            rm -rf /var/tmp
            mkdir -p /var/tmp

            """
            j.sal.process.execute(C)

        # elif j.builder.tools.isArch:
        #     cmd = "pacman -Sc"
        #     if agressive:
        #         cmd += "c"
        #     j.sal.process.execute(cmd)
        #     if agressive:
        #         j.sal.process.execute("pacman -Qdttq", showout=False)

        elif j.core.platformtype.myplatform.isMac:
            if package:
                j.sal.process.execute("brew cleanup %s" % package)
                j.sal.process.execute("brew remove %s" % package)
            else:
                j.sal.process.execute("brew cleanup")

        elif j.builder.tools.isCygwin:
            if package:
                j.sal.process.execute("apt-cyg remove %s" % package)
            else:
                pass

        else:
            raise j.exceptions.RuntimeError(
                "could not package clean:%s, platform not supported" % package)

    def remove(self, package, autoclean=False):
        if j.core.platformtype.myplatform.isUbuntu:
            self._apt_get('remove ' + package)
            if autoclean:
                self._apt_get("autoclean")
        elif j.core.platformtype.myplatform.isMac:
            j.sal.process.execute("brew remove %s 2>&1 > /dev/null|echo """ % package)

