from Jumpscale import j


class BuilderRuntimesFactory(j.application.JSBaseClass):

    __jslocation__ = "j.builders.runtimes"

    def _init(self, **kwargs):
        #
        self._python = None
        self._php = None
        self._lua = None
        self._golang = None
        self._nimlang = None
        self._rust = None
        self._nodejs = None

    @property
    def python(self):
        if self._python is None:
            from .BuilderPython import BuilderPython

            self._python = BuilderPython()
        return self._python

    @property
    def php(self):
        if self._php is None:
            from .BuilderPHP import BuilderPHP

            self._php = BuilderPHP()
        return self._php

    @property
    def lua(self):
        if self._lua is None:
            from .BuilderLua import BuilderLua

            self._lua = BuilderLua()
        return self._lua

    @property
    def golang(self):
        if self._golang is None:
            from .BuilderGolang import BuilderGolang

            self._golang = BuilderGolang()
        return self._golang

    @property
    def nimlang(self):
        if self._nimlang is None:
            from .BuilderNIM import BuilderNIM

            self._nimlang = BuilderNIM()
        return self._nimlang

    @property
    def rust(self):
        if self._rust is None:
            from .BuilderRust import BuilderRust

            self._rust = BuilderRust()
        return self._rust

    @property
    def nodejs(self):
        if self._nodejs is None:
            from .BuilderNodeJS import BuilderNodeJS

            self._nodejs = BuilderNodeJS()
        return self._nodejs
