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
        """Configure gitea, db, iyo"""
        pass

    @builder_method()
    def install(self):
        """install odoo"""
        j.builders.db.postgres.install()
        j.builders.runtimes.nodejs.install()

        self.tools.dir_ensure(self.APP_DIR)

        # create user and related config
        self._execute(
            """
            id -u odoouser &>/dev/null || (useradd odoouser --home {APP_DIR} --no-create-home --shell /bin/bash
            sudo su - postgres -c "/sandbox/bin/createuser -s odoouser") || true
            chown -R odoouser:odoouser {APP_DIR}
            mkdir -p {APP_DIR}/data
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
        pg_ctl = self._replace("sudo -u odoouser {DIR_BIN}/pg_ctl %s -D {APP_DIR}/data")
        cmd_start = pg_ctl % "start"
        cmd_stop = pg_ctl % "stop"
        postgres_cmd = j.tools.startupcmd.get("postgres-custom", cmd_start, cmd_stop, ports=[5432], path="/sandbox/bin")
        odoo_start = self._replace(
            "sudo -H -u odoouser python3 /sandbox/apps/odoo/odoo/odoo-bin -c {DIR_CFG}/odoo.conf"
        )
        odoo_cmd = j.tools.startupcmd.get("odoo", odoo_start, path="/sandbox/bin")
        return [postgres_cmd, odoo_cmd]
