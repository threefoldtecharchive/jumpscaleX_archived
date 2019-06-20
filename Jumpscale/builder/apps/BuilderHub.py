from Jumpscale import j
import textwrap

builder_method = j.builders.system.builder_method


class BuilderHub(j.builders.system._BaseClass):
    NAME = "zerohub"

    CaddyFile = """
    0.0.0.0:80

    timeouts 30m

    log stdout
    root public

    oauth {
        client_id       {$CLIENT_ID}
        client_secret   {$CLIENT_SECRET}
        redirect_url    http://{$IP_PORT}/iyo_callback

        authentication_required    /upload
        authentication_required    /upload-flist
        authentication_required    /merge
        authentication_required    /docker-convert
        authentication_required    /api/flist/me

        api_base_path /api/flist/me
        logout_url /logout

        forward_payload
        refreshable
    }

    proxy / 127.0.0.1:5555 {
	    except /static
    }

    """

    @builder_method()
    def install(self, reset=False):

        self.HUB_PATH = "/tmp"
        if self._done_check("install") and reset is False:
            return

        create_hub = """
        mkdir -p /hub
        rm -f /usr/local/lib/libcurl.so.4
        """
        j.builders.tools.execute(create_hub)

        j.builders.db.zdb.install()
        j.builders.tools.file_download("https://download.grid.tf/caddy-build/caddy", "/sandbox/bin/caddy")
        j.builders.tools.file_download(
            "https://raw.githubusercontent.com/threefoldtech/0-hub/master/deployment/deploy.sh", "/tmp/deploy.sh"
        )

        install_hub = """
        chmod +x /sandbox/bin/caddy
        bash /tmp/deploy.sh /hub
        """
        j.builders.tools.execute(install_hub)

        j.sal.fs.writeFile("/hub/Caddyfile", self.CaddyFile)
        file = self.tools.joinpaths(j.sal.fs.getDirName(__file__), "templates", "config_hub.py")
        file_dest = self.tools.joinpaths("/hub/python/", "config.py")
        self._copy(file, file_dest)
        self._done_set("install")

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox", "bin")
        self.tools.dir_ensure(bin_dest)
        bins = ["caddy", "zdb"]
        for bin in bins:
            self._copy("{DIR_BIN}/" + bin, bin_dest)

        lib_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox", "lib")
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self.tools.joinpaths(bin_dest, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest)

        self.tools.dir_ensure("/hub")
        self._copy("/hub", self.DIR_SANDBOX + "/hub")
        self.tools.dir_ensure("/opt")
        self._copy("/opt", self.DIR_SANDBOX + "/opt")
        file = self.tools.joinpaths(j.sal.fs.getDirName(__file__), "templates", "zerohub_startup.toml")
        file_dest = self.tools.joinpaths(self.DIR_SANDBOX, ".startup.toml")
        self._copy(file, file_dest)
        self._done_set("sandbox")

    @property
    def startup_cmds(self):

        j.builders.db.zdb.start()

        caddy_script = """
        caddy --conf /hub/Caddyfile
        """

        start_script = """
        cd /hub/python/ && python3 flist-uploader.py
        """
        caddy_cmd = j.tools.startupcmd.get(self.NAME + "_caddy", cmd=caddy_script)
        start_cmd = j.tools.startupcmd.get(self.NAME, cmd=start_script)
        return [start_cmd, caddy_cmd]

    def stop(self):
        # killing the daemon
        j.tools.tmux.pane_get(self.NAME).kill()
        j.tools.tmux.pane_get(self.NAME + "_caddy").kill()
        j.builders.db.zdb.stop()

    def test(self):
        self.start()
        self.stop()
