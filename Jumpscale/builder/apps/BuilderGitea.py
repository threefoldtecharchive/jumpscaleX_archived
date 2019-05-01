from Jumpscale import j
import textwrap


class BuilderGitea(j.builder.system._BaseClass):
    NAME = "gitea"

    def _init(self):
        self._gogspath = str()
        self._gopath = str()
        self._appini = str()

    @property
    def GOPATH(self):
        return j.builder.runtimes.golang.GOPATH

    def build(self, reset=False):
        """Build Gitea with itsyou.online config

        Keyword Arguments:
            reset {bool} -- force build if True (default: {False})
        """

        # set needed paths
        self.GITEAPATH = j.core.tools.text_replace('{}/src/code.gitea.io/gitea'.format(self.GOPATH))
        self.CUSTOM_PATH = j.core.tools.text_replace('%s/custom' % self.GITEAPATH)
        self.CODEDIR = self.GITEAPATH
        self.INIPATH = j.core.tools.text_replace('%s/conf/app.ini' % self.CUSTOM_PATH)
        if self._done_check('build', reset):
            return

        self._installDeps()
        j.builder.runtimes.golang.get('code.gitea.io/gitea')

        # change branch from master to gigforks/iyo_integration
        j.sal.process.execute('cd %s && git remote add gigforks https://github.com/gigforks/gitea' % self.GITEAPATH,
                             profile=True)
        j.sal.process.execute('cd %s && git fetch gigforks && git checkout gigforks/iyo_integration' % self.GITEAPATH,
                             profile=True, timeout=1200)

        # gitea-custom is needed to replace the default gitea custom
        j.clients.git.pullGitRepo("https://github.com/incubaid/gitea-custom.git", branch="master")
        if not j.builder.tools.file_is_link(self.CUSTOM_PATH):
            j.builder.tools.dir_remove(self.CUSTOM_PATH)

        j.builder.tools.file_link(source='/sandbox/code/github/incubaid/gitea-custom',
                                   destination=self.CUSTOM_PATH)

        self._configure()

        # build gitea (will be stored in self.GITEAPATH/gitea)
        j.sal.process.execute('cd %s && TAGS="bindata" make generate build' % self.GITEAPATH, profile=True,
                             timeout=1200)
        self._done_set('build')

    def _installDeps(self):
        """Install gitea deps

        sys packages: git-core, gcc, golang
        db: postgresql
        """

        j.builder.system.package.mdupdate()
       j.builder.system.package.ensure('git-core')
       j.builder.system.package.ensure('gcc')
        j.builder.runtimes.golang.install()
        j.builder.db.postgresql.install()

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
        j.sal.fs.writeFile(location=self.INIPATH,
                                    content=config)

    def install(self, org_client_id, org_client_secret, reset=False, start=False):
        """Build Gitea with itsyou.online config

        Same as build but exists for standarization sake

        Keyword Arguments:
            reset {bool} -- force build if True (default: {False})
        """

        self.build(reset=reset)
        if not j.builder.db.postgresql.isStarted():
            j.builder.db.postgresql.start()

        # # Create postgres db  : #TODO:*1 this should be part of the postgresql prefab module
        j.sal.process.execute('sudo -u postgres /opt/bin/psql -c \'create database gitea;\'', die=False)
        self.start()
        cmd = """
        sudo -u postgres /opt/bin/psql gitea -c
        "INSERT INTO login_source (type, name, is_actived, cfg, created_unix, updated_unix)
        VALUES (6, 'Itsyou.online', TRUE,
        '{\\"Provider\\":\\"itsyou.online\\",\\"ClientID\\":\\"%s\\",\\"ClientSecret\\":\\"%s\\",\\"OpenIDConnectAutoDiscoveryURL\\":\\"\\",\\"CustomURLMapping\\":null}',
        extract('epoch' from CURRENT_TIMESTAMP) , extract('epoch' from CURRENT_TIMESTAMP));"
        """
        cmd = cmd % (org_client_id, org_client_secret)
        cmd = cmd.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        j.sal.process.execute(cmd)
        if not start:
            self.stop()
            j.builder.db.postgresql.stop()

    def start(self, name='main'):
        """Start GITEA server instance

        Keyword Arguments:
            name {string} -- name of the server instance (default: {'main'})
        """
        if not j.builder.db.postgresql.isStarted():
            j.builder.db.postgresql.start()
        cmd = '{giteapath}/gitea web'.format(giteapath=self.GITEAPATH)
        pm = j.builder.system.processmanager.get()
        pm.ensure(name='gitea_%s' % name, cmd=cmd)

    def stop(self, name='main'):
        """Stop GITEA server instance

        Keyword Arguments:
            name {string} -- name of the server instance (default: {'main'})
        """

        pm = j.builder.system.processmanager.get()
        pm.stop('gitea_%s' % name)

    def restart(self, name='main'):
        """Stop GITEA server instance

        Keyword Arguments:
            name {string} -- name of the server instance (default: {'main'})
        """
        pm = j.builder.system.processmanager.get()
        pm.stop('gitea_%s' % name)
        self.start(name)

    def reset(self):
        """
        helper method to clean what this module generates.
        """
        super().reset()
        j.sal.fs.remove(self.CODEDIR)
        self._init()
