from Jumpscale import j
import textwrap

builder_method = j.builders.system.builder_method


class BuilderGraphql(j.builders.system._BaseClass):
    NAME = "graphql"

    def _init(self):
        self.DIR_GRAPHQL_WS = self.tools.joinpaths(self.DIR_BUILD, "graphql_websockets")

    @builder_method()
    def clean(self):
        self.DIR_GRAPHQL_WS = self.tools.joinpaths(self.DIR_BUILD, "graphql_websockets")
        self._remove(self.DIR_GRAPHQL_WS)

    @builder_method()
    def reset(self):
        super().reset()
        self.clean()

    @builder_method()
    def build(self):
        # TODO : Build from source
        graphql_websockets_url = "https://github.com/threefoldfoundation/graphql_websockets"
        j.clients.git.pullGitRepo(dest=self.DIR_GRAPHQL_WS, url=graphql_websockets_url, depth=1)

    @builder_method()
    def install(self):
        # install graphql_ws,sanic, graphene, sanic-graphql
        cmd = """
        cd {DIR_GRAPHQL_WS}
        pip3 install -r requirements.txt -t /sandbox/bin/
        """
        self._execute(cmd)

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        # TODO
        pass

    @property
    def startup_cmds(self):
        j.builders.db.zdb.start()
        start_script = self._replace(
            """
        cd {DIR_GRAPHQL_WS} && python3 app.py
        """
        )
        start_cmd = j.servers.startupcmd.get(self.NAME, cmd=start_script)
        return [start_cmd]

    @builder_method()
    def stop(self):
        # killing the daemon
        j.tools.tmux.pane_get(self.NAME).kill()
        j.builders.db.zdb.stop()

    @builder_method()
    def test(self):
        if self.running():
            self.stop()
        self.start()
        assert self.running()
        self.stop()
        print("TEST OK")
