from Jumpscale import j
from .Capacity import Capacity

JSBASE = j.application.JSBaseClass


class Ubuntu(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.sal.ubuntu"
        JSBASE.__init__(self)
        self._aptupdated = False
        self._checked = False
        self._cache_ubuntu = None
        self.installedpackage_names = []
        self._local = j.tools.executorLocal
        self.capacity = Capacity(self)

    def uptime(self):
        """
        return system uptime value.
        :return: uptime value
        :rtype: float
        """
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

    def check(self):
        """
        check if ubuntu or mint (which is based on ubuntu)
        :return: True if system in ubuntu or mint
        :rtype: bool
        :raise: j.exceptions.RuntimeError: is os is not ubuntu nor mint
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
        :return: codename, description, id, release
        :rtype: tuple
        """
        self.check()
        import lsb_release
        result = lsb_release.get_distro_information()
        return result["CODENAME"].lower().strip(), result["DESCRIPTION"], result["ID"].lower().strip(),\
               result["RELEASE"]

    def apt_install_check(self, package_name, cmd_name):
        """
        :param package_name: is name of ubuntu package to install e.g. curl
        :type package_name: str
        :param cmd_name: is cmd to check e.g. curl
        :type cmd_name: str
        
        :raise: j.exceptions.RuntimeError: Could not install package
        """
        self.check()
        rc, out, err = self._local.execute("which %s" % cmd_name, False)
        if rc != 0:
            self.apt_install(package_name)
        
        rc, out, err = self._local.execute("which %s" % cmd_name, False)
        if rc != 0:
            raise j.exceptions.RuntimeError(
                "Could not install package %s and check for command %s." % (package_name, cmd_name))

    def apt_install(self, package_name):
        """
        :param package_name: name of the package
        :type package_name: str

        """
        self.apt_update()
        cmd = 'apt-get install %s --force-yes -y' % package_name
        self._local.execute(cmd)

    def apt_install_version(self, package_name, version):
        """
        Install a specific version of an ubuntu package.

        :param package_name: name of the package
        :type package_name: str

        :param version: version of the package
        :type version: str
        """

        self.check()
        if self._cache_ubuntu is None:
            self.apt_init()

        main_package = self._cache_ubuntu[package_name]
        version_package = main_package.versions[version].package

        if not version_package.is_installed:
            version_package.mark_install()

        self._cache_ubuntu.commit()
        self._cache_ubuntu.clear()

    def deb_install(self, path, install_deps=True):
        """
        Install a debian package

        :param path: debian package path
        :type path: str
        :param install_deps: install debian package's dependencies
        :type install_deps: bool 
        """
        self.check()
        if self._cache_ubuntu is None:
            self.apt_init()
        import apt.debfile
        deb = apt.debfile.DebPackage(path, cache=self._cache_ubuntu)
        if install_deps:
            deb.check()
            for missing_pkg in deb.missing_deps:
                self.apt_install(missing_pkg)
        deb.install()

    def deb_download_install(self, url, remove_downloaded=False):
        """
        download to tmp if not there yet, then install it

        :param url: debian package  url
        :rtype: str
        :param remove_downloaded: remove tmp download file
        :rtype: bool
        """
        j.sal.fs.changeDir(j.dirs.TMPDIR)  # will go to tmp
        path = j.sal.nettools.download(url, "")
        self.deb_install(path)
        if remove_downloaded:
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

    def pkg_remove(self, package_name):
        self._logger.info("ubuntu remove package:%s" % package_name)
        self.check()
        if self._cache_ubuntu is None:
            self.apt_init()
        pkg = self._cache_ubuntu[package_name]
        if pkg.is_installed:
            pkg.mark_delete()
        if package_name in self.installedpackage_names:
            self.installedpackage_names.pop(self.installedpackage_names.index(package_name))
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

    def apt_find_all(self, package_name):
        package_name = package_name.lower().strip().replace("_", "").replace("_", "")
        if self._cache_ubuntu is None:
            self.apt_init()
        result = []
        for item in self._cache_ubuntu.keys():
            item2 = item.replace("_", "").replace("_", "").lower()
            if item2.find(package_name) != -1:
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

    def apt_find_installed(self, package_name):
        package_name = package_name.lower().strip().replace("_", "").replace("_", "")
        if self._cache_ubuntu is None:
            self.apt_init()
        result = []
        for item in self.get_installed_package_names():
            item2 = item.replace("_", "").replace("_", "").lower()
            if item2.find(package_name) != -1:
                result.append(item)
        return result

    def apt_find1_installed(self, package_name):
        self._logger.info("find 1 package in ubuntu")
        res = self.apt_find_installed(package_name)
        if len(res) == 1:
            return res[0]
        elif len(res) > 1:
            raise j.exceptions.RuntimeError("Found more than 1 package for %s" % package_name)
        raise j.exceptions.RuntimeError("Could not find package %s" % package_name)

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
