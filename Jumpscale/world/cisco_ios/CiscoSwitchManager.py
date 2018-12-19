from Jumpscale import j
# import baselib.remote

JSBASE = j.application.JSBaseClass


class CiscoSwitchManager(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal.ciscoswitch"
        JSBASE.__init__(self)

    def get(self, host, login, password):
        """get CiscoSwitch
        
        Arguments:
            host {str} -- host of CiscoSwitch
            login {str} -- User of CiscoSwitch
            password {str} -- Password of CiscoSwitch
        
        Returns:
            CiscoSwitch -- return your Cisco Switch 
        """
        return CiscoSwitch(host, login, password)
#!/usr/bin/python


from .Router import Router


class CiscoSwitch(JSBASE):

    def __init__(self, host, login, password):
        JSBASE.__init__(self)
        R1 = Router(hostname=host, logfile='cisco.log')
        login_cmd = 'telnet ' + host
        login_expect = '#'  # .format(hostname)  # TODO: NEEDS TO BE ADJUSTED
        out = R1.login(login_cmd, login, password, login_expect)
        # if out != R1._LOGIN_USERNAME_PROMPTS:
        #     R1.logout()
        #     time.sleep(60)
        #     R1 = Router(hostname, logfile='cisco.log')
        #     password = Localhost1.get_rsa_token()
        #     out = R1.login(login_cmd, login, password, login_expect)

        self.cisco = R1

        self.host = host
        self.login = login
        self.password = password
        # if res != True: # TODO: adjust to check
        #     raise j.exceptions.RuntimeError("Could not login into cisco switch: %s"%host)

        # inputsentence = []

        cmd = "terminal length 0"
        self.do(cmd)
        self.do("configure terminal", "#")
        self.do("hostname %s" % host, "#")
        self.do("exit")

    def logout(self):
        self._client.logout()

    def do(self, cmd, prompt=None):
        if prompt == "":
            prompt = "%s#" % self.cisco.hostname

        return self.cisco.exec_cmd(cmd, prompt=prompt)

    def interface_getvlanconfig(self, interfaceName):
        """
        return vlan config of interface
        """

    def interface_setvlan(self, interfaceName, fromVlanId, toVlanId, reset=False):
        """
        configure set of vlan's on interface
        @param reset when True older info is deleted and only this vlanrange is added
        """

    def _normalizespaces(self, line):
        while line.find("  ") != -1:
            line = line.replace("  ", " ")
        return line

    def interface_getArpMAC(self):
        """
        returns mac addresses an interface knows about (can be used to detect connected ports from servers)
        return dict as follows
        {$interfacename:[$macaddr1,$macaddr2,...]}
        """
        result = {}
        out = self.do("sh mac-address-table")
        for line in out.split("\n"):
            line = line.strip()
            if line == "" or line[0] != "*":
                continue
            line = self._normalizespaces(line)
            splitted = line.split(" ")
            if len(splitted) > 5:
                vlan = splitted[1]
                mac = splitted[2].replace(".", "").lower()
                ttype = splitted[3]
                interface = splitted[5]
                if interface not in result:
                    result[interface] = []
                result[interface].append(mac)
            else:
                pass

        return result

    def interface_getall(self):
        """
        return info about interfaces on switch (name, macaddresses, types, ...)
        """
        raise j.exceptions.RuntimeError("implement")
        return r

    def interface_getnames(self):
        raise j.exceptions.RuntimeError("implement")
        return r

    def backup(self, name, destinationdir):
        config = self.do("show running-config")
        raise j.exceptions.RuntimeError("implement")
        return r
        self.do("/system/backup/save", args={"name": name})
        path = "%s.backup" % name
        self.download(path, j.sal.fs.joinPaths(destinationdir, path))
        self.do("/export", args={"file": name})
        path = "%s.rsc" % name
        self.download(path, j.sal.fs.joinPaths(destinationdir, path))

    def download(self, path, dest):
        # TODO: now sure how that works on cisco sw
        from ftplib import FTP
        ftp = FTP(host=self.host, user=self.login, passwd=self.password)
        ftp.retrbinary('RETR %s' % path, open(dest, 'wb').write)
        ftp.close()
