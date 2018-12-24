from Jumpscale import j

JSBASE = j.builder.system._BaseClass

class BuilderPython(j.builder.system._BaseClass):

    def _init(self):
        self._logger_enable()
        self.BUILDDIRL = j.core.tools.text_replace("{DIR_VAR}/build/python3")
        self.CODEDIRL = j.core.tools.text_replace("{DIR_VAR}/build/code/python3")
        self.OPENSSLPATH = j.core.tools.text_replace("{DIR_VAR}/build/openssl")

    def reset(self):
        base.reset(self)
        j.sal.fs.remove(self.BUILDDIRL)
        j.sal.fs.remove(self.CODEDIRL)
        j.builder.system.python_pip.reset()

    def build(self, reset=False,tag="v3.6.7"):
        """
        js_shell 'j.core.builder.runtimes.python.build(reset=False)'
        js_shell 'j.core.builder.runtimes.python.build(reset=True)'


        will build python and install all pip's inside the builded directory

        possible tags: v3.7.1, v3.6.7

        """

        if reset:
            self.reset()

        j.builder.buildenv.install()
        j.shell()

        j.clients.git.pullGitRepo('https://github.com/python/cpython', dest=self.CODEDIRL, tag=tag, reset=reset, ssh=False, timeout=20000)
        if not self.doneGet("compile") or reset:
            if self.core.isMac:
                # clue to get it finally working was in https://stackoverflow.com/questions/46457404/how-can-i-compile-python-3-6-2-on-macos-with-openssl-from-homebrew

                C = """
                set -ex
                cd {CODEDIRL}
                mkdir -p {DIR_VAR}/build

                # export OPENSSLPATH=$(brew --prefix openssl)
                
                # export OPENSSLPATH={OPENSSLPATH}
                
                # export CPPFLAGS=-I/opt/X11/include
                # export CFLAGS="-I$(brew --prefix openssl)/include" LDFLAGS="-L$(brew --prefix openssl)/lib"                

                ./configure --prefix={BUILDDIRL}/  CPPFLAGS="-I{OPENSSLPATH}/include" LDFLAGS="-L{OPENSSLPATH}/lib"

                #if you do the optimizations then it will do all the tests
                # ./configure --prefix={BUILDDIRL}/ --enable-optimizations
                
                # make -j12

                make -j12 EXTRATESTOPTS=--list-tests install
                """
                C = j.core.tools.text_replace(C,args=self.__dict__)
            else:
                # on ubuntu 1604 it was all working with default libs, no reason to do it ourselves
                j.builder.tools.package_install('zlib1g-dev,libncurses5-dev,libbz2-dev,liblzma-dev,libsqlite3-dev,libreadline-dev,libssl-dev,libsnappy-dev')

                C = """

                apt install wget gcc make -y

                set -ex
                cd {CODEDIRL}
                
                # export OPENSSLPATH={OPENSSLPATH}

                ./configure --prefix={BUILDDIRL}/ --enable-optimizations  #THIS WILL MAKE SURE ALL TESTS ARE DONE, WILL TAKE LONG TIME

                make clean
                # make -j4
                make -j8 EXTRATESTOPTS=--list-tests install
                # make install
                """
                C = j.core.tools.text_replace(C,args=self.__dict__)

            j.sal.fs.writeFile("%s/mycompile_all.sh" % self.CODEDIRL, C)

            self._logger.info("compile python3")
            self._logger.debug(C)
            j.sal.process.execute("bash %s/mycompile_all.sh" % self.CODEDIRL, sudo=False)  # makes it easy to test & make changes where required

            #test openssl is working
            cmd = "source /sandbox/env.sh;/sandbox/var/build/python3/bin/python3 -c 'import ssl'"
            rc,out,err=j.sal.process.execute(cmd,die=False,args=self.__dict__)
            if rc>0:
                raise RuntimeError("SSL was not included well\n%s"%err)

            self.doneSet("compile")


        self._addPIP(reset=reset,tag=tag)

        return self.BUILDDIRL

    def _addPIP(self, reset=False,tag="v3.6.7"):
        """

        will make sure we add env scripts to it as well as add all the required pip modules

        js_shell 'j.core.builder.runtimes.python._addPIP(reset=True)'
        """

        C = """

        source env.sh

        export PBASE=`pwd`

        # export OPENSSLPATH=$(brew --prefix openssl)

        export PATH=$PATH:{OPENSSLPATH}/bin:/usr/local/bin:/usr/bin:/bin

        export LIBRARY_PATH="$LIBRARY_PATH:{OPENSSLPATH}/lib:/usr/lib:/usr/local/lib:/lib:/lib/x86_64-linux-gnu"
        export LD_LIBRARY_PATH="$LIBRARY_PATH"

        export CPPPATH="$PBASE/include/python3.6m:{OPENSSLPATH}/include:/usr/include"
        export CPATH="$CPPPATH"

        export CFLAGS="-I$CPATH/"
        export CPPFLAGS="-I$CPATH/"
        export LDFLAGS="-L$LIBRARY_PATH/"

        """
        C = j.core.tools.text_replace(C,args=self.__dict__)
        j.sal.fs.writeFile("%s/envbuild.sh" % self.BUILDDIRL, C)

        C = """
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
        j.sal.fs.writeFile("%s/env.sh" % self.BUILDDIRL, C)

        if not self.doneGet("pip3install") or reset:
            C = """
            cd {BUILDDIRL}/
            . envbuild.sh
            set -e                        
            rm -rf get-pip.py
            curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
            {DIR_VAR}/build//bin/python3 get-pip.py
            """
            C = j.core.tools.text_replace(C,args=self.__dict__)
            j.sal.fs.writeFile("%s/pip3build.sh" % self.BUILDDIRL, C)
            j.sal.process.execute("cd %s;bash pip3build.sh" % self.BUILDDIRL)
        self.doneSet("pip3install")

        if not self.core.isMac:
            self.prefab.system.package.ensure("libssl-dev")
            # for osx SHOULD NOT BE DONE BECAUSE WE SHOULD HAVE IT BUILD BEFORE AND ARE USING I FOR OSX
            # self.prefab.system.package.ensure("libcapnp-dev")
            pass
        else:
            self.prefab.system.package.ensure("capnp")

        self._pipAll(reset=reset)

        msg = "\n\nto test do:\ncd {DIR_VAR}/build/;source env.sh;python3"
        msg = j.core.tools.text_replace(msg)
        self._logger.info(msg)


    def _pipAll(self, reset=False):
        """
        js_shell 'j.core.builder.runtimes.python._pipAll(reset=False)'
        """

        if self.doneCheck("pipall", reset):
            return

        #need to build right version of capnp
        self.prefab.lib.capnp.build()

        #list comes from /sandbox/code/github/threefoldtech/jumpscale_core/install/InstallTools.py


        self._pip( j.core.installtools.UbuntuInstall.pips_list())

        if not self.core.isMac:
            raise NotImplementedError()
            self.prefab.zero_os.zos_stor_client.build(python_build=True)  # builds the zos_stor_client
            self._pip(["g8storclient"])

        # self.sandbox(deps=False)
        self.doneSet("pipall")


    # need to do it here because all runs in the sandbox
    def _pip(self, pips, reset=False):
        for item in pips:
            item = "'%s'"%item
            # cannot use prefab functionality because would not be sandboxed
            if not self.doneGet("pip3_%s" % item) or reset:
                C = "set -ex;cd {BUILDDIRL}/;source envbuild.sh;pip3 install --trusted-host pypi.python.org %s" % item
                j.sal.process.execute(j.core.tools.text_replace(C), shell=True)
                self.doneSet("pip3_%s" % item)


    @property
    def PACKAGEDIR(self):
        return j.dirs.BUILDDIR + "/sandbox/tfbot/"


    def copy2sandbox_github(self, reset=False):
        """

        js_shell 'j.core.builder.runtimes.python.copy2sandbox_github(reset=False)'


        builds python and returns the build dir

        result in : j.dirs.BUILDDIR+"/sandbox/tfbot/

        """
        assert self.executor.type=="local"

        path = self.build(reset=reset)


        self._logger.info("sandbox:%s" % path)
        j.core.builder.system.package.install("zip")
        if j.core.platformtype.myplatform.isMac:
            j.core.builder.system.package.install("redis")
        else:
            j.core.builder.system.package.install("redis-server")

        if path == "":
            path = self.BUILDDIR

        if not j.sal.fs.exists("%s/bin/python3.6" % path):
            j.shell()
            raise RuntimeError(
                "am not in compiled python dir, need to find %s/bin/python3.6" % path)

        dest = self.PACKAGEDIR

        j.sal.fs.remove(dest)
        j.sal.fs.createDir(dest)

        for item in ["bin", "root", "lib"]:
            j.sal.fs.createDir("%s/%s" % (dest, item))

        for item in ["pip3", "python3.6", "ipython","bpython","electrum","pudb3","zrobot"]:
            src0 = "%s/bin/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            if j.sal.fs.exists(src0):
                j.sal.fs.copyFile(src0, dest0)

        #for OSX
        for item in ["libpython3.6m.a"]:
            src0 = "%s/lib/%s" % (path, item)
            dest0 = "%s/bin/%s" % (dest, item)
            if j.sal.fs.exists(src0):
                j.sal.fs.copyFile(src0, dest0)




        #LINK THE PYTHON BINARIES
        j.sal.fs.symlink("%s/bin/python3.6" % dest, "%s/bin/python" % dest, overwriteTarget=True)
        j.sal.fs.symlink("%s/bin/python3.6" % dest, "%s/bin/python3" % dest, overwriteTarget=True)


        #NOW DEAL WITH THE PYTHON LIBS

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
                self._logger.debug("found binary files in:%s" % path)
                return True
            return False

        # ignore files which are not relevant,

        ignoredir = ['.egg-info', '.dist-info', "__pycache__", "audio", "tkinter", "audio", "test",
                     "electrum_"]
        ignorefiles = ['.egg-info', ".pyc"]

        todo = ["%s/lib/python3.6/site-packages" % path,"%s/lib/python3.6" % path]
        for src in todo:
            for ddir in j.sal.fs.listDirsInDir(src, recursive=False, dirNameOnly=True, findDirectorySymlinks=True, followSymlinks=True):
                if dircheck(ddir):
                    src0 = src+"/%s" % ddir
                    if binarycheck(src0):
                        dest0 = "%s/lib/pythonbin/%s" % (dest, ddir)
                    else:
                        dest0 = "%s/lib/python/%s" % (dest, ddir)
                    self._logger.debug("copy lib:%s ->%s" % (src0, dest0))
                    j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=True, overwriteFiles=True, ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True, createdir=True)


            for item in j.sal.fs.listFilesInDir(src, recursive=False, exclude=ignorefiles, followSymlinks=True):
                fname = j.sal.fs.getBaseName(item)
                dest0 = ""
                if fname.endswith(".so") or ".so." in fname:
                    dest0 = "%s/lib/pythonbin/%s" % (dest, fname)
                if fname.endswith(".py"):
                    dest0 = "%s/lib/python/%s" % (dest, fname)
                self._logger.debug("copy %s %s" % (item, dest0))
                if dest0 is not "":
                    j.sal.fs.copyFile(item, dest0)

        self.env_write(dest)


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

        C="""
        mv $PACKAGEDIR/lib/python/_sysconfigdata_m_linux_x86_64-linux-gnu.py $PACKAGEDIR/lib/pythonbin/_sysconfigdata_m_linux_x86_64-linux-gnu.py
        rm -rf $PACKAGEDIR/lib/python/config-3.6m-x86_64-linux-gnu
        
        """
        args={}
        args["$PACKAGEDIR"]=self.PACKAGEDIR
        C = j.core.tools.text_strip(C,args=args)
        j.sal.process.executeBashScript(C)

        def copy2git():

            #copy to sandbox & upload
            ignoredir = ['.egg-info', '.dist-info', "__pycache__", "audio", "tkinter", "audio", "test",".git","linux-gnu"]
            ignorefiles = ['.egg-info', ".pyc","_64-linux-gnu.py"]

            path = j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_base.git")
            src0 = "%s/lib/python"%self.PACKAGEDIR
            dest0 = "%s/base/lib/python"%path
            j.sal.fs.createDir(dest0)
            j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=False, overwriteFiles=True,
                             ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True)
            j.shell()

            if j.core.platformtype.myplatform.isUbuntu:
                url = "git@github.com:threefoldtech/sandbox_ubuntu.git"
                path = j.clients.git.getContentPathFromURLorPath(url)
                src0 = "%s/lib/pythonbin"%self.PACKAGEDIR
                dest0 = "%s/base/lib/pythonbin"%path
                j.sal.fs.createDir(dest0)
                j.sal.fs.copyDirTree(src0, dest0, keepsymlinks=False, deletefirst=False, overwriteFiles=True,
                                 ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=True)

            if j.core.platformtype.myplatform.isMac:
                url = "git@github.com:threefoldtech/sandbox_osx.git"
                j.shell()




        copy2git()


    def _zip(self, dest="", python_lib_zip=False):
        assert self.executor.type=="local"
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
        #TODO: need to test
        if build:
            self.build()

        raise RuntimeError("implement")

        print("TEST OK")
