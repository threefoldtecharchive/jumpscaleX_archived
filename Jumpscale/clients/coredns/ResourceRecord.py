import json
from enum import Enum


class RecordType(Enum):
    A = "A"
    AAAA = "AAAA"
    SRV = "SRV"
    TXT = "TXT"


class ResourceRecord:
    def __init__(self, domain, rrdata, record_type=RecordType.A, ttl=300, priority=None, port=None):  # SRV
        """ DNS Resource Record.

            domain    : Record Name.  Corresponds to first field in
                      DNS Bind Zone file entries.  REQUIRED.
            record_type    : Record Type.  CNAME, A, AAAA, TXT, SRV.  REQUIRED
            ttl     : time to live. default value 300 (optional)
            port    : SRV record port (optional)
            priority: SRV record priority (optional)
            rrdata  : Resource Record Data (REQUIRED)

            TXT record example  : rrdata = 'this is a TXT record'
            A record example    : rrdata = '1.1.1.1'
            AAAA record example : rrdata = '2003:8:1'
            SRV record example  : rrdata = 'skydns-local.server'
            CNAME record example: rrdata = 'cn1.skydns.local skydns.local.'
        """

        if rrdata is None:
            rrdata = ""

        self.type = record_type
        if self.type == "CNAME":
            self.cname, rrdata = rrdata.split(" ")
        self.domain = domain
        self.port = port
        self.priority = priority
        self.ttl = ttl
        self.weight = 100
        self._rrdata = rrdata

    @property
    def rrdata(self):
        """
        reconstructs CoreDNS/etcd-style JSON data format
        """
        res = {"ttl": self.ttl}
        rdatafield = "host"  # covers SRV, A, AAAA and CNAME
        if self.type == RecordType.TXT:
            rdatafield = "text"
        elif self.type == RecordType.SRV:
            res["priority"] = self.priority
            res["port"] = self.port
        elif self.type == "CNAME":
            res["cname"] = self._rrdata
            res["host"] = self.cname
        res[rdatafield] = self._rrdata
        return json.dumps(res)

    def key(self):
        """
        return the key used to store this entry in etcd
        """
        domain_parts = self.domain.split(".")
        # The key for coredns should start with path(/hosts) and the domain reversed
        # i.e. test.com => /hosts/com/test
        key = "/hosts/{}".format("/".join(domain_parts[::-1]))
        return key

    def __str__(self):
        if self.type == "TXT":
            rrdata = '"%s"' % self._rrdata
        else:
            rrdata = self._rrdata
        extra = "IN\t%s" % self.type
        if self.type == "SRV":
            extra += "\t%d %d %d" % (self.priority, self.weight, self.port)
        return "%s\t%d\t%s\t%s" % (self.domain, self.ttl, extra, rrdata)

    def __repr__(self):
        return "'%s'" % str(self)
