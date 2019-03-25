from Jumpscale import j
import os
import textwrap
from time import sleep


class BuilderOpenResty(j.builder.system._BaseClass):
    NAME = 'openresty'

    def _init(self):
        self.BUILDDIR = j.core.tools.text_replace('{DIR_VAR}/build/')

        self.new_dirs = ['var/pid/', 'var/log/']
        self.root_files = {
            'etc/passwd': 'nobody:x:65534:65534:nobody:/:/sandbox/bin/openresty',
            'etc/group': 'nogroup:x:65534:'
        }

    def sandbox(self, dest_path="/tmp/builders/openresty", reset=False, create_flist=False, zhub_instance=None):
        '''Copy built bins to dest_path and create flist if create_flist = True

        :param dest_path: destination path to copy files into
        :type dest_path: str
        :param sandbox_dir: path to sandbox
        :type sandbox_dir: str
        :param reset: reset sandbox file transfer
        :type reset: bool
        :param create_flist: create flist after copying files
        :type create_flist:bool
        :param zhub_instance: hub instance to upload flist to
        :type zhub_instance:str
        '''
        if self._done_check('sandbox',reset):
            return
        self.build(reset=reset)

        self.bins = ['openresty', 'lua', 'resty', 'restydoc', 'restydoc-index', 'lapis', 'moon', 'moonc']
        self.dirs = {
            self.tools.joinpaths(j.core.dirs.BASEDIR, 'cfg/openresty.cfg'): 'cfg/',
            self.tools.joinpaths(j.core.dirs.BASEDIR, 'cfg/mime.types'): 'cfg/',
            self.tools.joinpaths(j.core.dirs.BASEDIR, 'openresty/'): 'openresty/',
                '/lib/x86_64-linux-gnu/libnss_files.so.2': 'lib',
        }
        lua_files = j.sal.fs.listFilesInDir(self.tools.joinpaths(j.core.dirs.BASEDIR, 'bin/'), filter='*.lua')
        for file in lua_files:
            self.dirs[file] = 'bin/'

        for bin_name in self.bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin_name)
            dir_dest = j.sal.fs.joinPaths(dest_path, j.core.dirs.BINDIR[1:])
            j.builder.tools.dir_ensure(dir_dest)
            j.sal.fs.copyFile(dir_src, dir_dest)

        lib_dest = j.sal.fs.joinPaths(dest_path, 'sandbox/lib')
        j.builder.tools.dir_ensure(lib_dest)
        for bin in self.bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest, exclude_sys_libs=False)

        for dir_src in self.dirs:
            dir_dest = j.sal.fs.joinPaths(dest_path, dir_src[1:])
            j.builder.tools.dir_ensure(dir_dest)
            j.sal.fs.copyDirTree(dir_src, dir_dest)

        startup_file = j.sal.fs.joinPaths(j.sal.fs.getDirName(__file__), 'templates', 'openresty_startup.toml')
        self.startup = j.sal.fs.readFile(startup_file)
        j.sal.fs.copyFile(startup_file,j.sal.fs.joinPaths(dest_path, 'sandbox'))

        self._done_set('sandbox')

        if create_flist:
            self.flist_create(dest_path, zhub_instance)

    def _build_prepare(self):
        j.builder.system.package.mdupdate()
        j.builder.system.package.ensure('build-essential libpcre3-dev libssl-dev zlib1g-dev')
        j.builder.tools.dir_remove('{DIR_VAR}/build/openresty')
        j.core.tools.dir_ensure('{DIR_VAR}/build/openresty')
        url = 'https://openresty.org/download/openresty-1.13.6.2.tar.gz'
        dest = j.core.tools.text_replace('{DIR_VAR}/build/openresty')
        j.sal.fs.createDir(dest)
        j.builder.tools.file_download(url, to=dest, overwrite=False, retry=3,
                                      expand=True, minsizekb=1000, removeTopDir=True, deletedest=True)

    def reset(self):
        """
        js_shell 'j.builder.web.openresty.reset()'
        :return:
        """
        self._done_reset()

        C = """
        cd /sandbox
        rm -rf {DIR_VAR}/build/openresty
        rm -f /sandbox/bin/lua*
        rm -f /sandbox/bin/moon*
        rm -f /sandbox/bin/openresty*
        rm -f /sandbox/bin/resty*
        rm -f /sandbox/bin/_moon*
        rm -f /sandbox/bin/_lapis*
        rm -f /sandbox/bin/lapis*
        rm -rf /sandbox/openresty/

        """
        self.tools.run(C)

    def build(self, reset=False):
        """
        js_shell 'j.builder.web.openresty.build()'
        :return:
        """
        if self._done_check("build") and not reset and j.sal.fs.exists("/sandbox/openresty"):
            return

        if reset:
            self.reset()

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
            self.tools.run(C)


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
            rm -f /sandbox/bin/lua
            cp /sandbox/openresty/luajit/bin/luajit /sandbox/bin/lua

            """
            self.tools.run(C)

        self._done_set("build")


    def install(self,reset=False):
        """
        will build & install in sandbox
        js_shell 'j.builder.web.openresty.install()'
        :return:
        """
        self.build(reset=reset)


    def copy_to_github(self,reset=False):
        """
        js_shell 'j.builder.web.openresty.copy_to_github(reset=True)'
        js_shell 'j.builder.web.openresty.copy_to_github()'
        :return:
        """
        self.build(reset=reset)

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

        self.tools.run(C,args=args)

    def start(self, config_file=None, args=None):
        test_dir = j.core.tools.text_replace('{DIR_TEMP}/lapis_test')
        if self.tools.exists(test_dir):
            self.tools.dir_remove(test_dir)
        self.tools.dir_ensure(test_dir)
        cmd = """
            cd {dir}
            lapis --lua new
            lapis server
        """.format(dir=test_dir)
        p = j.tools.tmux.execute(cmd, window=self.NAME, pane=self.NAME, reset=True)
        return p

    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key='test_main')
