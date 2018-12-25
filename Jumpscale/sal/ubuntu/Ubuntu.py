from Jumpscale import j

# from .Capacity import Capacity

JSBASE = j.application.JSBaseClass


class Ubuntu(j.application.JSBaseClass):

    def __init__(self):
        self.__jslocation__ = "j.sal.ubuntu"
        JSBASE.__init__(self)
        self._aptupdated = False
        self._checked = False
        self._cache_ubuntu = None
        self.installedPackageNames = []
        self._local = j.tools.executorLocal
        # self.capacity = Capacity(self)

    def uptime(self):
        with open('/proc/uptime') as f:
            data = f.read()
            uptime, _ = data.split(' ')
            return float(uptime)

    def apt_init(self):
        try:
            import apt
        except ImportError:
            # we dont wont jshell to break, self.check will take of this
            return
        apt.apt_pkg.init()
        if hasattr(apt.apt_pkg, 'Config'):
            cfg = apt.apt_pkg.Config
        else:
            cfg = apt.apt_pkg.Configuration
        try:
            cfg.set("APT::Install-Recommends", "0")
            cfg.set("APT::Install-Suggests", "0")
        except BaseException:
            pass
        self._cache_ubuntu = apt.Cache()
        self.aptCache = self._cache_ubuntu
        self.apt = apt

    def check(self, die=True):
        """
        check if ubuntu or mint (which is based on ubuntu)
        """
        if not self._checked:
            osname = j.core.platformtype.myplatform.osname
            osversion = j.core.platformtype.myplatform.osversion
            if osname not in ('ubuntu', 'linuxmint'):
                raise j.exceptions.RuntimeError("Only Ubuntu/Mint supported")
            # safe cast to the release to a number
            else:
                release = float(osversion)
                if release < 14:
                    raise j.exceptions.RuntimeError("Only ubuntu version 14+ supported")
                self._checked = True

        return self._checked

    def version_get(self):
        """
        returns codename,descr,id,release
        known ids" raring, linuxmint
        """
        self.check()
        import lsb_release
        result = lsb_release.get_distro_information()
        return result["CODENAME"].lower().strip(), result["DESCRIPTION"], result[
            "ID"].lower().strip(), result["RELEASE"],

    def apt_install_check(self, packagenames, cmdname):
        """
        @param packagenames is name or array of names of ubuntu package to install e.g. curl
        @param cmdname is cmd to check e.g. curl
        """
        self.check()
        if j.data.types.list.check(packagenames):
            for packagename in packagenames:
                self.apt_install_check(packagename, cmdname)
        else:
            packagename = packagenames
            rc, out, err = self._local.execute("which %s" % cmdname, False)
            if rc != 0:
                self.apt_install(packagename)
            else:
                return
            rc, out, err = self._local.execute("which %s" % cmdname, False)
            if rc != 0:
                raise j.exceptions.RuntimeError(
                    "Could not install package %s and check for command %s." % (packagename, cmdname))

    def apt_install(self, packagename, update_md=True):
        """Install a package in the system
        
        Arguments:
            packagename {[string]} -- [name of the package ot install, can be a space separated list of of names]
        
        Keyword Arguments:
            update_md {bool} -- [if True, an apt update will be executed before 
            installing the package] (default: {True})
        """
        if update_md:
            self.apt_update()
        cmd = 'apt-get install %s --force-yes -y' % packagename
        self._local.execute(cmd)

    def apt_install_version(self, packageName, version):
        '''
        Installs a specific version of an ubuntu package.

        @param packageName: name of the package
        @type packageName: str

        @param version: version of the package
        @type version: str
        '''

        self.check()
        if self._cache_ubuntu is None:
            self.apt_init()

        mainPackage = self._cache_ubuntu[packageName]
        versionPackage = mainPackage.versions[version].package

        if not versionPackage.is_installed:
            versionPackage.mark_install()

        self._cache_ubuntu.commit()
        self._cache_ubuntu.clear()

    def deb_install(self, path, installDeps=True):
        self.check()
        if self._cache_ubuntu is None:
            self.apt_init()
        import apt.debfile
        deb = apt.debfile.DebPackage(path, cache=self._cache_ubuntu)
        if installDeps:
            deb.check()
            for missingpkg in deb.missing_deps:
                self.apt_install(missingpkg)
        deb.install()

    def deb_download_install(self, url, removeDownloaded=False, minspeed=20):
        """
        will download to tmp if not there yet
        will then install
        """
        j.sal.fs.changeDir(j.dirs.TMPDIR)  # will go to tmp
        path = j.sal.nettools.download(url, "")
        self.deb_install(path)
        if removeDownloaded:
            j.tools.path.get(path).rmtree_p()

    def pkg_list(self, pkgname, regex=""):
        """
        list files of dpkg
        if regex used only output the ones who are matching regex
        """
        rc, out, err = self._local.execute("dpkg -L %s" % pkgname)
        if regex != "":
            return j.data.regex.findAll(regex, out)
        else:
            return out.split("\n")

    def pkg_remove(self, packagename):
        self._logger.info("ubuntu remove package:%s" % packagename)
        self.check()
        if self._cache_ubuntu is None:
            self.apt_init()
        pkg = self._cache_ubuntu[packagename]
        if pkg.is_installed:
            pkg.mark_delete()
        if packagename in self.installedPackageNames:
            self.installedPackageNames.pop(self.installedPackageNames.index(packagename))
        self._cache_ubuntu.commit()
        self._cache_ubuntu.clear()

    def service_install(self, servicename, daemonpath, args='', respawn=True, pwd=None, env=None, reload=True):
        C = """
start on runlevel [2345]
stop on runlevel [016]
"""
        if respawn:
            C += "respawn\n"
        if pwd:
            C += "chdir %s\n" % pwd
        if env is not None:
            for key, value in list(env.items()):
                C += "env %s=%s\n" % (key, value)
        C += "exec %s %s\n" % (daemonpath, args)

        C = j.dirs.replace_txt_dir_vars(C)

        j.tools.path.get("/etc/init/%s.conf" % servicename).write_text(C)
        if reload:
            self._local.execute("initctl reload-configuration")

    def service_uninstall(self, servicename):
        self.service_stop(servicename)
        j.tools.path.get("/etc/init/%s.conf" % servicename).remove_p()

    def service_start(self, servicename):
        self._logger.debug("start service on ubuntu for:%s" % servicename)
        if not self.service_status(servicename):
            cmd = "sudo start %s" % servicename
            return self._local.execute(cmd)

    def service_stop(self, servicename):
        cmd = "sudo stop %s" % servicename
        return self._local.execute(cmd, False)

    def service_restart(self, servicename):
        return self._local.execute("sudo restart %s" % servicename, False)

    def service_status(self, servicename):
        exitcode, output = self._local.execute("sudo status %s" % servicename, False)
        parts = output.split(' ')
        if len(parts) >= 2 and parts[1].startswith('start'):
            return True

        return False

    def service_disable_start_boot(self, servicename):
        self._local.execute("update-rc.d -f %s remove" % servicename)

    def service_enable_start_boot(self, servicename):
        self._local.execute("update-rc.d -f %s defaults" % servicename)

    def apt_update(self, force=True):
        self.check()
        if self._cache_ubuntu is None:
            self.apt_init()
        if self._cache_ubuntu:
            self._cache_ubuntu.update()
        else:
            self._local.execute("apt-get update", False)

    def apt_upgrade(self, force=True):
        self.check()
        if self._cache_ubuntu is None:
            self.apt_init()
        self.apt_update()
        self._cache_ubuntu.upgrade()

    def apt_get_cache_keys(self):
        return list(self._cache_ubuntu.keys())

    def apt_get_installed(self):
        return self.get_installed_package_names()

    def apt_get(self, name):
        return self._cache_ubuntu[name]

    def apt_find_all(self, packagename):
        packagename = packagename.lower().strip().replace("_", "").replace("_", "")
        if self._cache_ubuntu is None:
            self.apt_init()
        result = []
        for item in self._cache_ubuntu.keys():
            item2 = item.replace("_", "").replace("_", "").lower()
            if item2.find(packagename) != -1:
                result.append(item)
        return result

    def get_installed_package_names(self):
        if self._cache_ubuntu is None:
            self.apt_init()
        if self._installed_pkgs is None:
            self._installed_pkgs = []
            for p in self._cache_ubuntu:
                if p.is_installed:
                    self._installed_pkgs.append(p.name)

        return self._installed_pkgs

    def is_pkg_installed(self, pkg):
        return pkg in self._installed_pkgs

    def apt_find_installed(self, packagename):
        packagename = packagename.lower().strip().replace("_", "").replace("_", "")
        if self._cache_ubuntu is None:
            self.apt_init()
        result = []
        for item in self.get_installed_package_names():
            item2 = item.replace("_", "").replace("_", "").lower()
            if item2.find(packagename) != -1:
                result.append(item)
        return result

    def apt_find1_installed(self, packagename):
        self._logger.info("find 1 package in ubuntu")
        res = self.apt_find_installed(packagename)
        if len(res) == 1:
            return res[0]
        elif len(res) > 1:
            raise j.exceptions.RuntimeError("Found more than 1 package for %s" % packagename)
        raise j.exceptions.RuntimeError("Could not find package %s" % packagename)

    def apt_sources_list(self):
        from aptsources import sourceslist
        return sourceslist.SourcesList()

    def apt_sources_uri_change(self, newuri):
        src = self.apt_sources_list()
        for entry in src.list:
            entry.uri = newuri
        src.save()

    def apt_sources_uri_add(self, url):
        url = url.replace(";", ":")
        name = url.replace("\\", "/").replace("http://", "").replace("https://", "").split("/")[0]
        path = j.tools.path.get("/etc/apt/sources.list.d/%s.list" % name)
        path.write_text("deb %s\n" % url)

    def whoami(self):
        rc, out, err = self._local.execute("whoami")
        return out.strip()

    def checkroot(self):
        if self.whoami() != "root":
            raise j.exceptions.Input("only support root")

    def sshkeys_generate(self, passphrase='', type="rsa", overwrite=False, path="/root/.ssh/id_rsa"):
        path = j.tools.path.get(path)
        if overwrite and path.exists():
            path.rmtree_p()
        if not path.exists():
            if type not in ['rsa', 'dsa']:
                raise j.exceptions.Input("only support rsa or dsa for now")
            cmd = "ssh-keygen -t %s -b 4096 -P '%s' -f %s" % (type, passphrase, path)
            self._local.execute(cmd)

    @property
    def version(self):
        # use command, don't bypass it by going directly to /etc/lsb-release
        cmd = "lsb_release -r"
        rc, out, err = self._local.execute(cmd)
        return (out.split(":")[-1]).strip()
