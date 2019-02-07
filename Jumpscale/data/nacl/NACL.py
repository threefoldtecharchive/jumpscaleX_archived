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
import sys
JSBASE = j.application.JSBaseClass


class NACL(j.application.JSBaseClass):
    def __init__(self, name,privkey=None,secret=None,reset=False,interactive=True):

        while True:
            try:
                self._init__(name=name,privkey=privkey,secret=secret,reset=reset,interactive=interactive)
                break
            except nacl.exceptions.CryptoError as e:
                print(e)
                self._log_warning("ERROR in decrypting")
                secret = j.tools.console.askPassword("issue in decrypting the private key, try other secret")

    def reset(self,privkey=None,secret=None):
        self._init__(name=self.name,privkey=privkey,secret=secret,reset=True,interactive=True)

    def _init__(self, name,privkey=None,secret=None,reset=False,interactive=True):
        """
        :param if secret given will be used in nacl
        """
        JSBASE.__init__(self)

        self.name = name

        self.path = j.core.tools.text_replace("{DIR_CFG}/nacl")
        j.sal.fs.createDir(self.path)
        self._log_debug("NACL uses path:'%s'" % self.path)

        path_encryptor_for_secret="{DIR_VAR}/myprocess_%s.log"%name
        if reset:
            j.sal.fs.remove(path_encryptor_for_secret)
        if not j.sal.fs.exists(path_encryptor_for_secret):
            key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            j.sal.fs.writeFile(path_encryptor_for_secret,key)
        else:
            key = j.sal.fs.readFile(path_encryptor_for_secret,binary=True)
        sb=nacl.secret.SecretBox(key)
        redis_key="secret_%s"%name


        if reset:
            j.core.db.delete(redis_key)

        # TODO: this should be placed in the correct location
        if not j.core.db:
            j.core._db = j.clients.redis.core_get()

        r = j.core.db.get(redis_key)
        if r:
            try:
                secret = sb.decrypt(r)
            except Exception as e:
                r = None

        if r is None:
            if not secret:
                secret = j.tools.console.askPassword("Provide a strong secret which will be used to encrypt/decrypt your private key")
                if secret.strip() in [""]:
                    raise RuntimeError("Secret cannot be empty")
                secret = self._hash(secret)
            r = sb.encrypt(secret)
            j.core.db.set(redis_key,r)

        r = j.core.db.get(redis_key)
        secret = sb.decrypt(r) #this to doublecheck

        self._box = nacl.secret.SecretBox(secret)  #used to decrypt the private key

        self.__init()

        print = j.tools.console.echo

        self.path_privatekey = "%s/%s.priv" % (self.path, self.name)
        if reset:
            j.sal.fs.remove(self.path_privatekey)
        if not j.sal.fs.exists(self.path_privatekey):
            if interactive:
                msg = """
                There is no private key on your system yet.
                We will generate one for you or you can provide words of your secret key.
                """
                if j.tools.console.askYesNo("Ok to generate private key (Y or 1 for yes, otherwise provide words)?"):
                    print("\nWe have generated a private key for you.")
                    print("\nThe private key:\n\n")
                    self._keys_generate()
                    j.tools.console.echo("{RED}")
                    print("{BLUE}"+self.words+"{RESET}\n")
                    print("\n{RED}ITS IMPORTANT TO STORE THIS KEY IN A SAFE PLACE{RESET}")
                    if not j.tools.console.askYesNo("Did you write the words down and store them in safe place?"):
                        j.sal.fs.remove(self.path_privatekey)
                        print("WE HAVE REMOVED THE KEY, need to restart this procedure.")
                        sys.exit(1)
                else:
                    words = j.tools.console.askString("Provide words of private key")
                    self._keys_generate(words=words)
                    assert self.words == words

            j.tools.console.clear_screen()

            word3=self.words.split(" ")[2]

            word3_to_check = j.tools.console.askString("give the 3e word of the private key string")

            if not word3 == word3_to_check:
                print ("the control word was not correct, please restart the procedure.")
                sys.exit(1)

        self.__init()


        self.words  #will check that the private key is in line with secret used


    def __init(self):

        self._privkey = ""
        self._pubkey = ""
        self._signingkey = ""
        self._signingkey_pub = ""



    def _hash(self,data):
        m = hashlib.sha256()
        if not j.data.types.bytes.check(data):
            data = data.encode()
        m.update(data)
        return m.digest()


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
        #     self._log_info("GENERATED words")
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

    def decryptSymmetric(self, data, hex=False):
        if hex:
            data = self.hex_to_bin(data)
        res = self._box.decrypt(self.tobytes(data))
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

    def _keys_generate(self,words=None):
        """
        Generate private key (strong) & store in chosen path &
        will load in this class
        """
        if words:
            key2 = j.data.encryption.mnemonic.to_entropy(words)
        else:
            key = PrivateKey.generate()
            key2 = key.encode()  # generates a bytes representation of the key
        key3 = self.encryptSymmetric(key2)
        self.file_write_hex(self.path_privatekey, key3)

        # build in verification
        key4 = self.file_read_hex(self.path_privatekey)
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

    def __str__(self):
        return "nacl:%s"%self.name

    __repr__ = __str__
