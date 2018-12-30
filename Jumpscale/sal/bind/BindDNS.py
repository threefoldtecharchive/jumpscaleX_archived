import os
import re
import dns.zone
from dns.zone import NoSOA
import dns.rdatatype
from dns.rdtypes.IN.A import A
from sal.bind.base import DNS
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class Zone(j.application.JSBaseClass):
    CONFIG_FILES_DIR = j.tools.path.get('/etc/bind/')
    NON_ZONE_FILES = ['/etc/bind/named.conf.options']

    def __init__(self, domain, type, file):
        JSBASE.__init__(self)
        self.domain = domain
        self.type = type
        self.file = file

    def __repr__(self):
        return "{domain:%s, type:%s, file:%s}" % (self.domain, self.type, self.file)

    @staticmethod
    def getZones():
        configs = []
        zonesfiles = []
        for configfile in ['named.conf.local', 'named.conf']:
            configs.append(''.join(os.path.join(
                Zone.CONFIG_FILES_DIR, configfile)))

        for file in configs:
            with open(file) as f:
                for line in re.findall('^include \".*\";$', f.read(), re.M):
                    path = line.replace('include ', '').replace(
                        '"', '').replace(';', '')
                    if path not in Zone.NON_ZONE_FILES:
                        zonesfiles.append(path)
        zones = {}
        for file in zonesfiles:
            with open(file) as f:
                for match in re.finditer('zone \"(?P<domain>.*)\" \{(?P<data>[^\}]+)', f.read()):
                    domain = match.group('domain')
                    data = match.group('data')
                    domaindata = dict()
                    for fieldm in re.finditer("^\s+(?P<key>\w+)\s+(?P<value>.*);$", data, re.M):
                        domaindata[fieldm.group('key')] = fieldm.group('value')
                    if not domaindata:
                        continue
                    zones[domain] = domaindata
                    zones[domain]['file'] = zones[
                        domain]['file'].replace('"', '')
        return zones

    @staticmethod
    def getMap(zones):
        res = {}
        for k, v in Zone.getZones().items():
            try:
                zone = dns.zone.from_file(
                    v['file'], os.path.basename(v['file']), relativize=False)
                for (name, ttl, rdata) in zone.iterate_rdatas('A'):
                    key = name.to_text().rstrip('.')
                    val = res.get(key, [])
                    if not {'ip': rdata.address, 'file': v['file']} in val:
                        val.append({'ip': rdata.address, 'file': v['file']})
                    res[key] = val
            except NoSOA:
                continue
        return res

    @staticmethod
    def getreverseMap(zones):
        res = {}
        for k, v in Zone.getZones().items():
            try:
                zone = dns.zone.from_file(
                    v['file'], os.path.basename(v['file']), relativize=False)
                for (name, ttl, rdata) in zone.iterate_rdatas('A'):
                    value = res.get(rdata.address, [])
                    value.append(
                        {'file': v['file'], 'domain': name.to_text().rstrip('.')})
                    res[rdata.address] = value
            except NoSOA:
                continue
        return res


class BindDNS(DNS):

    def __init__(self):
        self.__jslocation__ = "j.sal.bind"
        self.__imports__ = "dnspython3"
        DNS.__init__(self)

    @property
    def zones(self):
        res = []
        for k, v in Zone.getZones().items():
            z = Zone(k, v['type'], v['file'])
            res.append(z)
        return res

    @property
    def map(self):
        return Zone.getMap(self.zones)

    @property
    def reversemap(self):
        return Zone.getreverseMap(self.zones)

    def start(self):
        """
        Start bind9 server.
        """
        self._logger.info('STARTING BIND SERVICE')
        _, out, _ = j.sal.process.execute(
            'service bind9 start', showout=True)
        self._logger.info(out)

    def stop(self):
        """
        Stop bind9 server.
        """
        self._logger.info('STOPPING BIND SERVICE')
        _, out, _ = j.sal.process.execute(
            'service bind9 stop', showout=True)
        self._logger.info(out)

    def restart(self):
        """
        Restart bind9 server.
        """
        self._logger.info('RESTSRTING BIND SERVICE')
        _, out, _ = j.sal.process.execute(
            'service bind9 restart', showout=True)
        self._logger.info(out)

    def updateHostIp(self, host, ip):
        """
        Update the IP of a host.

        @param host string: hostname
        @param ip   string: ip

        """
        map = self.map
        record = map.get(host)
        if not record:
            raise j.exceptions.RuntimeError("Invalid host name")

        for r in record:
            file = r['file']
            old_ip = r['ip']
            zone = dns.zone.from_file(
                file, os.path.basename(file), relativize=False)
            for k, v in zone.items():
                for dataset in v.rdatasets:
                    for item in dataset.items:
                        if hasattr(item, 'address') and item.address == old_ip:
                            item.address = ip
                            zone.to_file(file)
        self.restart()

    def addRecord(self, domain, host, ip, klass, type, ttl):
        """
        Add an A record.

        @param domain string: domain
        @param host string: host
        @param ip string: ip
        @param klass string: class
        @param type:
        @param ttl: time to live

        """
        host = "%s." % host
        records = [x for x in self.zones if x.domain == domain]
        if not records:
            raise j.exceptions.RuntimeError("Invalid domain")

        record = records[0]
        file = record.file
        zone = dns.zone.from_file(
            file, os.path.basename(file), relativize=False)
        node = zone.get_node(host, create=True)

        if type == "A":
            t = dns.rdatatype.A

        if klass == "IN":
            k = dns.rdataclass.IN

        ds = node.get_rdataset(t, k, covers=dns.rdatatype.NONE, create=True)
        ds.ttl = ttl
        if type == "A" and klass == "IN":
            item = A(k, t, ip)
            ds.items.append(item)

        # update version
        for k, v in zone.nodes.items():
            for ds in v.rdatasets:
                if ds.rdtype == dns.rdatatype.SOA:
                    for item in ds.items:
                        item.serial += 1

        zone.to_file(file, relativize=False)
        self.restart()

    def deleteHost(self, host):
        """
        Delete host.

        @param host string: host
        """
        host = host.rstrip('.')
        map = self.map
        record = map.get(host)
        if not record:
            raise j.exceptions.RuntimeError("Invalid host name")

        for r in record:
            file = r['file']
            old_ip = r['ip']
            zone = dns.zone.from_file(
                file, os.path.basename(file), relativize=False)
            for k, v in zone.nodes.copy().items():
                if k.to_text() == "%s." % host:
                    zone.delete_node(k)
            # update version
            for k, v in zone.nodes.items():
                for ds in v.rdatasets:
                    if ds.rdtype == dns.rdatatype.SOA:
                        for item in ds.items:
                            item.serial += 1

            zone.to_file(file, relativize=False)
        self.restart()
