from Jumpscale import j
import os
import textwrap
from time import sleep

builder_method = j.builder.system.builder_method


class BuilderOpenResty(j.builder.system._BaseClass):
    NAME = 'openresty'

    @builder_method()
    def build(self, reset=False):
        """
        js_shell 'j.builder.web.openresty.build()'
        :return:
        """
        if j.core.platformtype.myplatform.isUbuntu:
            j.builder.system.package.mdupdate()
            j.builder.system.package.ensure('build-essential libpcre3-dev libssl-dev zlib1g-dev')
            url = 'https://openresty.org/download/openresty-1.13.6.2.tar.gz'

            dest = self._replace('{DIR_BUILD}/openresty')
            self.tools.file_download(url, to=dest, overwrite=False, retry=3,
                                     expand=True, minsizekb=1000, removeTopDir=True, deletedest=True)
            C = """
            cd {DIR_BUILD}/openresty
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
            rm -rf {DIR_BUILD}
            rm -f /sandbox/bin/lua
            ln -s /sandbox/openresty/luajit/bin/luajit /sandbox/bin/lua

            """
            self._execute(C)

        else:
            # build with system openssl, no need to include custom build
            # j.builder.libs.openssl.build()

            url = "https://openresty.org/download/openresty-1.13.6.2.tar.gz"
            dest = self.DIR_BUILD
            self.tools.dir_ensure(dest)
            self.tools.file_download(url, to=dest, overwrite=False, retry=3,
                                     expand=True, minsizekb=1000, removeTopDir=True, deletedest=True)
            C = """
            cd {DIR_BUILD}
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
            rm -rf {DIR_BUILD}
            rm -f /sandbox/bin/lua
            cp /sandbox/openresty/luajit/bin/luajit /sandbox/bin/lua

            """
            self.tools.execute(C)

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False, merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist"):
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

        bins = ['openresty', 'lua', 'resty', 'restydoc', 'restydoc-index', 'lapis', 'moon', 'moonc']
        dirs = {
            self.tools.joinpaths(j.core.dirs.BASEDIR, 'cfg/openresty.cfg'): 'sandbox/cfg/',
            self.tools.joinpaths(j.core.dirs.BASEDIR, 'cfg/mime.types'): 'sandbox/cfg/',
            self.tools.joinpaths(j.core.dirs.BASEDIR, 'openresty/'): 'sandbox/openresty/',
            '/lib/x86_64-linux-gnu/libnss_files.so.2': 'sandbox/lib/'
        }
        new_dirs = ['sandbox/var/pid/', 'sandbox/var/log/']
        root_files = {
            'etc/passwd': 'nobody:x:65534:65534:nobody:/:/sandbox/bin/openresty',
            'etc/group': 'nogroup:x:65534:'
        }
        lua_files = j.sal.fs.listFilesInDir(self.tools.joinpaths(j.core.dirs.BASEDIR, 'bin/'), filter='*.lua')
        for file in lua_files:
            dirs[file] = 'sandbox/bin/'

        for bin_name in bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin_name)
            dir_dest = self.tools.joinpaths(self.DIR_SANDBOX, j.core.dirs.BINDIR[1:])
            self.tools.dir_ensure(dir_dest)
            self._copy(dir_src, dir_dest)

        lib_dest = self.tools.joinpaths(self.DIR_SANDBOX, 'sandbox/lib')
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest, exclude_sys_libs=False)

        for dir_src, dir_dest in dirs.items():
            dir_dest = self.tools.joinpaths(self.DIR_SANDBOX, dir_dest)
            self.tools.dir_ensure(dir_dest)
            self.tools.copyTree(dir_src, dir_dest)

        for dir_dest in new_dirs:
            dir_dest = self.tools.joinpaths(self.DIR_SANDBOX, self.tools.path_relative(dir_dest))
            self.tools.dir_ensure(dir_dest)

        for file_dest, content in root_files.items():
            file_dest = self.tools.joinpaths(self.DIR_SANDBOX, self.tools.path_relative(file_dest))
            dir = j.sal.fs.getDirName(file_dest)
            self.tools.dir_ensure(dir)
            self.tools.file_ensure(file_dest)
            self.tools.file_write(file_dest, content)

        cur_dir = j.sal.fs.getDirName(__file__)
        startup_file = self.tools.joinpaths(cur_dir, 'templates', 'openresty_startup.toml')
        file_dest = self.tools.joinpaths(self.DIR_SANDBOX, '.startup.toml')
        self._copy(startup_file, file_dest)

    @builder_method()
    def clean(self, reset=False):
        """
        js_shell 'j.builder.web.openresty.clean()'
        :return:
        """
        C = """
        cd /sandbox
        rm -rf {DIR_BUILD}
        rm -f /sandbox/bin/lua*
        rm -f /sandbox/bin/moon*
        rm -f /sandbox/bin/openresty*
        rm -f /sandbox/bin/resty*
        rm -f /sandbox/bin/_moon*
        rm -f /sandbox/bin/_lapis*
        rm -f /sandbox/bin/lapis*
        rm -rf /sandbox/openresty/

        """
        self._execute(C)

    def copy_to_github(self, reset=False):
        """
        js_shell 'j.builder.web.openresty.copy_to_github(reset=True)'
        js_shell 'j.builder.web.openresty.copy_to_github()'
        :return:
        """
        self.build(reset=reset)

        if j.core.platformtype.myplatform.isUbuntu:
            CODE_SB_BIN = j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_ubuntu.git")
        elif j.core.platformtype.myplatform.isMac:
            CODE_SB_BIN = j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_osx.git")
        else:
            raise RuntimeError("only ubuntu & osx support")

        CODE_SB_BASE = j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/sandbox_base.git")

        C = """
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
        args = {}
        args["CODE_SB_BIN"] = CODE_SB_BIN
        args["CODE_SB_BASE"] = CODE_SB_BASE
        args["SRCBINDIR"] = j.core.tools.text_replace("{DIR_BASE}/openresty/bin")
        args["BINDIR"] = j.core.tools.text_replace("{DIR_BASE}/bin")

        self.tools.execute(C, args=args)

    @property
    def startup_cmds(self):
        test_dir = j.core.tools.text_replace('{DIR_TEMP}/lapis_test')
        if self.tools.exists(test_dir):
            self.tools.dir_remove(test_dir)
        self.tools.dir_ensure(test_dir)
        cmd = """
            cd {dir}
            lapis --lua new
            lapis server
        """.format(dir=test_dir)
        cmds = [j.tools.startupcmd.get('test_openresty', cmd=cmd)]
        return cmds

    @builder_method()
    def stop(self):
        # stop openresty
        j.sal.process.killProcessByName(self.NAME)


    def test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        if self.running():
            self.stop()

        self.start()
        assert self.running()
        self._log_info("openresty is running")
