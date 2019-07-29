from Jumpscale import j
from .OdooClient import OdooClient

JSConfigs = j.application.JSBaseConfigsClass


class OdooFactory(JSConfigs):

    __jslocation__ = "j.clients.odoo"
    _CHILDCLASS = OdooClient

