from Jumpscale import j


class BuilderAppsFactory(j.builders.system._BaseFactoryClass):

    __jslocation__ = "j.builders.apps"

    def _init(self):
        self._gitea = None
        self._freeflow = None
        self._digitalme = None
        self._userbot = None
        self._odoo = None
        self._corex = None

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
<<<<<<< HEAD
    def odoo(self):
        if self._odoo is None:
            from .BuilderOdoo import BuilderOdoo

            self._odoo = BuilderOdoo()
        return self._odoo
=======
    def corex(self):
        if self._corex is None:
            from .BuilderCoreX import BuilderCoreX

            self._corex = BuilderCoreX()
        return self._corex
>>>>>>> dbb55742833c7d13b8ea12c1434a66b6a9b9eac2
