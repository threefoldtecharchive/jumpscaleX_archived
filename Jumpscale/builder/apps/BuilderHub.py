from Jumpscale import j
import textwrap

builder_method = j.builders.system.builder_method


class BuilderHub(j.builders.system._BaseClass):
    NAME = "zerohub"

    def _init(self):
        self.build_dir = self.tools.joinpaths(self.DIR_BUILD, "code")
        self.makeopts = "-j 5"
        self.curl_dest = self.tools.joinpaths(self.build_dir, "curl")
        self.capnp_dest = self.tools.joinpaths(self.build_dir, "capnp")
        self.hub_dest = self.tools.joinpaths(self.build_dir, "hub")
        self.zeroflist_dest = self.tools.joinpaths(self.build_dir, "zeroflist")

    @builder_method()
    def clean(self):
        self._remove(self.build_dir)

    @builder_method()
    def reset(self):
        super().reset()
        self.clean()

    @builder_method()
    def build(self):
        # install dependancies
        self.system.package.mdupdate()
        self.system.package.install(
            [
                "build-essential",
                "git",
                "libsnappy-dev",
                "libz-dev",
                "libtar-dev",
                "libb2-dev",
                "autoconf",
                "libtool",
                "libjansson-dev",
                "libhiredis-dev",
                "libsqlite3-dev",
                "tmux",
                "vim",
                "python3-flask",
                "python3-redis",
                "python3-docker",
                "python3-pytoml",
                "python3-jwt",
                "libssl-dev",
            ]
        )
        # zdb backend
        j.builders.db.zdb.install()

        # libcurl build
        curl_url = "https://github.com/curl/curl"
        j.clients.git.pullGitRepo(dest=self.curl_dest, url=curl_url, depth=1, branch="curl-7_62_0")

        curl_cmd = """
        rm -f /usr/local/lib/libcurl.so.*
        cd {curl_dest}
        autoreconf -f -i -s
        ./configure --disable-debug --enable-optimize --disable-curldebug --disable-symbol-hiding --disable-rt \
        --disable-ftp --disable-ldap --disable-ldaps --disable-rtsp --disable-proxy --disable-dict \
        --disable-telnet --disable-tftp --disable-pop3 --disable-imap --disable-smb --disable-smtp --disable-gopher \
        --disable-manual --disable-libcurl-option --disable-sspi --disable-ntlm-wb --without-brotli --without-librtmp --without-winidn \
        --disable-threaded-resolver \
        --with-openssl
        make {makeopts}
        """.format(
            curl_dest=self.curl_dest, makeopts=self.makeopts
        )
        self._execute(curl_cmd)

        # capnp builder
        capnp_url = "https://github.com/opensourcerouting/c-capnproto"
        j.clients.git.pullGitRepo(dest=self.capnp_dest, url=capnp_url, depth=1)

        capnp_cmd = """
        cd {dest}
        git submodule update --init --recursive
        autoreconf -f -i -s
        ./configure
        make {makeopts}
        """.format(
            dest=self.capnp_dest, makeopts=self.makeopts
        )
        self._execute(capnp_cmd)

        # zeroflist
        zeroflist_url = "https://github.com/threefoldtech/0-flist/"
        j.clients.git.pullGitRepo(dest=self.zeroflist_dest, url=zeroflist_url, depth=1, branch="development")

        zeroflist_cmd = """
        cd {}
        pushd libflist
        make
        popd
        pushd zflist
        make production DESTDIR="/sandbox/"
        popd
        cp zflist/zflist /tmp/zflist
        strip -s /tmp/zflist
        """.format(
            self.zeroflist_dest
        )
        self._execute(zeroflist_cmd)

        # hub
        hub_url = "https://github.com/threefoldtech/0-hub"
        j.clients.git.pullGitRepo(dest=self.hub_dest, url=hub_url, depth=1, branch="playground")

    @builder_method()
    def install(self):
        # install curl
        curl_install_cmd = """
            cd {curl_dest}
            make install
            make install DESTDIR="/sandbox/"
            ldconfig
        """.format(
            curl_dest=self.curl_dest
        )
        self._execute(curl_install_cmd)

        # install capnp
        capnp_install_cmd = """
        cd {dest}
        make install
        ldconfig
        """.format(
            dest=self.capnp_dest
        )
        self._execute(capnp_install_cmd)

        # install hub
        hub_cmd = """
        cp {dest}/python/config.py.sample {dest}/python/config.py
        sed -i "s/'authentication': True/'authentication': False/" {dest}/python/config.py
        sed -i "s/'zflist-bin': '\/opt\/0-flist\/zflist\/zflist'/'zflist-bin': \
            '\/tmp\/builders\/zerohub\/code\/zeroflist\/zflist\/zflist'/" {dest}/python/config.py
        sed -i "s/'backend-internal-host': \\"my-zdb-host\\"/'backend-internal-host': \
            \\"127.0.0.1\\"/" {dest}/python/config.py
        """.format(
            dest=self.hub_dest
        )
        self._execute(hub_cmd)

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        sandbox_dir = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox")
        self.tools.dir_ensure(sandbox_dir)
        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox", "bin")
        self.tools.dir_ensure(bin_dest)
        # sandbox zdb
        bins = ["zdb"]
        for bin in bins:
            self._copy("{DIR_BIN}/" + bin, bin_dest)

        lib_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox", "lib")
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self.tools.joinpaths(bin_dest, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest)

        # sandbox curl
        curl_install_cmd = """
            cd {curl_dest}
            make install
            make install DESTDIR={sandbox}
            ldconfig
        """.format(
            curl_dest=self.curl_dest, sandbox=sandbox_dir
        )
        self._execute(curl_install_cmd)

        # sandbox capnp
        capnp_sandbox_cmd = """
        cd {dest}
        make install DESTDIR={sandbox}
        ldconfig
        """.format(
            dest=self.capnp_dest, sandbox=sandbox_dir
        )
        self._execute(capnp_sandbox_cmd)

        # sandbox zflist
        self._copy(self.zeroflist_dest, sandbox_dir)
        # sandbox hub
        self._copy(self.hub_dest, sandbox_dir)

        # install hub
        hub_cmd = """
        cp {sandbox_dir}/python/config.py.sample {sandbox_dir}/python/config.py
        sed -i "s/'authentication': True/'authentication': False/" {sandbox_dir}/python/config.py
        sed -i "s/'zflist-bin': '\/opt\/0-flist\/zflist\/zflist'/'zflist-bin': \
            '\/sandbox\/zeroflist\/zflist\/zflist'/" {sandbox_dir}/python/config.py
        sed -i "s/'backend-internal-host': \\"my-zdb-host\\"/'backend-internal-host': \
            \\"127.0.0.1\\"/" {sandbox_dir}/python/config.py
        """.format(
            sandbox_dir=sandbox_dir
        )
        self._execute(hub_cmd)

        file = self.tools.joinpaths(j.sal.fs.getDirName(__file__), "templates", "zerohub_startup.toml")
        file_dest = self.tools.joinpaths(self.DIR_SANDBOX, ".startup.toml")
        self._copy(file, file_dest)

    @property
    def startup_cmds(self):

        j.builders.db.zdb.start()
        start_script = """
        cd {}/hub/python/ && python3 flist-uploader.py
        """.format(
            self.build_dir
        )
        start_cmd = j.tools.startupcmd.get(self.NAME, cmd=start_script)
        return [start_cmd]

    @builder_method()
    def stop(self):
        # killing the daemon
        j.tools.tmux.pane_get(self.NAME).kill()
        j.builders.db.zdb.stop()

    @builder_method()
    def test(self):
        self.start()
        self.stop()

