

from Jumpscale import j

from .BuilderBaseClass import *
from .BuilderBaseFactoryClass import BuilderBaseFactoryClass


class BuilderSystemPackage(j.application.JSBaseClass):

    __jslocation__ = "j.builder.system"
    _BaseClass = BuilderBaseClass
    # BaseClass property shouldn't start with underscore but we will keep it for backward compatibility
    BaseClass = _BaseClass
    _BaseFactoryClass = BuilderBaseFactoryClass
    builder_method = builder_method

    def _init(self):
        self._package = None
        self._python_pip = None
        self._ns = None
        self._net = None
        self._process = None
        self._ssh = None
        self._user = None

        j.clients.redis.core_get()

    @property
    def package(self):
        if self._package is None:
            from .BuilderSystemPackage import BuilderSystemPackage
            self._package = BuilderSystemPackage()
        return self._package


    @property
    def python_pip(self):
        if self._python_pip is None:
            from .BuilderSystemPIP import BuilderSystemPIP
            self._python_pip = BuilderSystemPIP()
        return self._python_pip

    @property
    def ns(self):
        if self._ns is None:
            from .BuilderNS import BuilderNS
            self._ns = BuilderNS()
        return self._ns

    @property
    def net(self):
        if self._net is None:
            from .BuilderNet import BuilderNet
            self._net = BuilderNet()
        return self._net

    @property
    def process(self):
        if self._process is None:
            from .BuilderProcess import BuilderProcess
            self._process = BuilderProcess()
        return self._process

    @property
    def ssh(self):
        if self._ssh is None:
            from .BuilderSSH import BuilderSSH
            self._ssh = BuilderSSH()
        return self._ssh

    @property
    def user(self):
        if self._user is None:
            from .BuilderUser import BuilderUser
            self._user = BuilderUser()
        return self._user
