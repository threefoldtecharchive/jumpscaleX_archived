from Jumpscale import j

builder_method = j.builder.system.builder_method


class BuilderLua(j.builder.system._BaseClass):

    NAME = "lua"

    @builder_method()
    def build(self, reset=False):
        """
        js_shell 'j.builder.runtimes.lua.build()'
        :param install:
        :return:
        """
        if j.core.platformtype.myplatform.isUbuntu:
            j.builder.system.package.install(['libsqlite3-dev'])

        # need openresty & openssl to start from
        j.builder.web.openresty.build(reset=reset)
        j.builder.libs.openssl.build(reset=reset)

        url = "https://luarocks.org/releases/luarocks-3.0.4.tar.gz"
        dest = self._replace("{DIR_BUILD}/luarocks")
        self.tools.dir_ensure(dest)
        self.tools.file_download(url, to=dest, overwrite=False, retry=3,
                                 expand=True, minsizekb=100, removeTopDir=True, deletedest=True)
        C = """
        cd {DIR_BUILD}/luarocks
        ./configure --prefix=/sandbox/openresty/luarocks --with-lua=/sandbox/openresty/luajit
        make build
        make install

        cp {DIR_BUILD}/luarocks/luarocks /sandbox/bin/luarocks

        """
        # set showout to False to avoid text_replace of output log
        self._execute(C, showout=False)

        self.lua_rocks_install()

    def lua_rock_install(self, name, reset=False):
        self._log_info("lua_rock_install: %s" % name)
        if self._done_check("lua_rock_install_%s" % name) and not reset:
            return

        C = "luarocks install $NAME"
        C = C.replace("$NAME", name)
        self._execute(C)

        self._done_set("lua_rock_install_%s" % name)

    def lua_rocks_install(self, reset=False):
        """
        js_shell 'j.builder.runtimes.lua.lua_rocks_install()'
        :param install:
        :return:
        """

        if j.core.platformtype.myplatform.isUbuntu:
            # j.builder.system.package.mdupdate()
            j.builder.system.package.ensure("geoip-database,libgeoip-dev")

        C = """
        luaossl
        luasec
        lapis
        moonscript
        lapis-console
        LuaFileSystem
        luasocket
        # lua-geoip
        lua-cjson
        lua-term
        penlight
        lpeg
        mediator_lua
        # luajwt
        # mooncrafts
        inspect

        lua-resty-redis-connector
        lua-resty-openidc

        LuaRestyRedis
        # lua-resty-qless

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

        # various encryption
        luazen

        alt-getopt


        lua-messagepack
        """

        for line in C.split("\n"):
            line = line.strip()
            if line == "":
                continue
            if line.startswith("#"):
                continue
            self.lua_rock_install(line, reset)

        if j.core.platformtype.myplatform.isUbuntu:
            self.lua_rock_install("lua-geoip", reset)
            self.lua_rock_install("lua-resty-jwt", reset)
            self.lua_rock_install("lua-resty-iyo-auth", reset)  # need to check how to get this to work on OSX
        cmd = self._replace("rsync -rav {DIR_BUILD}/luarocks/lua_modules/lib/lua/5.1/ /sandbox/openresty/lualib")
        self.tools.execute(cmd, die=False)
        cmd = self._replace("rsync -rav {DIR_BUILD}/luarocks/lua_modules/share/lua/5.1/ /sandbox/openresty/lualib")
        self.tools.execute(cmd, die=False)

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

    def clean(self, reset=False):
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
        self._execute(C)

    @builder_method()
    def install(self, reset=False):
        """
        will build & install in sandbox
        js_shell 'j.builder.runtimes.lua.install()'
        :return:
        """
        src = "/sandbox/code/github/threefoldtech/sandbox_base/base/bin"
        C = """

        set -e
        pushd /sandbox/openresty/bin
        cp resty /sandbox/bin/resty
        popd

        pushd {DIR_BUILD}/luarocks/lua_modules/lib/luarocks/rocks-5.1/lapis/1.7.0-1/bin
        cp lapis /sandbox/bin/_lapis.lua
        popd

        pushd '{DIR_BUILD}/luarocks/lua_modules/lib/luarocks/rocks-5.1/moonscript/0.5.0-1/bin'
        cp moon /sandbox/bin/_moon.lua
        cp moonc /sandbox/bin/_moonc.lua
        popd

        """
        self._execute(C)

        self.tools.copyTree(src, "/sandbox/bin/", rsyncdelete=False, recursive=False, overwriteFiles=True)

        self._log_info("install lua & openresty done.")

    @builder_method()
    def sandbox(self, zhub_client=None, reset=False):
        '''Copy built bins to dest_path and create flist if create_flist = True

        :param dest_path: destination path to copy files into
        :type dest_path: str
        :param sandbox_dir: path to sandbox
        :type sandbox_dir: str
        :param reset: reset sandbox file transfer
        :type reset: bool
        :param create_flist: create flist after copying files
        :type create_flist:bool
        :param zhub_client: hub instance to upload flist tos
        :type zhub_client:str
        '''
        dest_path = self.DIR_SANDBOX
        j.builder.web.openresty.sandbox(dest_path=dest_path, reset=reset)

        bins = ['lua', '_lapis.lua', '_moonc.lua', '_moon.lua', '_moonrocks.lua']
        for bin_name in bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin_name)
            dir_dest = self.tools.joinpaths(dest_path, j.core.dirs.BINDIR[1:])
            self.tools.dir_ensure(dir_dest)
            self._copy(dir_src, dir_dest)

        lib_dest = self.tools.joinpaths(dest_path, 'sandbox/lib')
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest, exclude_sys_libs=False)

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
            dir_dest_full = j.sal.fs.getDirName(self.tools.joinpaths(d2, rdest))
            self.tools.dir_ensure(dir_dest_full)
            dest_full = self.tools.joinpaths(d2, rdest)
            self._copy(item, dest_full)

        self.clean()
