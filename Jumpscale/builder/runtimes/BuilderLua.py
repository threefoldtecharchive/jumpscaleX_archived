from Jumpscale import j


class BuilderLua(j.builder.system._BaseClass):

    NAME = "lua"

    def _init(self):
        self.BUILDDIR = j.core.tools.text_replace("{DIR_VAR}/build/")

    def reset(self):
        """
        js_shell 'j.builder.runtimes.lua.reset()'
        :return:
        """
        self._done_reset()
        j.builder.web.openresty.reset()  # make sure openresty gets build properly
        C = """
        cd /sandbox

        """
        self.tools.run(C)

    def build(self, reset=True):
        """
        js_shell 'j.builder.runtimes.lua.build()'
        :param install:
        :return:
        """
        if self._done_check("build") and not reset:
            return

        if j.core.platformtype.myplatform.isUbuntu:
            j.builder.system.package.install(['libsqlite3-dev'])

        j.tools.bash.local.locale_check()
        # need openresty & openssl to start from
        j.builder.web.openresty.build(reset)
        j.builder.libs.openssl.build(reset)

        url = "https://luarocks.org/releases/luarocks-3.0.4.tar.gz"
        dest = j.core.tools.text_replace("{DIR_VAR}/build/luarocks")
        j.sal.fs.createDir(dest)
        j.builder.tools.file_download(url, to=dest, overwrite=False, retry=3,
                                      expand=True, minsizekb=100, removeTopDir=True, deletedest=True)
        C = """
        cd {DIR_VAR}/build/luarocks
        ./configure --prefix=/sandbox/openresty/luarocks --with-lua=/sandbox/openresty/luajit
        make build
        make install

        cp /sandbox/var/build/luarocks/luarocks /sandbox/bin/luarocks

        """
        # set showout to False to avoid text_replace of output log
        self.tools.run(C, showout=False)

        self.lua_rocks_install(reset)

        self._done_set("build")

    def lua_rock_install(self, name, reset=False):
        if self._done_check("lua_rock_install_%s" % name) and not reset:
            return

        C = "luarocks install $NAME OPENSSL_DIR=/sandbox/var/build/openssl CRYPTO_DIR=/sandbox/var/build/openssl"
        C = C.replace("$NAME", name)
        j.sal.process.execute(j.core.tools.text_replace(C))

        self._done_set("lua_rock_install_%s" % name)

    def lua_rocks_install(self, reset=False):
        """
        js_shell 'j.builder.runtimes.lua.lua_rocks_install()'
        :param install:
        :return:
        """

        if j.core.platformtype.myplatform.isUbuntu:
            # j.builder.system.package.mdupdate()
            j.builder.tools.package_install("geoip-database,libgeoip-dev")

        C = """
        luaossl
        luasec
        lapis
        moonscript
        lapis-console
        LuaFileSystem
        luasocket
        lua-geoip
        lua-cjson
        lua-term
        penlight
        lpeg
        mediator_lua
        # luajwt
        # mooncrafts
        inspect
        lua-resty-jwt
        lua-resty-redis-connector
        lua-resty-openidc

        LuaRestyRedis
        lua-resty-qless

        lua-capnproto
        lua-toml

        lua-resty-exec

        lua-resty-influx
        lua-resty-repl


        lua-resty-iputils

        lsqlite3

        bcrypt
        md5

        date
        uuid
        lua-resty-cookie
        lua-path

        #various encryption
        luazen

        alt-getopt

        lua-resty-iyo-auth
        """

        for line in C.split("\n"):
            line = line.strip()
            if line == "":
                continue
            if line.startswith("#"):
                continue
            self.lua_rock_install(line, reset)

        C = """
        export LUALIB=/sandbox/openresty/lualib
        rsync -rav /sandbox/var/build/luarocks/lua_modules/lib/lua/5.1/ $LUALIB/
        rsync -rav /sandbox/var/build/luarocks/lua_modules/share/lua/5.1/ $LUALIB/

        """
        self.tools.run(C)

    # def build_crypto(self):
    #
    #     """
    #     # https://github.com/evanlabs/luacrypto
    #
    #     export OPENSSL_CFLAGS=-I/usr/local/opt/openssl/include/
    #     export OPENSSL_LIBS="-L/usr/local/opt/openssl/lib -lssl -lcrypto"
    #     export LUAJIT_LIB="/sandbox/openresty/luajit/lib"
    #     export LUAJIT_INC="/sandbox/openresty/luajit/include/luajit-2.1"
    #     export LUA_CFLAGS="-I/sandbox/openresty/luajit/include/luajit-2.1/"
    #     export LUA_LIB="/sandbox/openresty/luajit/lib"
    #     export LUA_INC="/sandbox/openresty/luajit/include/luajit-2.1"
    #
    #     :return:
    #     """

    def cleanup(self):
        """
        js_shell 'j.builder.runtimes.lua.cleanup()'
        :param install:
        :return:
        """
        C = """

        set -ex

        rm -rf /sandbox/openresty/luajit/lib/lua
        rm -rf /sandbox/openresty/luajit/lib/luarocks
        rm -rf /sandbox/openresty/luajit/lib/pkgconfig
        rm -rf /sandbox/openresty/pod
        rm -rf /sandbox/openresty/luarocks
        rm -rf /sandbox/openresty/luajit/include
        rm -rf /sandbox/openresty/luajit/lib/lua
        rm -rf /sandbox/openresty/luajit/lib/pkgconfig
        rm -rf  /sandbox/openresty/luajit/share
        rm -rf  /sandbox/var/build
        rm -rf  /sandbox/root
        mkdir -p /sandbox/root


        """
        self.tools.run(C)

    def install(self, reset=False):
        """
        will build & install in sandbox
        js_shell 'j.builder.runtimes.lua.install()'
        :return:
        """
        self.build(reset=reset)
        src = j.clients.git.getContentPathFromURLorPath(
            "https://github.com/threefoldtech/sandbox_base/tree/master/base/bin", pull=True)
        C = """

        set -e
        pushd /sandbox/openresty/bin
        cp resty /sandbox/bin/resty
        popd

        pushd /sandbox/var/build/luarocks/lua_modules/lib/luarocks/rocks-5.1/lapis/1.7.0-1/bin
        cp lapis /sandbox/bin/_lapis.lua
        popd

        pushd '/sandbox/var/build/luarocks/lua_modules/lib/luarocks/rocks-5.1/moonscript/0.5.0-1/bin'
        cp moon /sandbox/bin/_moon.lua
        cp moonc /sandbox/bin/_moonc.lua
        popd

        """
        self.tools.run(C)

        j.sal.fs.copyDirTree(src, "/sandbox/bin/", rsyncdelete=False, recursive=False, overwriteFiles=True)

        self._log_info("install lua & openresty done.")

    def sandbox(self, dest_path="/tmp/builders/lua", reset=False, create_flist=False, zhub_instance=None):
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
        if self._done_check('sandbox', reset):
            return
        if not self._done_check('build'):
            self.build(reset=reset)

        j.builder.web.openresty.sandbox(dest_path=dest_path, reset=reset)

        self.bins = ['_lapis.lua', '_moonc.lua', '_moon.lua', '_moonrocks.lua']

        for bin_name in self.bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin_name)
            dir_dest = j.sal.fs.joinPaths(dest_path, j.core.dirs.BINDIR[1:])
            j.builder.tools.dir_ensure(dir_dest)
            j.sal.fs.copyFile(dir_src, dir_dest)

        self._done_set('sandbox')

        if create_flist:
            self.flist_create(dest_path, zhub_instance)

    def copy_to_github(self):
        """
        js_shell 'j.builder.runtimes.lua.copy_to_github()'
        :return:
        """
        # assert self.executor.type=="local"
        path = "/sandbox/openresty/lualib"

        if j.core.platformtype.myplatform.isUbuntu:
            destbin = "%s/base/openresty/lualib" % j.clients.git.getContentPathFromURLorPath(
                "git@github.com:threefoldtech/sandbox_ubuntu.git")
        elif j.core.platformtype.myplatform.isMac:
            destbin = "%s/base/openresty/lualib" % j.clients.git.getContentPathFromURLorPath(
                "git@github.com:threefoldtech/sandbox_osx.git")
        else:
            raise RuntimeError("only ubuntu & osx support")

        dest = "%s/base/openresty/lualib" % j.clients.git.getContentPathFromURLorPath(
            "git@github.com:threefoldtech/sandbox_base.git")

        for item in j.sal.fs.listFilesInDir(path, recursive=True):
            rdest = j.sal.fs.pathRemoveDirPart(item, path)
            if j.sal.fs.getFileExtension(item) == "so":
                d2 = destbin
            elif j.sal.fs.getFileExtension(item) == "lua":
                d2 = dest
            else:
                raise RuntimeError(item)
            dir_dest_full = j.sal.fs.getDirName(j.sal.fs.joinPaths(d2, rdest))
            j.sal.fs.createDir(dir_dest_full)
            dest_full = j.sal.fs.joinPaths(d2, rdest)
            print("copy: %s %s" % (item, dest_full))
            j.sal.fs.copyFile(item, dest_full)

        self.cleanup()
