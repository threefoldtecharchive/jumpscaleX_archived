from Jumpscale import j

try:
    import odoolib
except:
    j.builders.runtimes.python.pip_package_install("odoo-client-lib")
    import odoolib


JSConfigBase = j.application.JSBaseConfigClass


class OdooClient(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.odoo.client
    name* = "" (S)
    host = "" (S)
    username="" (S)
    password_ = "" (S)
    database = "" (S)
    """

    def _init(self, **kwargs):
        self.connection = odoolib.get_connection(
            hostname=self.host, database=self.database, login=self.username, password=self.password_
        )
        self.server = j.servers.odoo.get(name=self.name, host=self.host, admin_secret_=self.password_)

    def install_module(self, module_name):
        return self.server._install_module(module_name)

