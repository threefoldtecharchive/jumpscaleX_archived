from Jumpscale import j




class BuilderPostgresql(j.builder.system._BaseClass):
    NAME = "psql"

    def _init(self):
        self.BUILD_DIR = '{DIR_TEMP}/postgresql'
        self.passwd = "postgres"
        self.dbdir = "{DIR_VAR}/postgresqldb"

    def build(self, beta=False, reset=False):
        """
        beta is 2 for 10 release
        """
        if self._done_check("build", reset):
            return

        if beta:
            postgres_url = 'https://ftp.postgresql.org/pub/source/v10beta2/postgresql-10beta3.tar.bz2'
        else:
            postgres_url = 'https://ftp.postgresql.org/pub/source/v9.6.3/postgresql-9.6.3.tar.gz'
        j.builder.tools.file_download(
            postgres_url, overwrite=False, to=self.BUILD_DIR, expand=True, removeTopDir=True)
        j.builder.tools.dir_ensure("{DIR_BASE}/apps/pgsql")
        j.builder.tools.dir_ensure("{DIR_BIN}")
        j.builder.tools.dir_ensure("$LIBDIR/postgres")
        j.builder.tools.package_install(
            ['build-essential', 'zlib1g-dev', 'libreadline-dev'])
        cmd = """
        cd {}
        ./configure --prefix={DIR_BASE}/apps/pgsql --bindir={DIR_BIN} --sysconfdir=$CFGDIR --libdir=$LIBDIR/postgres --datarootdir={DIR_BASE}/apps/pgsql/share
        make
        """.format(self.BUILD_DIR)
        j.builder.tools.execute_bash(cmd, profile=True)
        self._done_set('build')

    def _group_exists(self, groupname):
        return groupname in j.builder.tools.file_read("/etc/group")

    def install(self, reset=False, start=False, port=5432, beta=False):
        if self._done_check("install", reset):
            return
        self.build(beta=beta, reset=reset)
        cmd = """
        cd {build_dir}
        make install with-pgport={port}
        """.format(build_dir=self.BUILD_DIR, port=port)
        j.builder.tools.dir_ensure(self.dbdir)
        j.builder.tools.execute_bash(cmd, profile=True)
        if not self._group_exists("postgres"):
            j.sal.process.execute('adduser --system --quiet --home $LIBDIR/postgres --no-create-home \
        --shell /bin/bash --group --gecos "PostgreSQL administrator" postgres')
        c = """
        cd {DIR_BASE}/apps/pgsql
        mkdir -p data
        mkdir -p log
        chown -R postgres {DIR_BASE}/apps/pgsql/
        chown -R postgres {postgresdbdir}
        sudo -u postgres {DIR_BIN}/initdb -D {postgresdbdir} --no-locale
        echo "\nlocal   all             postgres                                md5\n" >> {postgresdbdir}/pg_hba.conf
        """.format(postgresdbdir=self.dbdir)

        # NOTE pg_hba.conf uses the default trust configurations.
        j.builder.tools.execute_bash(c, profile=True)
        if start:
            self.start()

    def configure(self, passwd, dbdir=None):
        """
        #TODO
        if dbdir none then {DIR_VAR}/postgresqldb/
        """
        if dbdir is not None:
            self.dbdir = dbdir
        self.passwd = passwd

    def start(self):
        """
        Starts postgresql database server and changes the postgres user's password to password set in configure method or using the default `postgres` password
        """
        cmd = """
        chown postgres {DIR_BASE}/apps/pgsql/log/
        """

        j.builder.tools.execute_bash(cmd, profile=True)

        cmdpostgres = "sudo -u postgres {DIR_BIN}/postgres -D {postgresdbdir}".format(
            postgresdbdir=self.dbdir)
        pm = j.builder.system.processmanager.get()
        pm.ensure(name="postgres", cmd=cmdpostgres,
                  env={}, path="", autostart=True)

        # make sure postgres is ready
        import time
        timeout = time.time() + 10
        while True:
            rc, out, err = j.sal.process.execute(
                "sudo -H -u postgres {DIR_BIN}/pg_isready", die=False)
            if time.time() > timeout:
                raise j.exceptions.Timeout("Postgres isn't ready")
            if rc == 0:
                break
            time.sleep(2)

        # change password
        cmd = """
        sudo -u postgres {DIR_BIN}/psql -c "ALTER USER postgres WITH PASSWORD '{passwd}'";
        """.format(passwd=self.passwd)
        j.builder.tools.execute_bash(cmd, profile=True)
        print("user: {}, password: {}".format("postgres", self.passwd))

    def stop(self):
        j.builder.system.process.kill("postgres")
