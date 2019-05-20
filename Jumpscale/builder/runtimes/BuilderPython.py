from Jumpscale import j

builder_method = j.builder.system.builder_method


class BuilderPython(j.builder.system._BaseClass):
    def _init(self):

        self.DIR_BUILD = j.core.tools.text_replace("{DIR_VAR}/build/python3")
        j.sal.fs.createDir(self.DIR_BUILD)

        self.DIR_CODE_L = j.core.tools.text_replace("{DIR_VAR}/build/code/python3")
        j.sal.fs.createDir(self.DIR_CODE_L)

        if not j.core.platformtype.myplatform.isMac:
            self.PATH_OPENSSL = j.core.tools.text_replace("{DIR_VAR}/build/openssl")
        else:
            rc, out, err = j.sal.process.execute("brew --prefix openssl")
            self.PATH_OPENSSL = out.strip()

        self.DIR_SANDBOX = j.core.tools.text_replace("{DIR_VAR}/build/sandbox_python/")
        j.sal.fs.createDir(self.DIR_SANDBOX)

    @builder_method()
    def clean(self):
        self._remove("{DIR_BUILD}")
        self._remove(self.DIR_CODE_L)
        self._remove(self.DIR_SANDBOX)

        C = """
        set -ex
        rm -rf {DIR_CODE_L}/cpython
        """
        self._execute(C)

    @builder_method()
    def reset(self):
        super().reset()
        self.clean()

    @builder_method()
    def build(self, tag="v3.6.7"):  # default "v3.6.7" else may cause locals problem
        """
        kosmos 'j.builder.runtimes.python.build()'
            kosmos 'j.builder.runtimes.python.build(reset=True)'

        will build python and install all pip's inside the build directory

        :param reset: choose to reset the build process even if it was done before
        :type reset: bool
        :param tag: the python version tag (possible tags: 3.7.1, 3.6.7)
        :type tag: str
        :return:
        """
        self.profile_home_select()

        if self.tools.dir_exists(self._replace("{DIR_CODE_L}/cpython")):
            current_tag = self._execute(
                """
                    cd {}/cpython
                    git tag
                    """.format(
                    self.DIR_CODE_L
                )
            )[1]
            if current_tag.replace("\n", "") != tag:
                self._execute("rm -r {}/cpython".format(self.DIR_CODE_L))

        if not self.tools.dir_exists(self._replace("{DIR_CODE_L}/cpython")):
            self._execute(
                """
            cd {}
            git clone --depth 1 --branch {} https://github.com/python/cpython
            """.format(
                    self.DIR_CODE_L, tag
                )
            )

        if j.core.platformtype.myplatform.isMac:
            # clue to get it finally working was in
            # https://stackoverflow.com/questions/46457404/
            # how-can-i-compile-python-3-6-2-on-macos-with-openssl-from-homebrew

            script = """
            set -ex
            cd {DIR_CODE_L}/cpython
            mkdir -p {DIR_BUILD}

            # export CPPFLAGS=-I/opt/X11/include
            # export CFLAGS="-I${PATH_OPENSSL}/include" LDFLAGS="-L${PATH_OPENSSL}/lib"

            ./configure --prefix={DIR_BUILD}/  CPPFLAGS="-I{PATH_OPENSSL}/include" LDFLAGS="-L{PATH_OPENSSL}/lib"

            #if you do the optimizations then it will do all the tests
            # ./configure --prefix={DIR_BUILD}/ --enable-optimizations

            # make -j12

            make -j12 EXTRATESTOPTS=--list-tests install
            """
        else:
            j.builder.libs.openssl.build()
            j.builder.system.package.install(
                [
                    "zlib1g-dev",
                    "libncurses5-dev",
                    "libbz2-dev",
                    "liblzma-dev",
                    "libsqlite3-dev",
                    "libreadline-dev",
                    "libssl-dev",
                    "libsnappy-dev",
                    "wget",
                    "gcc",
                    "make",
                    "cmake",
                    "libjpeg-dev",
                    "zlib1g-dev",
                    "libffi-dev",
                ]
            )
            script = """
            set -ex
            cd {DIR_CODE_L}/cpython
            # THIS WILL MAKE SURE ALL TESTS ARE DONE, WILL TAKE LONG TIME
            ./configure --prefix={DIR_BUILD}/ --enable-optimizations CFLAGS="-I{PATH_OPENSSL}/include -L{PATH_OPENSSL}/lib"

            make clean
            make -j8 EXTRATESTOPTS=--list-tests install
            """

        self._log_info("compiling python3...")

        self._execute(script)
        self.build_pip()

    @builder_method()
    def build_pip(self):
        """
        kosmos 'j.builder.runtimes.python.build_pip()'
        :return:
        """

        # self.build()

        self.profile_builder_select()  # now select builder profile in the builder directory

        # test openssl is working
        cmd = "{DIR_BUILD}/bin/python3 -c 'import ssl'"
        rc, out, err = self._execute(cmd, die=False)
        if rc > 0:
            raise RuntimeError("SSL was not included in building process !\n%s" % err)

        self._pip_install()

        self._pip_packages_all()

    @builder_method()
    def install(self):
        """
        kosmos 'j.builder.runtimes.python.install()'
        """

        self.profile_sandbox_select()

        self.profile_builder_set()

        self._pip_install()

    def profile_builder_set(self):

        self._log_info("build profile builder")

        self.profile.path_add(self._replace("{PATH_OPENSSL}"))

        self.profile.env_set("PYTHONHTTPSVERIFY", 0)

        self.profile.env_set_part("PYTHONPATH", self._replace("{DIR_BUILD}/lib"))
        self.profile.env_set_part("PYTHONPATH", self._replace("{DIR_BUILD}/lib/python3.7"))
        self.profile.env_set_part("PYTHONPATH", self._replace("{DIR_BUILD}/lib/python3.7/site-packages"))

        self.profile.env_set_part("LIBRARY_PATH", self._replace("{PATH_OPENSSL}/lib"))

        self.profile.env_set_part("CPPPATH", self._replace("{DIR_BUILD}/include/python3.7m"))
        self.profile.env_set_part("CPPPATH", self._replace("{PATH_OPENSSL}/include"))

    def profile_sandbox_set(self):

        self.profile.env_set_part("PYTHONPATH", "/sandbox/lib/python.zip")
        self.profile.env_set_part("PYTHONPATH", "/sandbox/lib/python3.7")
        self.profile.env_set_part("PYTHONPATH", "/sandbox/lib/python3.7/site-packages")
        self.profile.env_set_part("PYTHONPATH", "sandbox/lib/python3.7/lib-dynload")

        self.profile.env_set_part("PYTHONPATH", "/sandbox/bin")

        self.profile.env_set_part("LIBRARY_PATH", "/sandbox/bin")
        self.profile.env_set_part("LIBRARY_PATH", "/sandbox/lib")
        self.profile.env_set("LD_LIBRARY_PATH", self.profile.env_get("LIBRARY_PATH"))  # makes copy

        self.profile.env_set("LDFLAGS", "-L'%s'" % self.profile.env_get("LIBRARY_PATH"))

    @builder_method()
    def _pip_install(self):
        """

        kosmos 'j.builder.runtimes.python._pip_install()'

        will make sure we add env scripts to it as well as add all the required pip modules
        """

        script = """
        rm -rf get-pip.py
        curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
        {DIR_BUILD}/bin/python3 get-pip.py
        """
        self._execute(script)  # will automatically use the correct profile

    @builder_method()
    def _pip_packages_all(self):
        """
        kosmos 'j.builder.runtimes.python._pip_packages_all()'
        """

        self.profile_builder_select()

        j.builder.libs.capnp.install()
        # self.pip_package_install(['cython', 'setuptools', 'pycapnp'])  #DOES NOT WORK YET

        # list comes from /sandbox/code/github/threefoldtech/jumpscale_core/install/InstallTools.py
        self.pip_package_install(j.core.installer_base.pips_list(0))

        if not self.tools.isMac:
            # TODO: implement zerostor builder and use it
            # j.builder.zero_os.zos_stor_client.build(python_build=True)  # builds the zos_stor_client
            # self._pip(["g8storclient"])
            pass

        self._log_info("PIP DONE")

    @builder_method()
    def pip_package_install(self, pips):
        pips = j.core.text.getList(pips, "str")
        if len(pips) == 1:
            self._execute(
                "pip3 install --trusted-host pypi.python.org '{PACKAGE}' --upgrade", args={"PACKAGE": pips[0]}
            )
        else:
            for item in pips:
                self.pip_package_install(item)

    @builder_method()
    def pip_package_uninstall(self, package):
        """
        The "package" argument, defines the name of the package that will be ensured.
        """
        self.ensure()
        packages = j.core.text.getList(package, "str")
        if len(packages) == 1:
            return j.sal.process.execute("pip3 uninstall %s" % (packages[0]))
        else:
            for package in packages:
                self.pip_package_uninstall(package)

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        """
        js_shell 'j.builder.runtimes.python.sandbox()'
        :return:
        """
        path = self._replace("{DIR_SANDBOX}/bin/")
        j.tools.sandboxer.libs_sandbox(path, path, True)
        path = j.core.tools.text_replace("{DIR_SANDBOX}/lib/pythonbin/", args=self.__dict__)
        j.tools.sandboxer.libs_sandbox(path, path, True)

    def _copy2sandbox_github(self):
        """

        js_shell 'j.builder.runtimes.python.copy2sandbox_github(reset=False)'


        builds python and returns the build dir

        """

        self._log_info("COPY FILES TO SANDBOX")

        path = self.DIR_BUILD
        self._log_info("sandbox:%s" % path)

        if j.core.platformtype.myplatform.isMac:
            j.builder.system.package.install("redis")
        else:
            j.builder.system.package.install("redis-server")

        if not j.sal.fs.exists("%s/bin/python3.7" % path):
            raise RuntimeError("am not in compiled python dir, need to find %s/bin/python3.7" % path)

        dest = self.DIR_SANDBOX

        # j.sal.fs.remove(dest)
        # j.sal.fs.createDir(dest)

        for item in ["bin", "root", "lib"]:
            j.sal.fs.createDir("%s/%s" % (dest, item))

        for item in ["pip3", "python3.7", "ipython", "bpython", "electrum", "pudb3", "zrobot"]:
            src0 = "%s/bin/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            if j.sal.fs.exists(src0):
                j.sal.fs.copyFile(src0, dest0)

        # for OSX
        for item in ["libpython3.7m.a"]:
            src0 = "%s/lib/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            if j.sal.fs.exists(src0):
                j.sal.fs.copyFile(src0, dest0)

        # LINK THE PYTHON BINARIES
        j.sal.fs.symlink("%s/bin/python3.7" % dest, "%s/bin/python" % dest, overwriteTarget=True)
        j.sal.fs.symlink("%s/bin/python3.7" % dest, "%s/bin/python3" % dest, overwriteTarget=True)

        # NOW DEAL WITH THE PYTHON LIBS

        def dircheck(name):
            for item in ["lib2to3", "idle", ".dist-info", "__pycache__", "site-packages"]:
                if name.find(item) is not -1:
                    return False
            return True

        def binarycheck(path):
            """
            checks if there is a .so in the directory (python libs), if so we need to copy to the binary location
            """
            if "parso" in path:
                return True
            if "jedi" in path:
                return True

            files = j.sal.fs.listFilesInDir(path, recursive=True, filter="*.so", followSymlinks=True)
            files += j.sal.fs.listFilesInDir(path, recursive=True, filter="*.so.*", followSymlinks=True)
            if len(files) > 0:
                self._log_debug("found binary files in:%s" % path)
                return True
            return False

        # ignore files which are not relevant,

        ignoredir = [".egg-info", ".dist-info", "__pycache__", "audio", "tkinter", "audio", "test", "electrum_"]
        ignorefiles = [".egg-info", ".pyc"]

        todo = ["%s/lib/python3.7/site-packages" % path, "%s/lib/python3.7" % path]
        for src in todo:
            for ddir in j.sal.fs.listDirsInDir(
                src, recursive=False, dirNameOnly=True, findDirectorySymlinks=True, followSymlinks=True
            ):
                if dircheck(ddir):
                    src0 = src + "/%s" % ddir
                    if binarycheck(src0):
                        dest0 = "%s/lib/pythonbin/%s" % (dest, ddir)
                    else:
                        dest0 = "%s/lib/python/%s" % (dest, ddir)
                    self._log_debug("copy lib:%s ->%s" % (src0, dest0))
                    j.sal.fs.copyDirTree(
                        src0,
                        dest0,
                        keepsymlinks=False,
                        deletefirst=True,
                        overwriteFiles=True,
                        ignoredir=ignoredir,
                        ignorefiles=ignorefiles,
                        recursive=True,
                        rsyncdelete=True,
                        createdir=True,
                    )

            for item in j.sal.fs.listFilesInDir(src, recursive=False, exclude=ignorefiles, followSymlinks=True):
                fname = j.sal.fs.getBaseName(item)
                dest0 = ""
                if fname.endswith(".so") or ".so." in fname:
                    dest0 = "%s/lib/pythonbin/%s" % (dest, fname)
                if fname.endswith(".py"):
                    dest0 = "%s/lib/python/%s" % (dest, fname)
                self._log_debug("copy %s %s" % (item, dest0))
                if dest0 is not "":
                    j.sal.fs.copyFile(item, dest0)

        # self.env_write(dest)

        remove = ["codecs_jp", "codecs_hk", "codecs_cn", "codecs_kr", "testcapi", "tkinter", "audio"]
        # remove some stuff we don't need
        for item in j.sal.fs.listFilesInDir("%s/lib" % dest, recursive=True):
            if item.endswith(".c") or item.endswith(".h") or item.endswith(".pyc"):
                j.sal.fs.remove(item)
                pass
            for x in remove:
                if item.find(x) is not -1:
                    j.sal.fs.remove(item)
                    pass

        if j.core.platformtype.myplatform.isMac:
            C = """
            mv {DIR_SANDBOX}/lib/python/_sysconfigdata_m_darwin_darwin.py {DIR_SANDBOX}/lib/pythonbin/_sysconfigdata_m_darwin_darwin.py
            rm -rf {DIR_SANDBOX}/lib/python/config-3.6m-darwin

            """
        else:
            C = """
            mv {DIR_SANDBOX}/lib/python/_sysconfigdata_m_linux_x86_64-linux-gnu.py {DIR_SANDBOX}/lib/pythonbin/_sysconfigdata_m_linux_x86_64-linux-gnu.py
            rm -rf {DIR_SANDBOX}/lib/python/config-3.6m-x86_64-linux-gnu

            """

        C = j.core.tools.text_replace(C, args=self.__dict__)
        j.sal.process.execute(C)

        self._log_info("copy to sandbox done")

    def copy2git(self):
        """
        js_shell 'j.builder.runtimes.python.copy2git()'
        :return:
        """

        # copy to sandbox & upload
        ignoredir = [".egg-info", ".dist-info", "__pycache__", "audio", "tkinter", "audio", "test", ".git", "linux-gnu"]
        ignorefiles = [".egg-info", ".pyc", "_64-linux-gnu.py"]

        path = j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_base.git")
        src0 = "%s/lib/python" % self.DIR_SANDBOX
        dest0 = "%s/base/lib/python" % path
        j.sal.fs.createDir(dest0)

        j.sal.fs.copyDirTree(
            src0,
            dest0,
            keepsymlinks=False,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=ignoredir,
            ignorefiles=ignorefiles,
            recursive=True,
            rsyncdelete=True,
        )

        if j.core.platformtype.myplatform.isUbuntu:
            url = "git@github.com:threefoldtech/sandbox_ubuntu.git"
            path = j.clients.git.getContentPathFromURLorPath(url)
            src0 = "%s/lib/pythonbin/" % self.DIR_SANDBOX
            dest0 = "%s/base/lib/pythonbin/" % path
            j.sal.fs.createDir(dest0)
            j.sal.fs.copyDirTree(
                src0,
                dest0,
                keepsymlinks=False,
                deletefirst=False,
                overwriteFiles=True,
                ignoredir=ignoredir,
                ignorefiles=ignorefiles,
                recursive=True,
                rsyncdelete=True,
            )

        if j.core.platformtype.myplatform.isMac:
            url = "git@github.com:threefoldtech/sandbox_osx.git"
            path = j.clients.git.getContentPathFromURLorPath(url)
            src0 = "%s/lib/pythonbin/" % self.DIR_SANDBOX
            dest0 = "%s/base/lib/pythonbin/" % path
            j.sal.fs.createDir(dest0)
            j.sal.fs.copyDirTree(
                src0,
                dest0,
                keepsymlinks=False,
                deletefirst=False,
                overwriteFiles=True,
                ignoredir=ignoredir,
                ignorefiles=ignorefiles,
                recursive=True,
                rsyncdelete=True,
            )

    def _zip(self, dest="", python_lib_zip=False):
        j.builder.system.package.install("zip")
        if dest == "":
            dest = j.dirs.BUILDDIR + "/sandbox/python3/"
        cmd = "cd %s;rm -f ../js_sandbox.tar.gz;tar -czf ../js_sandbox.tar.gz .;" % dest
        j.sal.process.execute(cmd)
        if python_lib_zip:
            cmd = "cd %s;rm -f ../tfbot/lib/python.zip;cd ../tfbot/lib/python;zip -r ../python.zip .;" % dest
            j.sal.process.execute(cmd)
            cmd = "cd %s;rm -rf ../tfbot/lib/python" % dest
            j.sal.process.execute(cmd)

    def test(self, build=False):
        """
        js_shell 'j.builder.runtimes.python.test(build=True)'
        """
        self.profile_builder_select()
        assert self._execute("{DIR_BUILD}/bin/python3 -c \"print('python')\"")[1] == "python\n"
        assert self._execute('{DIR_BUILD}/bin/python3 -c "import capnp"')[0] == 0
        assert self._execute('{DIR_BUILD}/bin/python3 -c "import ssl"')[0] == 0

        print("TEST OK")
