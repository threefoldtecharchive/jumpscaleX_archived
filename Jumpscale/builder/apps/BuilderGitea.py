import textwrap

from Jumpscale import j
from Jumpscale.builder.runtimes.BuilderGolang import BuilderGolangTools

builder_method = j.builder.system.builder_method


class BuilderGitea(BuilderGolangTools):
    NAME = "gitea"

    def _init(self):
        super()._init()
        # set needed paths
        self.GITEAPATH = self._replace("{DIR_GO_PATH}/src/code.gitea.io/gitea")
        self.CUSTOM_PATH = "%s/custom" % self.GITEAPATH
        # app.ini will be bundled with the binary
        self.INIPATH = "%s/custom/conf/app.ini" % self.DIR_GO_PATH_BIN

    @builder_method()
    def build(self):
        """Build Gitea with itsyou.online authentication"""
        self._installDeps()
        self.get("code.gitea.io/gitea", install=False)

        # change branch from master to gigforks/iyo_integration
        _, out, _ = self._execute("cd {GITEAPATH} && git remote")
        if "gigforks" not in out:
            self._execute(
                """cd {GITEAPATH}
                git remote add gigforks https://github.com/gigforks/gitea
                """
            )

        self._execute("cd {GITEAPATH} && git fetch gigforks && git checkout gigforks/iyo_integration")

        # gitea-custom is needed to replace the default gitea custom
        j.clients.git.pullGitRepo("https://github.com/incubaid/gitea-custom.git", branch="master")
        if self.tools.exists(self.CUSTOM_PATH) and not self.tools.file_is_link(self.CUSTOM_PATH):
            self.tools.dir_remove(self.CUSTOM_PATH)

        self.tools.file_link(source="/sandbox/code/github/incubaid/gitea-custom", destination=self.CUSTOM_PATH)

        # build gitea (will be stored in self.GITEAPATH/gitea)
        self._execute('cd {GITEAPATH} && TAGS="bindata" make generate build')

    def _installDeps(self):
        """Install gitea deps

        sys packages: git-core, gcc, golang
        db: postgresql
        """
        j.builder.system.package.mdupdate()
        j.builder.system.package.ensure("git-core")
        j.builder.system.package.ensure("gcc")
        j.builder.runtimes.golang.install()
        j.builder.db.postgres.install()

    @builder_method()
    def configure(self, org_client_id, org_client_secret):
        """Configure gitea, db, iyo"""

        # Configure Database
        config = """
        RUN_MODE = prod
        [database]
        DB_TYPE  = postgres
        HOST     = localhost:5432
        NAME     = gitea
        USER     = postgres
        PASSWD   = postgres
        SSL_MODE = disable
        PATH     = data/gitea.db
        [security]
        INSTALL_LOCK = true
        [log]
        MODE      = file
        LEVEL     = Info
        """

        config = textwrap.dedent(config)
        self._write(self.INIPATH, config)

        try:
            j.sal.process.killProcessByName("postgres")
            j.sal.process.killProcessByName("gitea")
            self.stop()
        except j.exceptions.RuntimeError:
            # not started
            pass

        self.start()

        _, out, _ = self._execute("sudo -u postgres {DIR_BIN}/psql -l")
        if "gitea" not in out:
            self._execute("sudo -u postgres {DIR_BIN}/psql -c 'create database gitea;'")

        cmd = """
        "INSERT INTO login_source (type, name, is_actived, cfg, created_unix, updated_unix)
        VALUES (6, 'Itsyou.online', TRUE,
                '{{\\"Provider\\":\\"itsyou.online\\",\\"ClientID\\":\\"%s\\",\\"ClientSecret\\":\\"%s\\",\\"OpenIDConnectAutoDiscoveryURL\\":\\"\\",\\"CustomURLMapping\\":null}}',
                extract('epoch' from CURRENT_TIMESTAMP) , extract('epoch' from CURRENT_TIMESTAMP))
        ON CONFLICT (name) DO NOTHING;"
        """
        cmd = cmd % (org_client_id, org_client_secret)
        cmd = cmd.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        self._execute("sudo -u postgres {DIR_BIN}/psql gitea -c %s" % cmd)

    @builder_method()
    def install(self):
        # copy the binary with bundled assets using bindata to $GOPATH/bin
        self._copy("{GITEAPATH}/gitea", "{DIR_GO_PATH}/bin/gitea")

    @property
    def startup_cmds(self):
        cmd = j.tools.startupcmd.get("gitea", "gitea web", path="/sandbox/bin")
        return j.builder.db.postgres.startup_cmds + [cmd]
