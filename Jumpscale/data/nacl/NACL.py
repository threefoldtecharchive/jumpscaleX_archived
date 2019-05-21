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
print = j.tools.console.echo


class NACL(j.application.JSBaseClass):
    def _init2(self, name=None):
        assert name is not None
        self.name = name
        self._box = None

    @property
    def _path(self):
        return "/sandbox/cfg/nacl/%s" % self.name

    @property
    def _path_privatekey(self):
        return "%s/key.priv" % (self._path)

    @property
    def _path_encryptor_for_secret(self):
        return j.core.tools.text_replace("{DIR_VAR}/logs/myprocess_%s.log" % self.name)

    def _ask_privkey_words(self):
        """

        :param privkey_words:
        :return:
        """
        msg = """
        There is no private key on your system yet.
        We will generate one for you or you can provide words of your secret key.
        """
        if j.tools.console.askYesNo("Ok to generate private key (Y or 1 for yes, otherwise provide words)?"):
            print("\nWe have generated a private key for you.")
            print("\nThe private key:\n\n")
            self._keys_generate()
            j.tools.console.echo("{RED}")
            print("{BLUE}" + self.words + "{RESET}\n")
            print("\n{RED}ITS IMPORTANT TO STORE THIS KEY IN A SAFE PLACE{RESET}")
            if not j.tools.console.askYesNo("Did you write the words down and store them in safe place?"):
                j.sal.fs.remove(self._path_privatekey)
                print("WE HAVE REMOVED THE KEY, need to restart this procedure.")
                sys.exit(1)
        else:
            words = j.tools.console.askString("Provide words of private key")
            self._keys_generate(words=words)

        j.tools.console.clear_screen()

        word3 = self.words.split(" ")[2]

        word3_to_check = j.tools.console.askString("give the 3e word of the private key string")

        if not word3 == word3_to_check:
            j.sal.fs.remove(self._path_privatekey)
            self._error_raise("the control word was not correct, please restart the procedure.")

    @property
    def words(self):
        """
        e.g.
        kosmos 'print(j.data.nacl.default.words)'
        """
        assert self.privkey is not None
        privkey = self.privkey.encode()
        return j.data.encryption.mnemonic.to_mnemonic(privkey)

    def _keys_generate(self, words=None):
        """
        Generate private key (strong) & store in chosen path encrypted using the local secret
        """
        if words:
            key2 = j.data.encryption.mnemonic.to_entropy(words)
        else:
            key = PrivateKey.generate()
            key2 = key.encode()  # generates a bytes representation of the key
        key3 = self.encryptSymmetric(key2)
        self._file_write_hex(self._path_privatekey, key3)

        # build in verification
        key4 = self._file_read_hex(self._path_privatekey)
        assert key3 == key4

        self._load_privatekey()

    def configure(self, privkey_words=None, secret=None, sshagent_use=None, interactive=False, generate=False):
        """

        secret is used to encrypt/decrypt the private key when stored on local filesystem
        privkey_words is used to put the private key back

        will ask for the details of the configuration
        :param: sshagent_use is True, will derive the secret from the private key of the ssh-agent if only 1 ssh key loaded
                                secret needs to be None at that point
        :param: secret only used when sshagent not used, will be stored encrypted in redis
                sha256 is used on the secret as specified above before storing/encrypting/decrypting the private key

        :param: generate if True and interactive is False then will autogenerate a key

        :return: None
        """
        self._log_debug("NACL uses path:'%s'" % self._path)

        self.privkey = None

        j.application.interactive = j.application.interactive or interactive

        # create dir where the secret will be to encrypt the secret
        j.sal.fs.createDir(j.core.tools.text_replace("{DIR_VAR}/logs"))

        j.sal.fs.remove(self._path_encryptor_for_secret)

        redis_key = "secret_%s" % self.name

        if j.core.db is None:
            j.clients.redis.core_get()

        j.core.db.delete(redis_key)

        if j.application.interactive and sshagent_use is None:
            sshagent_use = j.tools.console.askYesNo("do you want to use ssh-agent for secret key in jumpscale?")

        if sshagent_use is False:
            if secret is None:
                secret = j.tools.console.askPassword(
                    "Provide a strong secret which will be used to encrypt/decrypt your private key"
                )
                if secret.strip() in [""]:
                    self._error_raise("Secret cannot be empty")
                secret = self._hash(secret)
            # will create a dummy file with a random key which will encrypt the secret
            key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            j.sal.fs.writeFile(self._path_encryptor_for_secret, key)
            self._box = nacl.secret.SecretBox(key)
            if isinstance(secret, str):
                secret = secret.encode()
            r = self._box.encrypt(secret)
            j.core.db.set(redis_key, r)

        # create path where the files for nacl will be
        j.sal.fs.createDir(self._path)

        self.load(die=False)

        if self.privkey is None:
            if j.application.interactive:
                # means we did not find a priv key yet
                self._ask_privkey_words()
            elif generate:
                self._keys_generate()

            self.load(die=False)

        if self.privkey is None:
            # none of the methods worked
            self._error_raise("could not generate/load a private key, please use 'kosmos --init' to fix.")

    def _error_raise(self, msg):
        msg = "## There is an issue in the Jumpscale encryption layer. ##\n%s" % msg
        if j.application.interactive:
            print(msg)
            sys.exit(1)
        else:
            raise RuntimeError(msg)

    def load(self, die=True):
        """
        will load private key from filesystem
        if not possible will exit to shell
        """

        self._signingkey = ""
        self.privkey = None

        if j.sal.fs.exists(self._path_encryptor_for_secret):
            # means will not use ssh-agent
            # get secret from redis which is encrypted there
            # use a local file to decrypt the key, so at least its not non encrypted in the redis
            redis_key = "secret_%s" % self.name
            key = j.sal.fs.readFile(self._path_encryptor_for_secret, binary=True)
            sb = nacl.secret.SecretBox(key)
            try:
                r = j.core.db.get(redis_key)
            except AttributeError:
                r = None
            if r is None:
                self._error_raise("cannot find secret in memory, please use 'kosmos --init' to fix.")
            secret = sb.decrypt(r)
        else:
            # need to find an ssh agent now and only 1 key
            if j.clients.sshagent.available_1key_check():
                key = j.clients.sshagent.sign("nacl_could_be_anything", hash=True)
            else:
                if die:
                    self._error_raise(
                        "could not find secret key from sshagent, ssh-agent not active, if active need 1 ssh key loaded!"
                    )
                else:
                    return False

        try:
            self._box = nacl.secret.SecretBox(key)  # used to decrypt the private key
        except nacl.exceptions.CryptoError as e:
            if die:
                self._error_raise("could not use the secret key, maybe wrong one, please use 'kosmos --init' to fix.")
            else:
                return False

        return self._load_privatekey(die=die)

    def _load_privatekey(self, die=True):

        if not j.sal.fs.exists(self._path_privatekey):
            if die:
                self._error_raise("could not find the path of the private key, please use 'kosmos --init' to fix.")
            else:
                return False
        priv_key = self._file_read_hex(self._path_privatekey)

        try:
            priv_key_decrypted = self.decryptSymmetric(priv_key)
        except nacl.exceptions.CryptoError as e:
            if die:
                self._error_raise(
                    "could not decrypt the private key, maybe wrong one, please use 'kosmos --init' to fix."
                )
            else:
                return False

        self.privkey = PrivateKey(priv_key_decrypted)

        return True

    @property
    def box(self):
        if not self._box:
            self.load()
        return self._box

    def _hash(self, data):
        m = hashlib.sha256()
        if not j.data.types.bytes.check(data):
            data = data.encode()
        m.update(data)
        return m.digest()

    @property
    def pubkey(self):
        return self.privkey.public_key

    @property
    def signingkey(self):
        if self._signingkey == "":
            encrypted_key = self._file_read_hex(self._path_privatekey)
            key = self.decryptSymmetric(encrypted_key)
            self._signingkey = nacl.signing.SigningKey(key)
        return self._signingkey

    @property
    def signingkey_pub(self):
        return self.signingkey.verify_key

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

    def ssh_hash(self, data):
        """
        uses sshagent to sign the payload & then hash result with md5
        :return:
        """
        if j.data.types.string.check(data):
            data = data.encode()
        data2 = self.sign_with_ssh_key(data)
        return j.data.hash.md5_string(data2)

    def encryptSymmetric(self, data, hex=False, salt=""):

        box = self.box
        if salt == "":
            salt = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        else:
            salt = j.data.hash.md5_string(salt)[0:24].encode()
        res = box.encrypt(self.tobytes(data), salt)
        if hex:
            res = self._bin_to_hex(res).decode()
        return res

    def decryptSymmetric(self, data, hex=False):
        if hex:
            data = self._hex_to_bin(data)
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
            res = self._bin_to_hex(res)
        return res

    def decrypt(self, data, hex=False):
        """ Decrypt incoming data using the private key
            :param data: encrypted data provided
            @return decrypted data
        """
        unseal_box = SealedBox(self.privkey)
        if hex:
            data = self._hex_to_bin(data)
        return unseal_box.decrypt(data)

    def sign(self, data):
        """
        sign using your private key using Ed25519 algorithm
        the result will be 64 bytes
        """
        signed = self.signingkey.sign(data)
        return signed.signature

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

    def _file_write_hex(self, path, content):
        j.sal.fs.createDir(j.sal.fs.getDirName(path))
        content = binascii.hexlify(content)
        j.sal.fs.writeFile(path, content)

    def _file_read_hex(self, path):
        content = j.sal.fs.readFile(path)
        content = binascii.unhexlify(content)
        return content

    def _bin_to_hex(self, content):
        return binascii.hexlify(content)

    def _hex_to_bin(self, content):
        content = binascii.unhexlify(content)
        return content

    def __str__(self):
        return "nacl:%s" % self.name

    __repr__ = __str__
