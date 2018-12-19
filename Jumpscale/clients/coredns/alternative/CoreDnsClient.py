import json
from ipaddress import (AddressValueError, IPv4Address, IPv6Address,
                       NetmaskValueError)
from urllib.parse import urlparse

from Jumpscale import j

from .ResourceRecord import RecordType, ResourceRecord


JSConfigBase = j.application.JSBaseClass

TEMPLATE = """
etcd_instance = "main"
"""


class CoreDnsClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,
                              template=TEMPLATE, interactive=interactive)
        self._etcd_client = None
        print("CoreDNS", instance)
        self._zones = []

    @property
    def etcd_client(self):
        if not self._etcd_client:
            self._etcd_client = j.clients.etcd.get(self.config.data['etcd_instance'])
        return self._etcd_client

    @property
    def zones(self):
        """get all zones
        """
        if not self._zones:
            self._zones = _load(self.etcd_client)
        return self._zones

    def zone_create(self, domain, rrdata, record_type=RecordType.A, ttl=300, priority=None, port=None):
        """ create new zone .

            domain    : Record Name.  Corresponds to first field in
                      DNS Bind Zone file entries.  REQUIRED.
            rrdata  : Resource Record Data (REQUIRED)
            record_type    : Record Type.  CNAME, A, AAAA, TXT, SRV.  REQUIRED
            ttl     : time to live. default value 300 (optional)
            priority: SRV record priority (optional)
            port    : SRV record port (optional)

            TXT record example  : rrdata = 'this is a TXT record'
            A record example    : rrdata = '1.1.1.1'
            AAAA record example : rrdata = '2003:8:1'
            SRV record example  : rrdata = 'skydns-local.server'
            CNAME record example: rrdata = 'cn1.skydns.local skydns.local.'
        """
        zone = ResourceRecord(domain, rrdata, record_type, ttl, priority, port)
        self._zones.append(zone)
        return zone

    def deploy(self):
        """
        add coredns records in etcd
        :param zones: list of `ResourceRecord` objects that needs to be added
        """
        per_domain = {}
        for zone in self.zones:
            if zone.domain not in per_domain:
                per_domain[zone.domain] = [zone]
            else:
                per_domain[zone.domain].append(zone)

        for zones in per_domain.values():
            if len(zones) > 1:
                for i, zone in enumerate(zones):
                    zone.domain = 'x%d.%s' % (i, zone.domain)

        for zones in per_domain.values():
            for zone in zones:
                self.etcd_client.put(zone.key(), zone.rrdata)

    def remove(self, zones):
        """
        remove coredns records from etcd
        :param zones: list of `ResourceRecord` objects that needs to be removed
        """
        for zone in zones:
            self.etcd_client.api.delete_prefix(zone.key())


def _load(client):
    """
    get all zones from etcd

    Arguments:
        client : ETCD client
    """
    zones = []
    for value, metadata in client.api.get_prefix('/hosts'):
        ss = metadata.key.decode().split('/')

        domain = '.'.join(reversed(ss[2:]))
        value = json.loads(value.decode())

        type_of_record, rrdata = _get_type_and_rdata(value)

        if type_of_record == "SRV":
            zone = ResourceRecord(domain, rrdata, type_of_record, value["ttl"], value["priority"], value["port"])
        else:
            zone = ResourceRecord(domain, rrdata, type_of_record, value["ttl"])

        # zone.domain = _sanitize_domain(zone.domain)
        zones.append(zone)
    return zones


def _get_type_and_rdata(record):
    """get type and data of record

    Arguments:
        record: dict value of zone

    Returns: type and data of type
    """
    if "text" in record:
        return 'TXT', record['text']
    elif "port" in record:
        return 'SRV', record['host']
    elif "cname" in record:
        return 'CNAME', record['cname']
    elif "host" in record:
        rrdata = record['host']
        try:
            IPv6Address(rrdata)
            rtype = 'AAAA'
            return rtype, rrdata
        except (AddressValueError, NetmaskValueError):
            try:
                IPv4Address(rrdata)
                rtype = 'A'
                return rtype, rrdata
            except (AddressValueError, NetmaskValueError):
                pass
    raise KeyError("cannot identify record type %s" % repr(record))


def _sanitize_domain(domain):
    if domain[0] != 'x':
        return domain

    prefix, rest = domain.split('.', 1)
    try:
        int(prefix[1:])
        return rest
    except TypeError:
        return domain
