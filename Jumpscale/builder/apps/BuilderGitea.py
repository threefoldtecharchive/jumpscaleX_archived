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
        self.CODEDIR = self.GITEAPATH
        self.INIPATH = "%s/conf/app.ini" % self.CUSTOM_PATH

    @builder_method()
    def build(self):
        """Build Gitea with itsyou.online config

        Keyword Arguments:
            reset {bool} -- force build if True (default: {False})
        """
        self._installDeps()
        self.get("code.gitea.io/gitea", install=False)

        # change branch from master to gigforks/iyo_integration
        _, out, _ = self._execute("cd {GITEAPATH} && git remote")
        if "gigforks" not in out:
            self._execute(
                """cd {GITEAPATH}
                git remote add gigforks https://github.com/gigforks/gitea
                git fetch gigforks && git checkout gigforks/iyo_integration
            """
            )

        # gitea-custom is needed to replace the default gitea custom
        j.clients.git.pullGitRepo("https://github.com/incubaid/gitea-custom.git", branch="master")
        if self.tools.exists(self.CUSTOM_PATH) and not self.tools.file_is_link(self.CUSTOM_PATH):
            self.tools.dir_remove(self.CUSTOM_PATH)

        self.tools.file_link(source="/sandbox/code/github/incubaid/gitea-custom", destination=self.CUSTOM_PATH)

        # configure
        self.tools.dir_ensure(self._replace("{CUSTOM_PATH}/conf"))
        self._configure()

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

    def _configure(self):
        """Configure gitea
        Configure: db, iyo
        """

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

    @builder_method()
    def install(self, org_client_id, org_client_secret):
        """Build Gitea with itsyou.online config

        Same as build but exists for standarization sake

        Keyword Arguments:
            reset {bool} -- force build if True (default: {False})
        """
        j.sal.process.killProcessByName("postgres")
        j.builder.db.postgres.start()
        self._execute("sudo -u postgres {DIR_BIN}/psql -c 'create database gitea;'")

        self._execute("sudo -u postgres {DIR_BIN}/psql gitea -c")

        cmd = """
        "INSERT INTO login_source (type, name, is_actived, cfg, created_unix, updated_unix)
        VALUES (6, 'Itsyou.online', TRUE,
        '{\\"Provider\\":\\"itsyou.online\\",\\"ClientID\\":\\"%s\\",\\"ClientSecret\\":\\"%s\\",\\"OpenIDConnectAutoDiscoveryURL\\":\\"\\",\\"CustomURLMapping\\":null}',
        extract('epoch' from CURRENT_TIMESTAMP) , extract('epoch' from CURRENT_TIMESTAMP));"
        """
        cmd = cmd % (org_client_id, org_client_secret)
        cmd = cmd.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        self._execute(cmd)

        self.tools.file_link(self._replace("{GITEAPATH}/gitea"), self.DIR_BIN)

    @property
    def startup_cmds(self):
        cmd = j.tools.startupcmd.get("gitea", "gitea web", path="/sandbox/bin")
        return [cmd]
