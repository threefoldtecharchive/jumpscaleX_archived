from .forwarder import MailForwarder

from Jumpscale import j

class JSMailForwarderBase(j.application.JSBaseConfigClass):
    """Base class that holds the forwarder's configurations as 
    A JSX schema
    """
    
    _SCHEMATEXT = """
        @url = jumpscale.mailforwarder.1
        name* = ""
        listening_host = ""
        listening_port = (I)
        relay_host = ""
        relay_port = (I)
        relay_user = ""
        relay_password = ""
        relay_ssl = (B)
        forward_config = (LO) !jumpscale.mailforwarder.forward_config.1

        @url = jumpscale.mailforwarder.forward_config.1
        destination_domain = ""
        source_domains = (LS)
    """
    
    def _process_forward_config(self):
        """Since the jsx sechema does not support dictionaries, we represent the forward_config
        which initially should be represented as a dict in the form of:
        {
            <destination_domain> : [<source_domain1>, <source_domain2>, ...]
        }
        The above dict will be represented as:
        ["<destination_domain>|<source_domain1>,<source_domain2>", ...]

        and the purpose of this function is to convert from the jsx schema LS format to the dictionary format
        """
        self._forward_config = {}
        for item in self.forward_config:
            mapping_items = item.split("|")
            if len(mapping_items) > 1:
                self._forward_config[mapping_items[0]] = map(lambda item: item.strip(), mapping_items[1].split(','))
            else:
                self._log_warning("forward_config is not correctly configured.")

    def _init(self):
        self._process_forward_config()
        relay_config = {
            "host": self.relay_host,
            "port": self.relay_port,
            "user": self.relay_user,
            "password": self.relay_password,
            "ssl": self.relay_ssl
        }
        self._forwarder = MailForwarder(self.listening_host,
                                        self.listening_port,
                                        self._forward_config,
                                        relay_config)
    
    def start(self):
        """Starts a forwarder server
        """
        self._forwarder.run()


    def test(self, gdomain_user, gdomain_password):
        mf = j.servers.mail_forwarder.get(name = "test",
                                          listening_host="localhost",
                                          listening_port=8823,
                                          relay_host="smtp.gmail.com",
                                          relay_port=587,
                                          relay_user=gdomain_user,
                                          relay_password=gdomain_password,
                                          relay_ssl=True,
                                          forward_config=["codescalers.com|incubaide.com,threefoldtech.com"])
        mf.start()
    

class JSMailForwarderFactory(j.application.JSBaseConfigsClass):
    """Factory class
    """
    __jslocation__ = "j.servers.mail_forwarder"
    _CHILDCLASS = JSMailForwarderBase
