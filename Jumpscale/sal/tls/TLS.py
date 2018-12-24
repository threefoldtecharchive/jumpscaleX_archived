from Jumpscale import j

JSBASE = j.application.JSBaseClass

class TLS(j.builder._BaseClass):

    def __init__(self, cfsslService=None, path=None):
        JSBASE.__init__(self)
        self._local = j.tools.executorLocal
        if cfsslService is not None:
            self._cfsslService = cfsslService
            self.cwd = j.tools.path.get(cfsslService.path).joinpath('tls')
        elif path is not None:
            self.cwd = j.tools.path.get(path)
        else:
            raise j.exceptions.RuntimeError('TLS must be initialized with either the cfsslService or path')

    def askSubjects(self):
        """
        ask questions for names arguments
        return a list of dict like :
         [{
            "C": "AE",
            "L": "Dubai",
            "O": "GreenITGlobe",
            "OU": "0-complexity",
            "ST": "Dubai",
            "CN": "Common Name"
        }]
        """
        def validCountry(input):
            return False if len(input) > 2 else True

        countrty = j.tools.console.askString("Country", "AE")
        location = j.tools.console.askString("Location", "Dubai")
        organisation = j.tools.console.askString("Organisation", "GreenITGlobe")
        orgUnit = j.tools.console.askString('Organisation Unit', "0-complexity")
        state = j.tools.console.askString('State', "Dubai")
        commonName = j.tools.console.askString('CommonName')
        return [{
            "C": countrty,
            "L": location,
            "O": organisation,
            "OU": orgUnit,
            "ST": state,
            "CN": commonName
        }]

    def createCA(self, subjects, keyAlgo='rsa', keySize=4096):
        """
        Generate a Root CA.

        subjects: list of dict containing valid names. get create it with askSubjects method
        commonName: string used by some CAs to determine which domain the certificate is to be generated
        keyAlgo: string. name of the algorythme to use to for key generation
        keySize: int. size of the key to generate

        return (path_to_cert, path_to_key)
        """
        if not isinstance(subjects, list):
            subjects = [subjects]

        commonName = ""
        for s in subjects:
            commonName += '%s,' % s['CN']
            del s['CN']
        commonName = commonName.rstrip(',')

        csr = {
            'hosts': [],
            'CN': commonName,
            'key': {
                'algo': keyAlgo,
                'size': keySize,
            },
            'names': subjects
        }
        ca_csr_path = self.cwd.joinpath('ca-csr.json')
        ca_cert_path = self.cwd.joinpath('root-ca')
        ca_csr_path.write_text(j.data.serializers.json.dumps(csr, indent=4))

        cmd = 'cfssl gencert -initca %s | cfssljson -bare %s' % (ca_csr_path, ca_cert_path)
        self._local.execute(cmd)

        cert_path = ca_cert_path + ".pem"
        key_path = ca_cert_path + "-key.pem"
        output = "certificate generated at %s and key at %s" % (cert_path, key_path)
        self._logger.debug(output)

        return (cert_path, key_path)

    def createCSR(self, name, subjects, hosts, keyAlgo='rsa', keySize=2048):
        """
        name: name to indentify the csr.
        subjects: list of dict containing valid names. get create it with askSubjects method
        hosts: list of the domain names which the certificate should be valid for
        commonName: string used by some CAs to determine which domain the certificate is to be generated
        keyAlgo: string. name of the algorythme to use to for key generation
        keySize: int. size of the key to generate

        return (path_to_csr, path_to_key)
        """
        if not isinstance(subjects, list):
            subjects = [subjects]

        commonName = ""
        for s in subjects:
            commonName += '%s,' % s['CN']
            del s['CN']
        commonName = commonName.rstrip(',')

        csr = {
            'hosts': hosts,
            'CN': commonName,
            'key': {
                'algo': keyAlgo,
                'size': keySize,
            },
            'names': subjects
        }
        csr_json_path = self.cwd.joinpath('%s.json' % name)
        csr_json_path.write_text(j.data.serializers.json.dumps(csr, indent=4))

        output_path = self.cwd.joinpath(name)
        cmd = 'cfssl genkey %s | cfssljson -bare %s' % (csr_json_path, output_path)
        self._local.execute(cmd)

        csr_path = self.cwd.joinpath('%s.csr' % name)
        key_path = self.cwd.joinpath('%s-key.pem' % name)
        output = "certificate signing request generated at %s and key at %s" % (csr_path, key_path)
        self._logger.debug(output)

        return (csr_path, key_path)

    def signCSR(self, csr, ca, ca_key):
        """
        csr: path to the csr filee to sign
        ca: path to the ca certificate
        ca_key: path to the ca key
        """
        base = j.tools.path.get(csr.rstrip('/')).basename()
        name = base.split('.')[0]

        output_path = self.cwd.joinpath(name)
        cmd = 'cfssl sign -ca %s -ca-key %s %s | cfssljson -bare %s' % (ca, ca_key, csr, output_path)
        self._local.execute(cmd)
        cert_path = self.cwd.joinpath("%s.pem" % name)
        output = 'certificate created at %s' % cert_path

        self._logger.debug(output)

        return cert_path

    def createSignedCertificate(self, name, subjects, hosts, ca, ca_key, keyAlgo='rsa', keySize=2048):
        """
        createSignedCertificate is a helper that create a CSR and sign it with the given CA in one operation.

        name: name to indentify the csr.
        subjects: list of dict containing valid names. get create it with askSubjects method
        hosts: list of the domain names which the certificate should be valid for
        ca: path to the CA certificate
        ca_key: path to the CA key
        keyAlgo: string. name of the algorythme to use to for key generation
        keySize: int. size of the key to generate

        return (path_to_csr, path_to_key)
        """
        if not isinstance(subjects, list):
            subjects = [subjects]

        commonName = ""
        for s in subjects:
            commonName += '%s,' % s['CN']
            del s['CN']
        commonName = commonName.rstrip(',')

        csr = {
            'hosts': hosts,
            'CN': commonName,
            'key': {
                'algo': keyAlgo,
                'size': keySize,
            },
            'names': subjects
        }
        csr_json_path = self.cwd.joinpath('%s.json' % name)
        csr_json_path.write_text(j.data.serializers.json.dumps(csr, indent=4))

        output_path = self.cwd.joinpath(name)
        cmd = 'cfssl gencert -ca %s -ca-key %s %s | cfssljson -bare %s' % (ca, ca_key, csr_json_path, output_path)
        self._local.execute(cmd)

        cert_path = self.cwd.joinpath('%s.pem' % name)
        key_path = self.cwd.joinpath('%s-key.pem' % name)

        output = "certificate generated at %s and key at %s" % (cert_path, key_path)
        self._logger.debug(output)

        return (cert_path, key_path)
