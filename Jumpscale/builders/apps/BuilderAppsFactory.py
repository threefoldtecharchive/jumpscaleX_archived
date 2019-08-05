from Jumpscale import j


class BuilderAppsFactory(j.builders.system._BaseFactoryClass):

    __jslocation__ = "j.builders.apps"

    def _init(self, **kwargs):
        self._gitea = None
        self._freeflow = None
        self._digitalme = None
        self._userbot = None
        self._odoo = None
        self._corex = None
        self._sonic = None
        self._hub = None
        self._sockexec = None
        self._graphql = None
        self._threebot = None

    @property
    def threebot(self):
        if self._threebot is None:
            from .BuilderThreebot import BuilderThreebot

            self._threebot = BuilderThreebot()
        return self._threebot

    @property
    def sockexec(self):
        if self._sockexec is None:
            from .BuilderSockexec import BuilderSockexec

            self._sockexec = BuilderSockexec()
        return self._sockexec

    @property
    def gitea(self):
        if self._gitea is None:
            from .BuilderGitea import BuilderGitea

            self._gitea = BuilderGitea()
        return self._gitea

    @property
    def freeflow(self):
        if self._freeflow is None:
            from .BuilderFreeflow import BuilderFreeflow

            self._freeflow = BuilderFreeflow()
        return self._freeflow

    @property
    def digitalme(self):
        if self._digitalme is None:
            from .BuilderDigitalME import BuilderDigitalME

            self._digitalme = BuilderDigitalME()
        return self._digitalme

    @property
    def userbot(self):
        if self._userbot is None:
            from .BuilderUserBot import BuilderUserBot

            self._userbot = BuilderUserBot()
        return self._userbot

    @property
    def odoo(self):
        if self._odoo is None:
            from .BuilderOdoo import BuilderOdoo

            self._odoo = BuilderOdoo()
        return self._odoo

    @property
    def corex(self):
        if self._corex is None:
            from .BuilderCoreX import BuilderCoreX

            self._corex = BuilderCoreX()
        return self._corex

    @property
    def sonic(self):
        if self._sonic is None:
            from .BuilderSonic import BuilderSonic

            self._sonic = BuilderSonic()
        return self._sonic
    
    @property
    def hub(self):
        if self._hub is None:
            from .BuilderHub import BuilderHub

            self._hub = BuilderHub()
        return self._hub

    @property
    def graphql(self):
        if self._graphql is None:
            from .BuilderGraphql import BuilderGraphql

            self._graphql = BuilderGraphql()
        return self._graphql
