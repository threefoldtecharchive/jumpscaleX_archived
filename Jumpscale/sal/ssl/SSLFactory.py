from Jumpscale import j
from OpenSSL import crypto
import OpenSSL
from socket import gethostname

JSBASE = j.application.JSBaseClass


class SSLFactory(j.builder._BaseClass):

    def __init__(self):
        self.__jslocation__ = "j.sal.ssl"
        self.__imports__ = "pyopenssl"
        JSBASE.__init__(self)

    def ca_cert_generate(self, cert_dir="",reset=False):
        """
        is for CA
        If ca.crt and ca.key don't exist in cert_dir, create a new ??? #TODO: *1 this is not right I think
        self-signed cert and keypair and write them into that directory.

        js_shell 'j.sal.ssl.ca_cert_generate()'

        returns True if generation happened

        """
        if cert_dir == "":
            cert_dir = j.dirs.CFGDIR+"/ssl"
            
        j.sal.fs.createDir(cert_dir)
            
        cert_dir = j.tools.path.get(cert_dir)
        CERT_FILE = cert_dir.joinpath("ca.crt")  # info (certificaat) (pub is inhere + other info)
        KEY_FILE = cert_dir.joinpath("ca.key")  # private key

        if reset or not CERT_FILE.exists() or not KEY_FILE.exists():

            # create a key pair
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 2048)

            # create a self-signed cert
            cert = crypto.X509()
            cert.set_version(3)
            cert.get_subject().C = "BE"
            cert.get_subject().ST = "OV"
            cert.get_subject().L = "Ghent"
            cert.get_subject().O = "my company"
            cert.get_subject().OU = "my organization"
            cert.get_subject().CN = gethostname()

            import time
            cert.set_serial_number(int(time.time() * 1000000))
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.add_extensions([
                OpenSSL.crypto.X509Extension(b"basicConstraints", True, b"CA:TRUE, pathlen:0"),
                OpenSSL.crypto.X509Extension(b"keyUsage", True, b"keyCertSign, cRLSign"),
                OpenSSL.crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash",
                                             subject=cert),
            ])
            cert.sign(k, 'sha1')

            CERT_FILE.write_text(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode())
            KEY_FILE.write_text(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode())

            return True
        else:
            return False

    def create_signed_cert(self, path, keyname):
        """
        Signing X509 certificate using CA
        The following code sample shows how to sign an X509 certificate using a CA:
        THis is usually done by the certificate authority it self like verisign, GODaddy, ... etc
        :param path: Path to the certificate and key that will be used in signing the new certificate
        :param keyname: the new certficate and key name
        """
        path = j.tools.path.get(path)
        cacert = path.joinpath("ca.crt").text()
        cakey = path.joinpath("ca.key").text()
        ca_cert = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cacert)
        ca_key = OpenSSL.crypto.load_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, cakey)

        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

        cert = OpenSSL.crypto.X509()
        cert.get_subject().CN = "node1.example.com"
        import time
        cert.set_serial_number(int(time.time() * 1000000))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(24 * 60 * 60)
        cert.set_issuer(ca_cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(ca_key, "sha1")

        path.joinpath("%s.crt" % keyname).write_text(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode())
        path.joinpath("%s.key" % keyname).write_text(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode())

    def create_certificate_signing_request(self, common_name):
        """
        Creating CSR (Certificate Signing Request)
        this CSR normally passed to the CA (Certificate Authority) to create a signed certificate
        :param common_name: common_name to be used in subject
        """
        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

        req = OpenSSL.crypto.X509Req()
        req.get_subject().commonName = common_name

        req.set_pubkey(key)
        req.sign(key, "sha1")

        # Write private key
        key = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)

        # Write request
        req = OpenSSL.crypto.dump_certificate_request(
            OpenSSL.crypto.FILETYPE_PEM, req)
        return key, req

    def sign_request(self, req, path):
        """
        Processes a CSR (Certificate Signning Request)
        issues a certificate based on the CSR data and signit
        :param req: CSR
        :param path: path to the key and certificate that will be used in signning this request
        """

        path = j.tools.path.get(path)
        cacert = path.joinpath("ca.crt").text()
        cakey = path.joinpath("ca.key").text()
        
        ca_cert = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cacert)
        ca_key = OpenSSL.crypto.load_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, cakey)
            
        req = OpenSSL.crypto.load_certificate_request(
            OpenSSL.crypto.FILETYPE_PEM, req)

        cert = OpenSSL.crypto.X509()
        cert.set_subject(req.get_subject())
        import time
        cert.set_serial_number(int(time.time() * 1000000))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(24 * 60 * 60)
        cert.set_issuer(ca_cert.get_subject())
        cert.set_pubkey(req.get_pubkey())
        cert.sign(ca_key, "sha1")

        certificate = OpenSSL.crypto.dump_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cert)
        return certificate

    def verify(self, certificate, key):
        """
        It reads the pathes of certificate and key files of an X509 certificate
        and verify if certificate matches private key

        :param certificate (string): path to the certificate file
        :param key (string): path to the key file
        :return (boolean): True only if certificate matches the private key
        """
        key = self._load_privatekey(key)
        certificate = self._load_certificate(certificate)

        ctx = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_METHOD)
        ctx.use_privatekey(key)
        ctx.use_certificate(certificate)
        try:
            ctx.check_privatekey()
        except OpenSSL.SSL.Error:
            self._logger.debug("Incorrect key")
            return False
        else:
            self._logger.debug("Key matches certificate")
            return True

    def bundle(self, certificate, key, certification_chain=(), passphrase=None):
        """
        Bundles a certificate with it's private key (if any) and it's chain of trust.
        Optionally secures it with a passphrase.

        :param certificate (string): path to the certificate file
        :param key (string): path to the key file
        :param certification_chain (tuple): certification chain, by default it is an empty tuple
        :param passphrase (string): passpharse for the bundle, by default it is None
        :return: PKCS12 object
        """
        key = self._load_privatekey(key)
        x509 = self._load_certificate(certificate)

        p12 = OpenSSL.crypto.PKCS12()
        p12.set_privatekey(key)
        p12.set_certificate(x509)
        p12.set_ca_certificates(certification_chain)
        p12.set_friendlyname(b'Jumpscaleclientauthentication')
        return p12.export(passphrase=passphrase)


    def _load_privatekey(self, path):
        """
        load a private key content from a path

        :param path: path to the key file
        :return: content of the file
        """
        key = j.tools.path.get(path).text()
        key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
        return key

    def _load_certificate(self, path):
        """
        load certifcate content from a path

        :param path: path to the certificate
        :return: content of the certificate
        """
        certificate = j.tools.path.get(path).text()
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
        return x509
