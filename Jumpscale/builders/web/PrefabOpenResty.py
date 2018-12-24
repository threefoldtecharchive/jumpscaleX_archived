from Jumpscale import j
import os
import textwrap
from time import sleep





class BuilderOpenResty(j.builder.system._BaseClass):
    NAME = 'openresty'

    def _init(self):
        self.BUILDDIR = j.core.tools.text_replace("{DIR_VAR}/build/")


    def build(self, reset=False):
        """
        js_shell 'j.builder.web.openresty.build()'
        :param install:
        :return:
        """
        if self.doneCheck("build") and not reset:
            return

        j.builder.sandbox.locale_check()

        if j.builder.core.isUbuntu:
            j.builder.system.package.mdupdate()
            j.builder.tools.package_install("build-essential libpcre3-dev libssl-dev")

            # j.builder.core.dir_remove("{DIR_TEMP}/build/openresty")
            # j.builder.core.dir_ensure("{DIR_TEMP}/build/openresty")
            url="https://openresty.org/download/openresty-1.13.6.2.tar.gz"
            dest = j.core.tools.text_replace("{DIR_VAR}/build/openresty")
            j.sal.fs.createDir(dest)
            j.builder.core.file_download(url, to=dest, overwrite=False, retry=3,
                        expand=True, minsizekb=1000, removeTopDir=True, deletedest=True)

            C = """
            cd {DIR_VAR}/build/openresty
            mkdir -p /sandbox/var/pid
            mkdir -p /sandbox/var/log
            ./configure \
                --with-cc-opt="-I/usr/local/opt/openssl/include/ -I/usr/local/opt/pcre/include/" \
                --with-ld-opt="-L/usr/local/opt/openssl/lib/ -L/usr/local/opt/pcre/lib/" \
                --prefix="/sandbox/openresty" \
                --sbin-path="/sandbox/bin/openresty" \
                --modules-path="/sandbox/lib" \
                --pid-path="/sandbox/var/pid/openresty.pid" \
                --error-log-path="/sandbox/var/log/openresty.log" \
                --lock-path="/sandbox/var/nginx.lock" \
                --conf-path="/sandbox/cfg/openresty.cfg" \
                -j8
            make -j8
            make install
            rm -rf {DIR_VAR}/build/openresty
            
            ln -s /sandbox/openresty/luajit/bin/luajit /sandbox/bin/lua
            
            """
            C = j.builder.core.replace(C)
            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)

        else:
            #build with system openssl, no need to include custom build
            # j.builder.lib.openssl.build()

            url="https://openresty.org/download/openresty-1.13.6.2.tar.gz"
            dest = j.core.tools.text_replace("{DIR_VAR}/build/openresty")
            j.sal.fs.createDir(dest)
            j.builder.core.file_download(url, to=dest, overwrite=False, retry=3,
                        expand=True, minsizekb=1000, removeTopDir=True, deletedest=True)
            C="""
            cd {DIR_VAR}/build/openresty
            mkdir -p /sandbox/var/pid
            mkdir -p /sandbox/var/log
            ./configure \
                --with-cc-opt="-I/usr/local/opt/openssl/include/ -I/usr/local/opt/pcre/include/" \
                --with-ld-opt="-L/usr/local/opt/openssl/lib/ -L/usr/local/opt/pcre/lib/" \
                --prefix="/sandbox/openresty" \
                --sbin-path="/sandbox/bin/openresty" \
                --modules-path="/sandbox/lib" \
                --pid-path="/sandbox/var/pid/openresty.pid" \
                --error-log-path="/sandbox/var/log/openresty.log" \
                --lock-path="/sandbox/var/nginx.lock" \
                --conf-path="/sandbox/cfg/openresty.cfg" \
                -j8
            make -j8
            make install
            rm -rf {DIR_VAR}/build/openresty
            
            ln -s /sandbox/openresty/luajit/bin/luajit /sandbox/bin/lua
            
            """
            C = j.builder.core.replace(C)
            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)

        self.doneSet("build")

        self.copy2sandbox_github()


    def copy2sandbox_github(self):
        """
        js_shell 'j.builder.web.openresty.copy2sandbox_github()'
        :return:
        """
        assert self.executor.type=="local"

        if j.builder.core.isUbuntu:
            CODE_SB_BIN=j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_ubuntu.git")
        elif j.builder.core.isMac:
            CODE_SB_BIN=j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_osx.git")
        else:
            raise RuntimeError("only ubuntu & osx support")

        CODE_SB_BASE = j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_base.git")

        C="""
        set -ex

        cp $SRCBINDIR/resty* $CODE_SB_BASE/base/bin/
        rm -f $CODE_SB_BIN/base/bin/resty*
                
        cp $SRCBINDIR/openresty $CODE_SB_BASE/base/bin/
        rm -f $CODE_SB_BIN/base/bin/openresty        

        cp {DIR_BIN}/*.lua $CODE_SB_BASE/base/bin/
        rm -f $CODE_SB_BIN/base/bin/*.lua    

        cp {DIR_BIN}/lapis $CODE_SB_BASE/base/bin/
        rm -f $CODE_SB_BIN/base/bin/lapis  

        cp {DIR_BIN}/lua $CODE_SB_BIN/base/bin/
        rm -f $CODE_SB_BASE/base/bin/lua  

        cp {DIR_BIN}/moon* $CODE_SB_BASE/base/bin/
        rm -f $CODE_SB_BIN/base/bin/moon*
        
        cp {DIR_BIN}/openresty $CODE_SB_BIN/base/bin/
        rm -f $CODE_SB_BASE/base/bin/openresty
          


        """
        args={}
        args["CODE_SB_BIN"]=CODE_SB_BIN
        args["CODE_SB_BASE"]=CODE_SB_BASE
        args["SRCBINDIR"]="%s/openresty/bin"%j.core.installtools.MyEnv.config["DIR_BASE"]
        args["BINDIR"]="%s/bin"%j.core.installtools.MyEnv.config["DIR_BASE"]
        j.core.tools.run(C, args=args)
        # self.cleanup()
