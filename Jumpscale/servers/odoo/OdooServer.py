import os
from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass


class OdooServer(JSConfigClient):
    _SCHEMATEXT = """
           @url =  jumpscale.odoo.server.1
           name* = "default" (S)
           host = "127.0.0.1" (S)
           port = 8080 (I)
           secret_ = "123456" (S)
           timeout = 300
           databases = (LO) !jumpscale.odoo.server.db.1
           
           @url =  jumpscale.odoo.server.db.1
           name* = "default" (S)
           secret_ = "123456" (S)
           
           """

    def _init(self, **kwargs):
        self.config_path = j.sal.fs.joinPaths(j.dirs.CFGDIR, "odoo_config_%s.cfg" % self.name)
        if self.host == "localhost":
            self.host = "127.0.0.1"

        self._default_client = None

    def start(self):
        """
        Starts odoo server in tmux
        """
        self._write_config()
        self.startupcmd.start()

    @property
    def _path(self):
        p = "%s/odoo_db/%s" % (j.core.myenv.config["DIR_VAR"], self.name)
        j.sal.fs.createDir(p)
        return p

    def _write_config(self):
        cfg_template = j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), "odoo_config.cfg")
        args = {
            "host": self.host,
            "port": self.port,
            "secret_": self.secret_,
            "timeout": self.timeout,
            "datapath": self._path,
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

    def databases_reset(self):
        """
        remove all databases
        :return:
        """
        pass

    def databases_list(self):
        """
        list databases from postgresql
        :return:
        """
        raise RuntimeError()  # TODO

    def databases_create(self, reset=True):
        """
        remove the database if reset=True
        create db in postgresql
        set admin passwd

        :return:
        """

        if reset:
            self.databases_reset()
        for db in self.databases:
            if not db.name in self.databases_list():
                # means does not exist yet, need to create
                raise RuntimeError()  # TODO

    def _database_obj_get(self, name):
        for db in self.databases:
            if db.name == name:
                return db
        raise RuntimeError("could not find database :%s" % name)

    def database_export(self, name, dest=None):
        db = self._database_obj_get(name)
        if not dest:
            dest = j.core.tools.text_replace("{DIR_VAR}/odoo/exports/%s" % db.name)
            j.sal.fs.createDir(dest)
            dest = dest + "/%s.tgz" % humantime
        raise RuntimeError()  # TODO

    def database_import(self, name, dest=None):
        db = self._database_obj_get(name)
        if not dest:
            dest = j.core.tools.text_replace("{DIR_VAR}/odoo/exports/%s" % db.name)
            # CHECK DIR EXISTS
            # look for newest one
        raise RuntimeError()  # TODO

    def stop(self):
        self._log_info("stop odoo server")
        self.startupcmd.stop()

    @property
    def startupcmd(self):
        cmd = "odoo -c {}".format(self.config_path)
        return j.servers.startupcmd.get(name="Odoo", cmd_start=cmd, ports=[self.port])
