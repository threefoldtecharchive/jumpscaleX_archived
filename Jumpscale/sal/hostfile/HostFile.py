# import time
# import socket
import re

from Jumpscale import j
JSBASE = j.application.JSBaseClass


class HostFileFactory(j.application.JSBaseClass):

    def __init__(self):
        self.__jslocation__ = "j.sal.hostsfile"
        JSBASE.__init__(self)

    def get(self):
        return HostFile()


class HostFile(j.application.JSBaseClass):

    def __init__(self):
        self.hostfilePath = "/etc/hosts"
        JSBASE.__init__(self)

    def remove(self, ip):
        """Update a hostfile, delete ip from hostsfile
        @param hostsfile: File where hosts are defined
        @param ip: Ip of the machine to remove
        """
        # get content of hostsfile
        filecontents = j.sal.fs.readFile(self.hostfilePath)
        searchObj = re.search('^%s\s.*\n' % ip, filecontents, re.MULTILINE)
        if searchObj:
            filecontents = filecontents.replace(searchObj.group(0), '')
            j.sal.fs.writeFile(self.hostfilePath, filecontents)
        else:
            self._logger.warning('Ip address %s not found in hosts file' % ip)

    def existsIP(self, ip):
        """Check if ip is in the hostsfile
        @param hostsfile: File where hosts are defined
        @param ip: Ip of the machine to check
        """
        # get content of hostsfile
        filecontents = j.sal.fs.readFile(self.hostfilePath)
        res = re.search('^%s\s' % ip, filecontents, re.MULTILINE)
        if res:
            return True
        else:
            return False

    def getNames(self, ip):
        """Get hostnames for ip address
        @param hostsfile: File where hosts are defined
        @param ip: Ip of the machine to get hostnames from
        @return: List of machinehostnames
        """

        if self.existsIP(ip):
            filecontents = j.sal.fs.readFile(self.hostfilePath)
            searchObj = re.search('^%s\s.*\n' % ip, filecontents, re.MULTILINE)
            hostnames = searchObj.group(0).strip().split()
            hostnames.pop(0)
            return hostnames
        else:
            return []

    def set(self, ip, hostname):
        """Update a hostfile to contain the basic information install
        @param hostsfile: File where hosts are defined
        @param ip: Ip of the machine to add/modify
        @param hostname: List of machinehostnames to add/modify
        """
        if isinstance(hostname, str):
            hostname = hostname.split()
        filecontents = j.sal.fs.readFile(self.hostfilePath)
        searchObj = re.search('^%s\s.*\n' % ip, filecontents, re.MULTILINE)

        hostnames = ' '.join(hostname)
        if searchObj:
            filecontents = filecontents.replace(
                searchObj.group(0), '%s %s\n' % (ip, hostnames))
        else:
            filecontents += '%s %s\n' % (ip, hostnames)

        j.sal.fs.writeFile(self.hostfilePath, filecontents)
