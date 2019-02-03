from Jumpscale import j


class BuilderPython(j.builder.system._BaseClass):
    def _init(self):

        self._logger_enable()

        self.DIR_BUILD_L = j.core.tools.text_replace("{DIR_VAR}/build/python3")
        j.sal.fs.createDir(self.DIR_BUILD_L)

        self.DIR_CODE_L = j.core.tools.text_replace("{DIR_VAR}/build/code/python3")

        if not j.core.platformtype.myplatform.isMac:
            self.PATH_OPENSSL = j.core.tools.text_replace("{DIR_VAR}/build/openssl")
        else:
            rc,out,err=j.sal.process.execute("brew --prefix openssl")
            self.PATH_OPENSSL=out.strip()

        self.DIR_PACKAGE = j.core.tools.text_replace("{DIR_VAR}/build/sandbox/tfbot/")
        j.sal.fs.createDir(self.DIR_PACKAGE)

    def reset(self):
        j.sal.fs.remove(self.DIR_BUILD_L)
        j.sal.fs.remove(self.DIR_CODE_L)
        j.sal.fs.remove(self.DIR_PACKAGE)

    def build(self, reset=False, sandbox=True,tag="v3.6.7"):
        """

        js_shell 'j.builder.runtimes.python.build(reset=False)'
        js_shell 'j.builder.runtimes.python.build(reset=True)'

        will build python and install all pip's inside the build directory

        :param reset: choose to reset the build process even if it was done before
        :type reset: bool
        :param tag: the python version tag (possible tags: 3.7.1, 3.6.7)
        :type tag: str
        :return:
        """
        if reset:
            self.reset()

        j.builder.buildenv.install()


        if not self._done_get("compile") or reset:

            j.clients.git.pullGitRepo('https://github.com/python/cpython', dest=self.DIR_CODE_L, depth=1,
                                  tag=tag, reset=reset, ssh=False, timeout=20000)

            if j.core.platformtype.myplatform.isMac:
                # clue to get it finally working was in
                # https://stackoverflow.com/questions/46457404/
                # how-can-i-compile-python-3-6-2-on-macos-with-openssl-from-homebrew

                script = """
                set -ex
                cd {DIR_CODE_L}
                mkdir -p {DIR_BUILD_L}

                # export CPPFLAGS=-I/opt/X11/include
                # export CFLAGS="-I${PATH_OPENSSL}/include" LDFLAGS="-L${PATH_OPENSSL}/lib"

                ./configure --prefix={DIR_BUILD_L}/  CPPFLAGS="-I{PATH_OPENSSL}/include" LDFLAGS="-L{PATH_OPENSSL}/lib"

                #if you do the optimizations then it will do all the tests
                # ./configure --prefix={DIR_BUILD_L}/ --enable-optimizations

                # make -j12

                make -j12 EXTRATESTOPTS=--list-tests install
                """
                script = j.core.tools.text_replace(script, args=self.__dict__)
            else:
                # on ubuntu 1604 it was all working with default libs, no reason to do it ourselves
                j.builder.libs.openssl.build()
                j.builder.system.package.install([
                    'zlib1g-dev',
                    'libncurses5-dev',
                    'libbz2-dev',
                    'liblzma-dev',
                    'libsqlite3-dev',
                    'libreadline-dev',
                    'libssl-dev',
                    'libsnappy-dev',
                    'wget',
                    'gcc',
                    'make'
                ])
                script = """
                set -ex
                cd {DIR_CODE_L}
                mkdir -p {DIR_BUILD_L}

                # THIS WILL MAKE SURE ALL TESTS ARE DONE, WILL TAKE LONG TIME
                ./configure --prefix={DIR_BUILD_L}/ --enable-optimizations

                make clean
                make -j8 EXTRATESTOPTS=--list-tests install
                """
                script = script.format(DIR_BUILD_L=self.DIR_BUILD_L, DIR_CODE_L=self.DIR_CODE_L)

            j.sal.fs.writeFile("%s/mycompile_all.sh" % self.DIR_CODE_L, script)

            self._log_info("compiling python3...")
            self._log_debug(script)

            # makes it easy to test & make changes where required
            j.sal.process.execute("bash %s/mycompile_all.sh" % self.DIR_CODE_L)

            # test openssl is working
            cmd = "source /sandbox/env.sh;/sandbox/var/build/python3/bin/python3 -c 'import ssl'"
            rc, out, err = j.sal.process.execute(cmd, die=False)
            if rc > 0:
                raise RuntimeError("SSL was not included well\n%s" % err)
            self._done_set("compile")

        self._add_pip(reset=reset)

        if sandbox:
            self.sandbox()


    def _add_pip(self, reset=False):
        """
        will make sure we add env scripts to it as well as add all the required pip modules
        js_shell 'j.builder.runtimes.python._add_pip(reset=True)'
        :param reset: choose to reset the build process even if it was done before
        :type reset: bool
        """

        script = """
        source env.sh
        export PBASE=`pwd`
        export PATH=$PATH:{PATH_OPENSSL}/bin:/usr/local/bin:/usr/bin:/bin
        export LIBRARY_PATH="$LIBRARY_PATH:{PATH_OPENSSL}/lib:/usr/lib:/usr/local/lib:/lib:/lib/x86_64-linux-gnu"
        export LD_LIBRARY_PATH="$LIBRARY_PATH"

        export CPPPATH="$PBASE/include/python3.6m:{PATH_OPENSSL}/include:/usr/include"
        export CPATH="$CPPPATH"
        export CFLAGS="-I$CPATH/"
        export CPPFLAGS="-I$CPATH/"
        export LDFLAGS="-L$LIBRARY_PATH/"
        """
        script = script.format(PATH_OPENSSL=self.PATH_OPENSSL)
        j.sal.fs.writeFile("%s/envbuild.sh" % self.DIR_BUILD_L, script)

        script = """
        export PBASE=`pwd`
        export PYTHONHTTPSVERIFY=0
        export PATH=$PBASE/bin:/usr/local/bin:/usr/bin
        export PYTHONPATH=$PBASE/lib/python.zip:$PBASE/lib:$PBASE/lib/python3.6:$PBASE/lib/python3.6/site-packages:$PBASE/lib/python3.6/lib-dynload:$PBASE/bin
        export PYTHONHOME=$PBASE
        export LIBRARY_PATH="$PBASE/bin:$PBASE/lib"
        export LD_LIBRARY_PATH="$LIBRARY_PATH"
        export LDFLAGS="-L$LIBRARY_PATH/"
        export LC_ALL=en_US.UTF-8
        export LANG=en_US.UTF-8
        export PS1="JUMPSCALE: "
        """
        j.sal.fs.writeFile("%s/env.sh" % self.DIR_BUILD_L, script)

        if not self._done_get("pip3install") or reset:
            script = """
            cd {DIR_BUILD_L}/
            . envbuild.sh
            set -e
            rm -rf get-pip.py
            curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
            {DIR_BUILD_L}/bin/python3 get-pip.py
            """
            script = j.core.tools.text_replace(script, args=self.__dict__)
            j.sal.fs.writeFile("%s/pip3build.sh" % self.DIR_BUILD_L, script)
            j.sal.process.execute("cd %s;bash pip3build.sh" % self.DIR_BUILD_L)
        self._done_set("pip3install")

        self._pip_all(reset=reset)

        msg = "\n\nto test do:\ncd {DIR_VAR}/build/;source env.sh;python3"
        msg = j.core.tools.text_replace(msg)

        self._log_info(msg)

    def _pip_all(self, reset=False):
        """
        js_shell 'j.builder.runtimes.python._pip_all(reset=True)'
        """
        if self._done_check("pipall", reset):
            return

        # need to build right version of capnp
        # TODO Fix Capnp builder
        # j.builder.libs.capnp.build()

        # list comes from /sandbox/code/github/threefoldtech/jumpscale_core/install/InstallTools.py

        self._pip(j.core.installer_ubuntu.pips_list(),reset=reset)

        if not self.tools.isMac:
            # raise NotImplementedError()
            j.builders.zero_os.zos_stor_client.build(python_build=True)  # builds the zos_stor_client
            self._pip(["g8storclient"])

        # self.sandbox(deps=False)
        self._done_set("pipall")

        self._log_info("PIP DONE")

    # need to do it here because all runs in the sandbox
    def _pip(self, pips, reset=False):
        for item in pips:
            item = "'%s'" % item
            # cannot use prefab functionality because would not be sandboxed
            if not self._done_get("pip3_%s" % item) or reset:
                script = "set -ex;cd {DIR_BUILD_L}/;" \
                         "source envbuild.sh;" \
                         "pip3 install --trusted-host pypi.python.org %s" % item
                j.sal.process.execute(j.core.tools.text_replace(script,args=self.__dict__))
                self._done_set("pip3_%s" % item)

    def sandbox(self,copy2git=True):
        """
        js_shell 'j.builder.runtimes.python.sandbox()'
        :return:
        """

        self._copy2sandbox_github()
        path=j.core.tools.text_replace("{DIR_PACKAGE}/bin/",args=self.__dict__)
        j.tools.sandboxer.libs_sandbox(path,path,True)
        path=j.core.tools.text_replace("{DIR_PACKAGE}/lib/pythonbin/",args=self.__dict__)
        j.tools.sandboxer.libs_sandbox(path,path,True)
        if copy2git:
            self.copy2git()

    def _copy2sandbox_github(self):
        """

        js_shell 'j.builder.runtimes.python.copy2sandbox_github(reset=False)'


        builds python and returns the build dir

        """

        self._log_info("COPY FILES TO SANDBOX")

        path = self.DIR_BUILD_L
        self._log_info("sandbox:%s" % path)

        if j.core.platformtype.myplatform.isMac:
            j.builder.system.package.install("redis")
        else:
            j.builder.system.package.install("redis-server")


        if not j.sal.fs.exists("%s/bin/python3.6" % path):
            raise RuntimeError("am not in compiled python dir, need to find %s/bin/python3.6" % path)

        dest = self.DIR_PACKAGE

        j.sal.fs.remove(dest)
        j.sal.fs.createDir(dest)

        for item in ["bin", "root", "lib"]:
            j.sal.fs.createDir("%s/%s" % (dest, item))

        for item in ["pip3", "python3.6", "ipython", "bpython", "electrum", "pudb3", "zrobot"]:
            src0 = "%s/bin/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            if j.sal.fs.exists(src0):
                j.sal.fs.copyFile(src0, dest0)

        # for OSX
        for item in ["libpython3.6m.a"]:
            src0 = "%s/lib/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            if j.sal.fs.exists(src0):
                j.sal.fs.copyFile(src0, dest0)

        # LINK THE PYTHON BINARIES
        j.sal.fs.symlink("%s/bin/python3.6" % dest, "%s/bin/python" % dest, overwriteTarget=True)
        j.sal.fs.symlink("%s/bin/python3.6" % dest, "%s/bin/python3" % dest, overwriteTarget=True)

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

        ignoredir = ['.egg-info', '.dist-info', "__pycache__", "audio", "tkinter", "audio", "test",
                     "electrum_"]
        ignorefiles = ['.egg-info', ".pyc"]

        todo = ["%s/lib/python3.6/site-packages" % path, "%s/lib/python3.6" % path]
        for src in todo:
            for ddir in j.sal.fs.listDirsInDir(src, recursive=False, dirNameOnly=True, findDirectorySymlinks=True,
                                               followSymlinks=True):
                if dircheck(ddir):
                    src0 = src + "/%s" % ddir
                    if binarycheck(src0):
                        dest0 = "%s/lib/pythonbin/%s" % (dest, ddir)
                    else:
                        dest0 = "%s/lib/python/%s" % (dest, ddir)
                    self._log_debug("copy lib:%s ->%s" % (src0, dest0))
                    j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True,
                                         ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True,
                                         createdir=True)

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
            mv {DIR_PACKAGE}/lib/python/_sysconfigdata_m_darwin_darwin.py {DIR_PACKAGE}/lib/pythonbin/_sysconfigdata_m_darwin_darwin.py
            rm -rf {DIR_PACKAGE}/lib/python/config-3.6m-darwin
    
            """
        else:
            C = """
            mv {DIR_PACKAGE}/lib/python/_sysconfigdata_m_linux_x86_64-linux-gnu.py {DIR_PACKAGE}/lib/pythonbin/_sysconfigdata_m_linux_x86_64-linux-gnu.py
            rm -rf {DIR_PACKAGE}/lib/python/config-3.6m-x86_64-linux-gnu
    
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
        ignoredir = ['.egg-info', '.dist-info', "__pycache__", "audio", "tkinter", "audio", "test", ".git",
                     "linux-gnu"]
        ignorefiles = ['.egg-info', ".pyc", "_64-linux-gnu.py"]

        path = j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_base.git")
        src0 = "%s/lib/python" % self.DIR_PACKAGE
        dest0 = "%s/base/lib/python" % path
        j.sal.fs.createDir(dest0)

        j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=False, overwriteFiles=True,
                             ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True)

        if j.core.platformtype.myplatform.isUbuntu:
            url = "git@github.com:threefoldtech/sandbox_ubuntu.git"
            path = j.clients.git.getContentPathFromURLorPath(url)
            src0 = "%s/lib/pythonbin/" % self.DIR_PACKAGE
            dest0 = "%s/base/lib/pythonbin/" % path
            j.sal.fs.createDir(dest0)
            j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=False, overwriteFiles=True,
                                 ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True)

        if j.core.platformtype.myplatform.isMac:
            url = "git@github.com:threefoldtech/sandbox_osx.git"
            path = j.clients.git.getContentPathFromURLorPath(url)
            src0 = "%s/lib/pythonbin/" % self.DIR_PACKAGE
            dest0 = "%s/base/lib/pythonbin/" % path
            j.sal.fs.createDir(dest0)
            j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=False, overwriteFiles=True,
                                 ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True)




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
        # TODO: need to test
        if build:
            self.build()

        raise RuntimeError("implement")

        print("TEST OK")


