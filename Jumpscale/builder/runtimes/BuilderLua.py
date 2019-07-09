from Jumpscale import j
from Jumpscale.sal.bash.Profile import Profile

builder_method = j.builders.system.builder_method


class BuilderLua(j.builders.system._BaseClass):

    NAME = "lua"

    def _init(self):
        self.ROCKS_PATHS_PROFILE = self._replace("{DIR_BUILD}/rocks_paths")

    @builder_method()
    def build(self):
        """
        kosmos 'j.builders.runtimes.lua.build()'
        :param install:
        :return:
        """

        if j.core.platformtype.myplatform.isUbuntu:
            j.builders.system.package.install(["libsqlite3-dev"])

        j.builders.web.openresty.build(reset=True)
        j.builders.libs.openssl.build(reset=True)

        url = "https://luarocks.org/releases/luarocks-3.0.4.tar.gz"
        dest = self._replace("{DIR_BUILD}/luarocks")
        self.tools.dir_ensure(dest)
        self.tools.file_download(
            url, to=dest, overwrite=False, retry=3, expand=True, minsizekb=100, removeTopDir=True, deletedest=True
        )
        C = """
        cd {DIR_BUILD}/luarocks
        ./configure --prefix=/sandbox/openresty/luarocks --with-lua=/sandbox/openresty/luajit
        make build
        make install

        cp {DIR_BUILD}/luarocks/luarocks /sandbox/bin/luarocks
        luarocks path > {ROCKS_PATHS_PROFILE}
        """
        # set showout to False to avoid text_replace of output log
        self._execute(C, showout=False)

    def profile_sandbox_set(self):
        # add lua_path and lua_cpath so lua libs/clibs can found by lua interpreter)
        luarocks_profile = Profile(self._bash, self.ROCKS_PATHS_PROFILE)
        lua_path = luarocks_profile.env_get("LUA_PATH")
        lua_cpath = luarocks_profile.env_get("LUA_CPATH")
        self.profile.env_set("LUA_PATH", lua_path)
        self.profile.env_set("LUA_CPATH", lua_cpath)

        # add luarocs path to PATH, so binaries of luarocks packageds can be executed normally
        path = luarocks_profile.env_get("PATH").replace(";", ":")
        self.profile.path_add(path, check_exists=False)

    def lua_rock_install(self, name):
        self._execute("luarocks install %s" % name)

    def lua_rocks_install(self):
        """
        kosmos 'j.builders.runtimes.lua.lua_rocks_install()'
        :param install:
        :return:
        """
        self.profile_sandbox_select()

        if j.core.platformtype.myplatform.isUbuntu:
            # j.builders.system.package.mdupdate()
            j.builders.system.package.ensure("geoip-database,libgeoip-dev")

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
            self.lua_rock_install(line)

        if j.core.platformtype.myplatform.isUbuntu:
            self.lua_rock_install("lua-geoip")
            self.lua_rock_install("lua-resty-jwt")
            self.lua_rock_install("lua-resty-iyo-auth")  # need to check how to get this to work on OSX

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

    @builder_method()
    def clean(self):
        """
        kosmos 'j.builders.runtimes.lua.cleanup()'
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
        rm -rf /sandbox/openresty/luajit/share
        rm -rf /sandbox/var/build
        rm -rf /sandbox/root
        mkdir -p /sandbox/root

        """
        self._execute(C)

    @builder_method()
    def install(self):
        """
        will build & install in sandbox
        kosmos 'j.builders.runtimes.lua.install()'
        :return:
        """
        self.lua_rocks_install()

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None):
        """Copy built bins to dest_path and create flist if create_flist = True

        :param dest_path: destination path to copy files into
        :type dest_path: str
        :param sandbox_dir: path to sandbox
        :type sandbox_dir: str
        :param create_flist: create flist after copying files
        :type create_flist:bool
        :param zhub_client: hub instance to upload flist tos
        :type zhub_client:str
        """
        dest_path = self.DIR_SANDBOX
        j.builders.web.openresty.sandbox(reset=reset)

        bins = ["lua", "_lapis.lua", "_moonc.lua", "_moon.lua", "_moonrocks.lua"]
        for bin_name in bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin_name)
            dir_dest = self.tools.joinpaths(dest_path, j.core.dirs.BINDIR[1:])
            self.tools.dir_ensure(dir_dest)
            self._copy(dir_src, dir_dest)

        lib_dest = self.tools.joinpaths(dest_path, "sandbox/lib")
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest, exclude_sys_libs=False)

    def copy_to_github(self):
        """
        kosmos 'j.builders.runtimes.lua.copy_to_github()'
        :return:
        """
        # assert self.executor.type=="local"
        path = "/sandbox/openresty/lualib"

        if j.core.platformtype.myplatform.isUbuntu:
            destbin = "%s/base/openresty/lualib" % j.clients.git.getContentPathFromURLorPath(
                "git@github.com:threefoldtech/sandbox_ubuntu.git"
            )
        elif j.core.platformtype.myplatform.isMac:
            destbin = "%s/base/openresty/lualib" % j.clients.git.getContentPathFromURLorPath(
                "git@github.com:threefoldtech/sandbox_osx.git"
            )
        else:
            raise RuntimeError("only ubuntu & osx support")

        dest = "%s/base/openresty/lualib" % j.clients.git.getContentPathFromURLorPath(
            "git@github.com:threefoldtech/sandbox_base.git"
        )

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
