import os
import fakeredis
from Jumpscale import j
from .NACL import NACL

JSBASE = j.application.JSBaseClass


class NACLFactory(j.application.JSBaseClass):

    def __init__(self):
        JSBASE.__init__(self)
        self.__jslocation__ = "j.data.nacl"
        self._default = None

        # check there is core redis
        if isinstance(j.core.db, fakeredis.FakeStrictRedis):
            j.clients.redis.core_get()

    def reset(self, name="default", privkey=None, secret=None, interactive=True):
        """
        removes the default private key & secret, be careful this will make your local data non accessible
        unless if you have your secret and key
        :return:
        """
        msg = """
        removes your private key & secret, be careful this will make your local data non accessible
        unless if you have your secret and key
        """
        if interactive:
            print(j.core.text.strip(msg))
            if not j.tools.console.askYesNo("Are you sure you want to erase your private key & secret for %s" % name):
                return

        NACL(name, privkey=privkey, secret=secret, reset=True, interactive=interactive)

    def get(self, name="default", privkey=None, secret=None):
        """
        """
        if not secret:
            secret = os.environ.get('NACL_SECRET')
        interactive = not bool(secret)
        return NACL(name, privkey=privkey, secret=secret, interactive=interactive)

    @property
    def default(self):
        if self._default is None:
            self._default = self.get()
        return self._default

    def test(self):
        """
        js_shell 'j.data.nacl.test()'
        """
        cl = self.get('test', secret=b'qwerty')  # get's the default location & generate's keys

        data = b"something"
        r = cl.sign(data)

        assert cl.verify(data, r)
        assert cl.verify(b"a", r) == False

        pubsignkey32 = cl.signingkey_pub.encode()

        assert cl.verify(data, r, pubsignkey32)

        a = cl.encryptSymmetric("something")
        b = cl.decryptSymmetric(a)

        assert b == b"something"

        a = cl.encryptSymmetric("something")
        b = cl.decryptSymmetric(a)
        assert b == b"something"

        a = cl.encryptSymmetric("something")
        b = cl.decryptSymmetric(a)
        assert b == b"something"

        a = cl.encryptSymmetric(b"something")
        b = cl.decryptSymmetric(a)
        assert b == b"something"

        # now with hex
        a = cl.encryptSymmetric(b"something", hex=True)
        b = cl.decryptSymmetric(a, hex=True)
        assert b == b"something"

        a = cl.encrypt(b"something")
        b = cl.decrypt(a)

        assert b == b"something"

        a = cl.encrypt("something")  # non binary start
        b = cl.decrypt(a)

        # now with hex
        a = cl.encrypt("something", hex=True)  # non binary start
        b = cl.decrypt(a, hex=True)
        assert b == b"something"

        self._log_info("TEST OK")

    def test_perf(self):
        """
        js_shell 'j.data.nacl.test_perf()'
        """

        cl = self.get('test', secret=b"qwerty")  # get's the default location & generate's keys
        data = b"something"

        nr = 10000
        j.tools.timer.start("signing")
        for i in range(nr):
            p = str(i).encode()
            r = cl.sign(data + p)
        j.tools.timer.stop(i)

        nr = 10000
        j.tools.timer.start("encode and verify")
        for i in range(nr):
            p = str(i).encode()
            r = cl.sign(data + p)
            assert cl.verify(data + p, r)
        j.tools.timer.stop(i)

        nr = 10000
        data2 = data * 20
        j.tools.timer.start("encryption/decryption assymetric")
        for i in range(nr):
            a = cl.encrypt(data2)
            b = cl.decrypt(a)
            assert data2 == b
        j.tools.timer.stop(i)

        nr = 40000
        secret = b"something111"
        data2 = data * 20
        j.tools.timer.start("encryption/decryption symmetric")
        for i in range(nr):
            a = cl.encryptSymmetric(data2)
            b = cl.decryptSymmetric(a)
            assert data2 == b
        j.tools.timer.stop(i)
