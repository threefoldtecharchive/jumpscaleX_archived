import textwrap

from Jumpscale import j

builder_method = j.builders.system.builder_method

# /tmp is the default directory for postgres unix socket
SIMPLE_CFG = """
[options]
admin_passwd = admin
db_host = /tmp
db_user = odoouser"""


class BuilderOdoo(j.builders.system._BaseClass):
    NAME = "odoo"

    def _init(self):
        self.VERSION = "12.0"
        self.APP_DIR = self._replace("{DIR_BASE}/apps/odoo")

    @builder_method()
    def configure(self):
        pass

    @builder_method()
    def install(self):
        """
        kosmos 'j.builders.apps.odoo.install()'
        install odoo
        """
        j.builders.db.postgres.install()
        j.builders.runtimes.nodejs.install()

        self.tools.dir_ensure(self.APP_DIR)

        # create user and related config
        self._execute(
            """
            id -u odoouser &>/dev/null || (useradd odoouser --home {APP_DIR} --no-create-home --shell /bin/bash
            sudo su - postgres -c "/sandbox/bin/createuser -s odoouser") || true
            mkdir -p {APP_DIR}/data
            chown -R odoouser:odoouser {APP_DIR}
            sudo -H -u odoouser /sandbox/bin/initdb -D {APP_DIR}/data || true
        """
        )

        j.builders.system.package.install(
            "sudo libxml2-dev libxslt1-dev libsasl2-dev python3-dev libldap2-dev libssl-dev"
        )

        self._execute(
            """
        cd {APP_DIR}

        if [ ! -d odoo/.git ]; then
            git clone https://github.com/odoo/odoo.git -b {VERSION} --depth=1
        fi

        cd odoo
        sudo -H -u odoouser python3 -m pip install --user -r requirements.txt
        chmod +x odoo-bin
        """
        )

        self._write("{DIR_CFG}/odoo.conf", SIMPLE_CFG)
        j.builders.runtimes.nodejs.npm_install("rtlcss")

    @property
    def startup_cmds(self):
        # run the db with the same user when running odoo server
        pg_ctl = self._replace("sudo -u odoouser {DIR_BIN}/pg_ctl %s -D {APP_DIR}/data")
        # WHY DONT WE USE POSTGRESQL START ON THAT BUILDER?
        cmd_start = pg_ctl % "start"
        cmd_stop = pg_ctl % "stop"
        postgres_cmd = j.servers.startupcmd.get(
            "postgres-custom", cmd_start, cmd_stop, ports=[5432], path="/sandbox/bin"
        )
        odoo_start = self._replace(
            "sudo -H -u odoouser python3 /sandbox/apps/odoo/odoo/odoo-bin -c {DIR_CFG}/odoo.conf"
        )
        odoo_cmd = j.servers.startupcmd.get(
            "odoo", odoo_start, process_strings=["/sandbox/apps/odoo/odoo/odoo-bin -c"], path="/sandbox/bin"
        )
        return [postgres_cmd, odoo_cmd]
