import os
from Jumpscale import j
import requests

JSConfigClient = j.application.JSBaseConfigClass


class OdooServer(JSConfigClient):
    _SCHEMATEXT = """
           @url =  jumpscale.odoo.server.1
           name* = "default" (S)
           host = "127.0.0.1" (S)
           port = 8069 (I)
           username="admin"(S)
           admin_secret_ = "admin" (S)
           Email = "bola@incubaid.com" (S)
           timeout = 300
           databases = (LO) !jumpscale.odoo.server.db.1
           
           @url =  jumpscale.odoo.server.db.1
           name* = "user" (S)
           db_secret_ = "123456" (S)
           
           """

    def _init(self, **kwargs):
        self.config_path = j.sal.fs.joinPaths(j.dirs.CFGDIR, "odoo_config_%s.conf" % self.name)
        if self.host == "localhost":
            self.host = " 127.0.0.1"

        self._default_client = None
        self._database = None
        self._postgres_cmd = j.servers.startupcmd.get("postgres-custom")
        self._odoo_cmd = j.servers.startupcmd.get("odoo")

    def start(self, module_name=None):
        """
        Starts odoo server in tmux
        """
        self._write_config()
        for server in self.startupcmd:
            server.start()

    @property
    def _path(self):
        p = "%s/odoo_db/%s" % (j.core.myenv.config["DIR_VAR"], self.name)
        j.sal.fs.createDir(p)
        return p

    @property
    def database(self):
        if not self._database:
            self._database = self.databases.new()
        return self._database

    def _write_config(self):
        cfg_template = j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), "odoo_config.conf")
        self._database = self.databases.new()
        args = {
            "email": self.Email,
            "host": self.host,
            "port": self.port,
            "admin_password": self.admin_secret_,
            "db_secret": self._database.db_secret_,
            "db_name": self._database.name,
        }
        j.tools.jinja2.file_render(path=cfg_template, dest=self.config_path, **args)
        return self.config_path

    @property
    def default_client(self):
        if not self._default_client:
            self._default_client = j.clients.odoo.get(
                name="default", host=self.host, port=self.port, secret_=self.secret_
            )
            self._default_client.save()
        return self._default_client

    def databases_reset(self, db_name=None):
        """
        remove all databases
        :return:
        """
        API_DROP = "http://{}:{}/web/database/drop".format(self.host, self.port)
        if db_name:
            data = {"master_pwd": self.database.db_secret_, "name": db_name}
            res = requests.post(url=API_DROP, data=data)
        else:
            for db in self.databases_list():
                data = {"master_pwd": self.database.db_secret_, "name": db}
                res = requests.post(url=API_DROP, data=data)
        return res

    def databases_list(self):
        """
        list databases from postgresql
        :return:
        """
        client = j.clients.odoo.get(
            host=self.host,
            port=self.port,
            username=self.username,
            password_=self.admin_secret_,
            database=self.database.name,
        )
        dbs = client.databases_list()
        return dbs

    def databases_create(self, name, email, password, phone, lang="en_US", country_code="eg", reset=True):
        """
        remove the database if reset=True
        create db in postgresql
        set admin passwd

        :return:
        """
        API_CREATE = "http://{}:{}/web/database/create".format(self.host, self.port)
        data = {
            "master_pwd": self.database.db_secret_,
            "name": name,
            "login": email,
            "password": password,
            "phone": phone,
            "lang": lang,
            "country_code": country_code,
        }
        res = requests.post(url=API_CREATE, data=data)
        if b"already exists" in res.content:
            raise RuntimeError("it's already exist")
        return True

    def _database_obj_get(self, name):
        for db in self.databases_list():
            if db == name:
                return db
        raise RuntimeError("could not find database :%s" % name)

    def database_export(self, name, dest=None):
        BACKUP_API = "http://{}:{}/web/database/backup".format(self.host, self.port)
        data = {"master_pwd": self.database.db_secret_, "name": name, "backup_format": "zip"}
        res = requests.post(url=BACKUP_API, data=data, stream=True)
        if not dest:
            dest = j.core.tools.text_replace("{DIR_VAR}/odoo/exports/%s" % self._database.name)
            j.sal.fs.createDir(dest)

        with open(dest + "%s.zip" % name, "wb") as f:
            for c in res.iter_content():
                f.write(c)
        return dest + "%s.zip" % name

    def database_import(self, name, dest=None, copy=False):
        IMPORT_API = "http://{}:{}/web/database/restore".format(self.host, self.port)

        if not dest:
            dest = j.core.tools.text_replace("{DIR_VAR}/odoo/exports/%s" % self.database.name)
            dest += "%s.zip" % name
            # CHECK DIR EXISTS
            # look for newest one
        data = {"master_pwd": self.database.db_secret_, "backup_file": dest, "name": name, "copy": copy}
        res = requests.post(url=IMPORT_API, data=data)
        return res

    def stop(self):
        self._log_info("stop odoo server")
        for server in self.startupcmd:
            server.stop()

    @property
    def startupcmd(self):

        cmd = "sudo -H -u odoouser python3 /sandbox/apps/odoo/odoo/odoo-bin -c {}".format(self.config_path)

        self._odoo_cmd.cmd_start = cmd
        self._odoo_cmd.process_strings = "/sandbox/apps/odoo/odoo/odoo-bin -c"
        self._odoo_cmd.path = "/sandbox/bin"

        pg_ctl = "sudo -u odoouser /sandbox/bin/pg_ctl %s -D /sandbox/apps/odoo/data"
        cmd_start = pg_ctl % "start"
        cmd_stop = pg_ctl % "stop"

        self._postgres_cmd.cmd_start = cmd_start
        self._postgres_cmd.cmd_stop = cmd_stop
        self._postgres_cmd.ports = [5432]
        self._postgres_cmd.path = "/sandbox/bin"
        return [self._odoo_cmd, self._postgres_cmd]
