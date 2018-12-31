from Jumpscale import j
from .CurrencyLayer import CurrencyLayer


JSConfigFactory = j.application.JSFactoryBaseClass


class CurrencyLayerFactory(JSConfigFactory):

    __jslocation__ = 'j.clients.currencylayer'
    _CHILDCLASS = CurrencyLayer
