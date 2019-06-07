from Jumpscale import j


class BuilderLibsFactory(j.builders.system._BaseFactoryClass):

    __jslocation__ = "j.builders.libs"

    def _init(self):
        self._openssl = None
        self._capnp = None
        self._cmake = None
        self._brotli = None
        self._libffi = None

    @property
    def openssl(self):
        if self._openssl is None:
            from .BuilderOpenSSL import BuilderOpenSSL

            self._openssl = BuilderOpenSSL()
        return self._openssl

    @property
    def capnp(self):
        if self._capnp is None:
            from .BuilderCapnp import BuilderCapnp

            self._capnp = BuilderCapnp()
        return self._capnp

    @property
    def cmake(self):
        if self._cmake is None:
            from .BuilderCmake import BuilderCmake

            self._cmake = BuilderCmake()
        return self._cmake

    @property
    def brotli(self):
        if self._brotli is None:
            from .BuilderBrotli import BuilderBrotli

            self._brotli = BuilderBrotli()
        return self._brotli

    @property
    def libffi(self):
        if self._libffi is None:
            from .BuilderLibffi import BuilderLibffi

            self._libffi = BuilderLibffi()
        return self._libffi
