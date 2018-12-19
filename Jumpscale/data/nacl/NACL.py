from Jumpscale import j
from nacl.public import PrivateKey, SealedBox
import nacl.signing
import nacl.secret
import nacl.utils
import nacl.hash
import nacl.encoding
import hashlib
# from .AgentWithKeyname import AgentWithName
import binascii
from nacl.exceptions import BadSignatureError

JSBASE = j.application.JSBaseClass


class NACL(JSBASE):
    def __init__(self, name, secret):
        """
        """
        JSBASE.__init__(self)


        self.secret = secret
        self.name = name

        self.path = j.core.tools.text_replace("{DIR_CFG}/nacl")
        j.sal.fs.createDir(self.path)
        self._logger.debug("NACL uses path:'%s'" % self.path)

        self._box = nacl.secret.SecretBox(self.secret)

        self.path_privatekey = "%s/%s.priv" % (self.path, self.name)
        if not j.sal.fs.exists(self.path_privatekey):
            self._keys_generate()
        self._privkey = ""
        self._pubkey = ""
        self._signingkey = ""
        self._signingkey_pub = ""

        self.words  #will check that the private key is in line with secret used


    @property
    def privkey(self):
        if self._privkey == "":
            self._privkey = self.file_read_hex(self.path_privatekey)
        key = self.decryptSymmetric(self._privkey)
        privkey = PrivateKey(key)
        self._pubkey = privkey.public_key
        return privkey

    @property
    def words(self):
        """
        js_shell 'print(j.data.nacl.default.words)'
        """
        privkey = self.privkey.encode()
        return j.data.encryption.mnemonic.to_mnemonic(privkey)
        # if not j.sal.fs.exists(self.path_words):
        #     self._logger.info("GENERATED words")
        #     words = j.data.encryption.mnemonic_generate()
        #     words = self.encryptSymmetric(words)
        #     self.file_write_hex(self.path_words,words)
        # words = self.file_read_hex(self.path_words)
        # words = self.decryptSymmetric(words)
        # return words.decode()

    @property
    def pubkey(self):
        if self._pubkey == "":
            return self.privkey.public_key
        return self._pubkey

    @property
    def signingkey(self):
        if self._signingkey == "":
            self._signingkey = nacl.signing.SigningKey(self.privkey.encode())
        return self._signingkey

    @property
    def signingkey_pub(self):
        if self._signingkey_pub == "":
            self._signingkey_pub = self.signingkey.verify_key
        return self._signingkey_pub

    def tobytes(self, data):
        if not j.data.types.bytes.check(data):
            data = data.encode()  # will encode utf8
        return data

    def hash32(self, data):
        m = hashlib.sha256()
        m.update(self.tobytes(data))
        return m.digest()

    def hash8(self, data):
        # shortcut, maybe better to use murmur hash
        m = hashlib.sha256()
        m.update(self.tobytes(data))
        return m.digest()[0:8]

    def ssh_hash(self,data):
        """
        uses sshagent to sign the payload & then hash result with md5
        :return:
        """
        if j.data.types.string.check(data):
            data = data.encode()
        data2 = self.sign_with_ssh_key(data)
        return j.data.hash.md5_string(data2)

    def encryptSymmetric(self, data, secret=b"", hex=False, salt=""):
        box = self._box
        if salt == "":
            salt = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        else:
            salt = j.data.hash.md5_string(salt)[0:24].encode()
        res = box.encrypt(self.tobytes(data), salt)
        if hex:
            res = self.bin_to_hex(res).decode()
        return res

    def decryptSymmetric(self, data, secret=b"", hex=False):
        box = self._box
        if hex:
            data = self.hex_to_bin(data)
        res = box.decrypt(self.tobytes(data))
        box = None
        return res

    def encrypt(self, data, hex=False):
        """ Encrypt data using the public key
            :param data: data to be encrypted, should be of type binary
            @return: encrypted data
        """
        data = self.tobytes(data)
        sealed_box = SealedBox(self.pubkey)
        res = sealed_box.encrypt(data)
        if hex:
            res = self.bin_to_hex(res)
        return res

    def decrypt(self, data, hex=False):
        """ Decrypt incoming data using the private key
            :param data: encrypted data provided
            @return decrypted data
        """
        unseal_box = SealedBox(self.privkey)
        if hex:
            data = self.hex_to_bin(data)
        return unseal_box.decrypt(data)

    def _keys_generate(self):
        """
        Generate private key (strong) & store in chosen path &
        will load in this class
        """
        key = PrivateKey.generate()
        key2 = key.encode()  # generates a bytes representation of the key
        key3 = self.encryptSymmetric(key2)
        path = self.path_privatekey

        self.file_write_hex(path, key3)

        # build in verification
        key4 = self.file_read_hex(path)
        assert key3 == key4

    def sign(self, data):
        """
        sign using your private key using Ed25519 algorithm
        the result will be 64 bytes
        """
        res = self.signingkey.sign(data)
        return res[:-len(data)]

    def verify(self, data, signature, pubkey=""):
        """ data is the original data we have to verify with signature
            signature is Ed25519 64 bytes signature
            pubkey is the signature public key, is not specified will use
            your own (the pubkey is 32 bytes)

        """
        if pubkey == "":
            pubkey = self.signingkey_pub
        else:
            pubkey = nacl.signing.VerifyKey(pubkey)
        try:
            pubkey.verify(data, signature)
        except BadSignatureError:
            return False

        return True

    def sign_with_ssh_key(self, data):
        """ will return 32 byte signature which uses the sshagent
            loaded on your system
            this can be used to verify data against your own sshagent
            to make sure data has not been tampered with

            this signature is then stored with e.g. data and you 
            can verify against your own ssh-agent if the data was
            tampered with
        """
        hash = hashlib.sha1(data).digest()
        signeddata = self.agent.sign_ssh_data(hash)
        return self.hash32(signeddata)

    def file_write_hex(self, path, content):
        j.sal.fs.createDir(j.sal.fs.getDirName(path))
        content = binascii.hexlify(content)
        j.sal.fs.writeFile(path, content)

    def file_read_hex(self, path):
        content = j.sal.fs.readFile(path)
        content = binascii.unhexlify(content)
        return content

    def bin_to_hex(self, content):
        return binascii.hexlify(content)

    def hex_to_bin(self, content):
        content = binascii.unhexlify(content)
        return content
