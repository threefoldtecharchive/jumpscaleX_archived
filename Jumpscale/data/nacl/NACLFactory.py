from Jumpscale import j

from .NACL import NACL
import nacl.secret
import nacl.utils
import base64
import hashlib
from nacl.public import PrivateKey, SealedBox

JSBASE = j.application.JSBaseClass

class NACLFactory(j.application.JSBaseClass):

    def __init__(self):
        JSBASE.__init__(self)
        self.__jslocation__ = "j.data.nacl"
        self._default = None

    def secret_set(self,secret):
        """
        the secret passphrase for the private key
        will be stored encrypted in the system redis
        :param secret:
        :return:
        """
        secret=self._hash(secret)
        self._secret_get(secret=secret)

    def _hash(self,data):
        m = hashlib.sha256()
        if not j.data.types.bytes.check(data):
            data = data.encode()
        m.update(data)
        return m.digest()

    def _secret_get(self,secret=None):
        path="{DIR_VAR}/dummy.log"
        if not j.sal.fs.exists(path):
            key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            j.sal.fs.writeFile(path,key)
        else:
            key = j.sal.fs.readFile(path,binary=True)
        sb=nacl.secret.SecretBox(key)
        r = j.core.db.get("secret")
        if r is None or secret is not None:
            if secret is None:
                secret=j.tools.console.askPassword("your secret passwd for your private key")
                secret=self._hash(secret)
            r = sb.encrypt(secret)
            j.core.db.set("secret",r)
        return sb.decrypt(r)

    def get(self, name="default", secret=""):
        """
        """
        if secret == "":
            secret = self._secret_get()
        return NACL(name, secret)

    @property
    def default(self):
        if self._default is None:
            self._default = self.get()
        return self._default

    @property
    def words(self):
        """
        default words which are securely stored on your filesystem
        js_shell 'print(j.data.nacl.default.words)'
        """
        return self.default.words

    def remember(self):
        """
        will start redis core, this will make sure that the secret & words
        are remembered for 1h

        js_shell 'j.data.nacl.remember()'

        """
        j.clients.redis.core_get()

    def _remember_get(self, secret, words):

        if "fake" not in str(j.core.db):
            if j.core.db.exists("nacl.meta"):
                data = j.core.db.get("nacl.meta")
                data2 = self.default.decryptSymmetric(data)
                data3 = j.data.serializers.json.loads(data2)

                if "secret" in data3 and not secret:
                    secret = data3["secret"]

                if "words" in data3 and not words:
                    words = data3["words"]

        return secret, words

    def _remember_set(self, secret, words):
        if "fake" not in str(j.core.db):
            data = {}
            data["secret"] = secret
            data["words"] = words
            data2 = j.data.serializers.json.dumps(data)
            data3 = self.default.encryptSymmetric(data2)
            self._logger.debug("remember secret,words")
            j.core.db.set("nacl.meta", data3, ex=3600)

    def encrypt(self, secret="", message="", words="", interactive=False):
        """
        secret is any size key
        words are bip39 words e.g. see https://iancoleman.io/bip39/#english

        if words not given then will take from the default nacl local config

        result is base64

        its a combination of nacl symmetric encryption using secret and
        asymetric encryption using the words

        the result is a super strong encryption

        to use

        js_shell 'j.data.nacl.encrypt()'

        """

        message = message.strip()

        if interactive:

            secret, words = self._remember_get(secret, words)

            if not secret:
                secret = j.tools.console.askPassword("your secret")
            if not message:
                message = j.tools.console.askMultiline(
                    "your message to encrypt")
                message = message.strip()
            if not words:
                yn = j.tools.console.askYesNo(
                    "do you wan to specify secret key as bip39 words?")
                if yn:
                    words = j.tools.console.askString("your bip39 words")
                else:
                    words = j.data.nacl.default.words

            self._remember_set(secret, words)

        else:
            if not secret or not message:
                raise RuntimeError("secret or message needs to be used")

        if words == "":
            words = j.data.nacl.default.words

        # first encrypt symmetric
        secret1 = j.data.hash.md5_string(secret)
        secret1 = bytes(secret1, 'utf-8')
        # print("secret1_jumpscale:%s"%secret1)

        box = nacl.secret.SecretBox(secret1)
        if j.data.types.str.check(message):
            message = bytes(message, 'utf-8')
        # print("msg_jumpscale:%s"%message)
        res = box.encrypt(message)

        # now encrypt asymetric using the words
        privkeybytes = j.data.encryption.mnemonic.to_entropy(words)
        # print("privkey_js:%s"%privkeybytes)

        pk = PrivateKey(privkeybytes)

        sb = SealedBox(pk.public_key)

        res = sb.encrypt(res)

        res = base64.encodestring(res)

        print("encr_js:%s" % res)

        # LETS VERIFY

        msg = self.decrypt(
            secret=secret,
            message=res.decode('utf8'),
            words=words,
            interactive=interactive)

        if j.data.types.bytes.check(message):
            message = message.decode('utf8')

        assert msg.strip() == message.strip()

        if interactive:
            print("encrypted text:\n*************\n")
            print(res.decode('utf8'))

        return res

    def decrypt(self, secret="", message="", words="", interactive=False):
        """
        use output from encrypt

        js_shell 'j.data.nacl.decrypt()'

        """

        if interactive:

            secret, words = self._remember_get(secret, words)

            if not secret:
                secret = j.tools.console.askPassword("your secret")
            if not message:
                message = j.tools.console.askMultiline(
                    "your message to decrypt")
                message = message.strip()
            if not words:
                yn = j.tools.console.askYesNo(
                    "do you wan to specify secret key as bip39 words?")
                if yn:
                    words = j.tools.console.askString("your bip39 words")
        else:
            if not secret or not message:
                raise RuntimeError("secret or message needs to be used")

        secret = j.data.hash.md5_string(secret)
        secret = bytes(secret, 'utf-8')

        if not j.data.types.bytes.check(message):
            message = bytes(message, 'utf8')

        message = base64.decodestring(message)

        if words == "":
            words = j.data.nacl.default.words

        privkeybytes = j.data.encryption.mnemonic.to_entropy(words)

        pk = PrivateKey(privkeybytes)
        sb = SealedBox(pk)

        message = sb.decrypt(message)

        # now decrypt symmetric
        box = nacl.secret.SecretBox(secret)
        message = box.decrypt(message)
        message = message.decode(encoding='utf-8', errors='strict')

        if interactive:
            print("decrypted text:\n*************\n")
            print(message.strip() + "\n")

        return message

    def test(self):
        """
        js_shell 'j.data.nacl.test()'
        """

        res = self.encrypt("1111", "something", interactive=False)
        res2 = self.decrypt("1111", res, interactive=False)
        assert "something" == res2

        words = 'oxygen fun inner bachelor cherry pistol knife quarter ' \
                'grass act ceiling wrap another input style profit middle ' \
                'cake slight glance silk rookie caught parade'
        res3 = self.encrypt(
            "1111",
            "something",
            words=words,
            interactive=False)
        assert res != res3

        try:
            res4 = self.decrypt("1111", res3, interactive=False)
        except Exception as e:
            assert str(e).find("error occurred") != -1

        res4 = self.decrypt("1111", res3, words=words, interactive=False)
        assert "something" == res4

        cl = self.default  # get's the default location & generate's keys

        data = b"something"
        r = cl.sign(data)

        assert cl.verify(data, r)
        assert cl.verify(b"a", r) == False

        pubsignkey32 = cl.signingkey_pub.encode()

        assert cl.verify(data, r, pubsignkey32)

        a = cl.encryptSymmetric("something")
        b = cl.decryptSymmetric(a)

        assert b == b"something"

        a = cl.encryptSymmetric("something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = cl.encryptSymmetric("something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = cl.encryptSymmetric(b"something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        # now with hex
        a = cl.encryptSymmetric(b"something", "qwerty", hex=True)
        b = cl.decryptSymmetric(a, b"qwerty", hex=True)
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

        self._logger.info("TEST OK")

    def test_perf(self):
        """
        js_shell 'j.data.nacl.test_perf()'
        """

        cl = self.default  # get's the default location & generate's keys
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
            a = cl.encryptSymmetric(data2, secret=secret)
            b = cl.decryptSymmetric(a, secret=secret)
            assert data2 == b
        j.tools.timer.stop(i)
