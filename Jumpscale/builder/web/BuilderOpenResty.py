from Jumpscale import j
import os
import textwrap
from time import sleep



class BuilderOpenResty(j.builder.system._BaseClass):
    NAME = 'openresty'

    def _init(self):
        self.BUILDDIR = j.core.tools.text_replace('{DIR_VAR}/build/')
        self.bins = [
            j.core.tools.text_replace('{DIR_BASE}/bin/openresty'),
            j.core.tools.text_replace('{DIR_BASE}/bin/lua'),
            j.core.tools.text_replace('{DIR_BASE}/bin/resty'),
            j.core.tools.text_replace('{DIR_BASE}/bin/restydoc'),
            j.core.tools.text_replace('{DIR_BASE}/bin/restydoc-index'),
            j.core.tools.text_replace('{DIR_BASE}/bin/lapis'),
            j.core.tools.text_replace('{DIR_BASE}/bin/moon'),
            j.core.tools.text_replace('{DIR_BASE}/bin/moonc')
        ]
        self.dirs = {
            j.core.tools.text_replace('{DIR_BASE}/cfg/openresty.cfg'): 'cfg/',
            j.core.tools.text_replace('{DIR_BASE}/cfg/mime.types'): 'cfg/',
            j.core.tools.text_replace('{DIR_BASE}/openresty/'): 'openresty/',
        }
        lua_files = j.sal.fs.listFilesInDir(j.core.tools.text_replace('{DIR_BASE}/bin/'), filter='*.lua')
        for file in lua_files:
            self.dirs[file] = 'bin/'

        self.new_dirs = ['var/pid/', 'var/log/']
        startup_file = j.sal.fs.joinPaths(j.sal.fs.getDirName(__file__), 'templates', 'openresty_startup.toml')
        self.new_files = {'//startup.toml': j.sal.fs.readFile(startup_file)}

    def _build_prepare(self):
        j.builder.system.package.mdupdate()
        j.builder.tools.package_install('build-essential libpcre3-dev libssl-dev zlib1g-dev')

        j.builder.tools.dir_remove('{DIR_TEMP}/build/openresty')
        j.core.tools.dir_ensure('{DIR_TEMP}/build/openresty')
        url = 'https://openresty.org/download/openresty-1.13.6.2.tar.gz'
        dest = j.core.tools.text_replace('{DIR_VAR}/build/openresty')
        j.sal.fs.createDir(dest)
        j.builder.tools.file_download(url, to=dest, overwrite=False, retry=3,
                                      expand=True, minsizekb=1000, removeTopDir=True, deletedest=True)

    def build(self, reset=False):
        """
        js_shell 'j.builder.web.openresty.build()'
        :param install:
        :return:
        """
        if self._done_check("build") and not reset:
            return

        j.tools.bash.local.locale_check()

        if j.core.platformtype.myplatform.isUbuntu:
            self._build_prepare()
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
            rm -f /sandbox/bin/lua
            ln -s /sandbox/openresty/luajit/bin/luajit /sandbox/bin/lua

            """
            C = j.builder.tools.replace(C)
            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)

        else:
            #build with system openssl, no need to include custom build
            # j.builder.libs.openssl.build()

            url="https://openresty.org/download/openresty-1.13.6.2.tar.gz"
            dest = j.core.tools.text_replace("{DIR_VAR}/build/openresty")
            j.sal.fs.createDir(dest)
            j.builder.tools.file_download(url, to=dest, overwrite=False, retry=3,
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
            rm /sandbox/bin/lua
            ln -s /sandbox/openresty/luajit/bin/luajit /sandbox/bin/lua

            """
            C = j.builder.tools.replace(C)
            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C)


        self.copy2sandbox_github()

        self._done_set("build")


    def copy2sandbox_github(self):
        """
        js_shell 'j.builder.web.openresty.copy2sandbox_github()'
        :return:
        """

        if j.core.platformtype.myplatform.isUbuntu:
            CODE_SB_BIN=j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_ubuntu.git")
        elif j.core.platformtype.myplatform.isMac:
            CODE_SB_BIN=j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_osx.git")
        else:
            raise RuntimeError("only ubuntu & osx support")

        CODE_SB_BASE = j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_base.git")

        C="""
        set -ex

        cp {SRCBINDIR}/resty* {CODE_SB_BASE}/base/bin/
        rm -f {CODE_SB_BIN}/base/bin/resty*

        cp {SRCBINDIR}/openresty {CODE_SB_BASE}/base/bin/
        rm -f {CODE_SB_BIN}/base/bin/openresty

        cp {DIR_BIN}/*.lua {CODE_SB_BASE}/base/bin/
        rm -f {CODE_SB_BIN}/base/bin/*.lua

        cp {DIR_BIN}/lapis {CODE_SB_BASE}/base/bin/
        rm -f {CODE_SB_BIN}/base/bin/lapis

        cp {DIR_BIN}/lua {CODE_SB_BIN}/base/bin/
        rm -f {CODE_SB_BASE}/base/bin/lua

        cp {DIR_BIN}/moon* {CODE_SB_BASE}/base/bin/
        rm -f {CODE_SB_BIN}/base/bin/moon*

        cp {DIR_BIN}/openresty {CODE_SB_BIN}/base/bin/
        rm -f {CODE_SB_BASE}/base/bin/openresty



        """
        args={}
        args["CODE_SB_BIN"]=CODE_SB_BIN
        args["CODE_SB_BASE"]=CODE_SB_BASE
        args["SRCBINDIR"]=j.core.tools.text_replace("{DIR_BASE}/openresty/bin")
        args["BINDIR"]=j.core.tools.text_replace("{DIR_BASE}/bin")

        C=j.core.tools.text_replace(C, args=args)

        j.sal.process.execute(C)
        # self.cleanup()
