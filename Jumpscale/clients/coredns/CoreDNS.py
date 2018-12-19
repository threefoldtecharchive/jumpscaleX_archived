""" A Jumpscale connection to the etcd backend for CoreDNS Zone and RRecords

"""

from copy import deepcopy
import json
import math
from ipaddress import IPv4Address, IPv6Address
from ipaddress import AddressValueError, NetmaskValueError

TEMPLATE = """
etcdpath = "skydns"
secrets_ = ""
"""

class ResourceRecord:

    def __init__(self, name, type, ttl, rrdata,
                             priority=None, port=None # SRV
                ):
        """ DNS Resource Record.

            name    : Record Name.  Corresponds to first field in
                      DNS Bind Zone file entries.  REQUIRED.
            type    : Record Type.  CNAME, A, AAAA, TXT, SRV.  REQUIRED
            ttl     : time to live.  REQUIRED
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
            rrdata = ''

        self.type = type.upper()
        if self.type == 'CNAME':
            self.cname, rrdata = rrdata.split(' ')
        self.name = name
        self.port = port
        self.priority = priority
        self.ttl = ttl
        self.weight = 100
        self._rrdata = rrdata


    @property
    def rrdata(self):
        """ reconstructs CoreDNS/etcd-style JSON data format
        """
        res = {'ttl': self.ttl}
        rdatafield = 'host' # covers SRV, A, AAAA and CNAME
        if self.type == 'TXT':
            rdatafield = 'text'
        elif self.type == 'SRV':
            res['priority'] = self.priority
            res['port'] = self.port
        elif self.type == 'CNAME':
            res['cname'] = self._rrdata # hmmm... weird, these being inverted
            res['host'] = self.cname    # weeeeird....
        res[rdatafield] = self._rrdata
        return json.dumps(res)

    def __str__(self):
        if self.type == 'TXT':
            rrdata = '"%s"' % self._rrdata
        else:
            rrdata = self._rrdata
        extra = 'IN\t%s' % self.type.upper()
        if self.type == 'SRV':
            extra += '\t%d %d %d' % (self.priority, self.weight, self.port)
        return "%s\t%d\t%s\t%s" % \
            (self.name, self.ttl, extra, rrdata)

    def __repr__(self):
            return "'%s'" % str(self)


class CoreDNS:

    __jsbase__ = 'j.tools.configmanager._base_class_config'
    _template = TEMPLATE

    def __init__(self, instance, data={}, parent=None, interactive=False,
                                 started=True):
        self._etcd = None
        print ("CoreDNS", instance)
        self.zones = {}
        self.CoreDNSZone = self._jsbase(('CoreDNSZone', '.CoreDNS'))
        self.ResourceRecord = ResourceRecord

    @property
    def secrets(self):
        res={}
        if "," in self.config.data["secrets_"]:
            items = self.config.data["secrets_"].split(",")
            for item in items:
                if item.strip()=="":
                    continue
                nsname,secret = item.split(":")
                res[nsname.lower().strip()]=secret.strip()
        else:
            res["default"]=self.config.data["secrets_"].strip()
        return res

    @property
    def etcdpath(self):
        return self.config.data["etcdpath"]

    def zone_exists(self, name):
        return name in self.zones

    def zone_del(self, name):
        ns = self.zones[name]
        try:
            ns.zonedb.delete_all()
        except KeyError:
            pass
        self.zones.pop(name)
        del ns

    def zone_get(self, name, *args, **kwargs):
        if not name in self.zones:
            pth = self.etcdpath
            if name:
                pth = "%s/%s" % (pth, name)
            etcd = self._j.clients.etcd.get(self.instance) # use same instance
            db = etcd.namespace_get(pth)
            self.zones[name] = CoreDNSZone(self, name, db)
        return self.zones[name]

    def zone_new(self, name, secret="", maxsize=0, die=False):
        if self.zone_exists(name):
            if die:
                raise RuntimeError("namespace already exists:%s" % name)
            return self.zone_get(name)

        #if secret is "" and "default" in self.secrets.keys():
        #    secret = self.secrets["default"]

        return self.zone_get(name)


class DNSZone:

    def __init__(self, name, dns_name=None, etcd=None, description=None):
        self.name = name
        self.dns_name = dns_name
        self._etcd = etcd
        if description is None:
            description = dns_nme
        self.description = description
        self.resource_records = []

def get_type_and_rdata(record):
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


class CoreDNSZone:

    def __init__(self, coredns, zone, db):

        self.coredns = coredns
        self.zone = zone
        self.zonedb = db

    def set(self, key, rr):
        """ sets a CoreDNS key from a ResourceRecord
        """
        self.zonedb.set(key, rr.rrdata)

    def del(self, key):
        """ deletes a single CoreDNS key
        """
        self.zonedb.delete(key)

    def get(self, key):
        """ gets a CoreDNS entry, constructs a ResourceRecord from it
        """
        record = self.zonedb.get(key)
        record = json.loads(record)
        zname = self._get_zonename()
        name = "%s." % zname
        rtype, rrdata = get_type_and_rdata(record)
        print ("get", record, rtype, repr(rrdata))
        ttl = record['ttl']
        if rtype == 'SRV':
            port = record['port']
            priority = record['priority']
        else:
            port = None
            priority = None
        if rtype == 'CNAME':
            rrdata = '%s %s' % (record['cname'], rrdata)
        return ResourceRecord(name, rtype, ttl, rrdata, priority, port)

    def get_arecords(self, subname=""):
        res = []
        zname = self._get_zonename()
        change_to_dot = None
        a_rec_match = None
        for k, record in self.zonedb.items().items():
            print ("arec", self.zone, repr(k), subname, record)
            record = json.loads(record)
            ttl = record['ttl']
            rtype = None
            priority = None
            port = None
            name = zname # apparently should always return zone-name
            name = "%s." % name
            rtype, rrdata = get_type_and_rdata(record)
            if "text" in record: # skip TXT
                continue
            elif "port" in record: # skip SRV
                continue
            elif "cname" in record:
                print ("found cname", record, zname)
                if rrdata == zname + ".":
                    change_to_dot = rrdata
                    rrdata = "."
                if subname:
                    name = "%s.%s" % (subname, name)
            elif "host" in record:
                if rtype == 'AAAA':
                    continue
            else:
                raise Exception("unknown record type %s search %s in %s" % \
                                (repr(record), subname, self.db.nsname))
            # filter non-matching subname
            if rtype == 'CNAME':
                rrdata = '%s %s' % (record['cname'], rrdata)
            rr = ResourceRecord(name, rtype, ttl, rrdata, priority, port)
            if rtype == 'A':
                a_rec_match = rr
                print ("found a-rec", a_rec_match.rrdata)
            if rtype.lower() not in ['a', 'cname']:
                continue
            #if k != subname:
            #    continue
            res.append(rr)
        nres = []
        if change_to_dot and a_rec_match:
            for rr in res:
                if rr.type == 'A':
                    rr.name = "."

        res += nres
        #print ("checking", res, subname, zname)
        if res or subname:
            return res
        # hmmm.... need to split and do a subname query....
        # aiyaaaa! actually have to get a new namespace!
        subname, _, zname = zname.partition('.')
        if not zname:
            return []
        zone = zname.split(".")
        zone.reverse()
        zone = '/'.join(zone)
        print ("split", subname, zname, zone)
        subzonedb = self.coredns.zone_get(zone)
        return subzonedb.get_arecords(subname)

    def _get_zonename(self):
        zname = self.zone.split("/")
        zname.reverse()
        return '.'.join(zname)

    def get_aaaarecords(self, subname=""):
        res = []
        zname = self._get_zonename()
        change_to_dot = None
        aaaa_rec_match = None
        for k, record in self.zonedb.items(subname).items():
            print (k, subname, record)
            record = json.loads(record)
            ttl = record['ttl']
            priority = None
            port = None
            name = zname # apparently should always return zone-name
            name = "%s." % name
            rtype, rrdata = get_type_and_rdata(record)
            if "text" in record: # skip TXT
                continue
            elif "port" in record: # skip SRV
                continue
            elif "cname" in record:
                print ("found cname", record, zname)
                if rrdata == zname + ".":
                    change_to_dot = rrdata
                    rrdata = "."
            elif "host" in record:
                if rtype == 'A':
                    continue
            else:
                raise Exception("unknown record type %s search %s in %s" % \
                                (repr(record), subname, self.db.nsname))
            # filter non-matching subname
            if rtype == 'CNAME':
                rrdata = '%s %s' % (record['cname'], rrdata)
            rr = ResourceRecord(name, rtype, ttl, rrdata, priority, port)
            if rtype == 'AAAA':
                aaaa_rec_match = deepcopy(rr)
                print ("found aaaa-rec", aaaa_rec_match.rrdata)
            #if k != subname:
            #    continue
            res.append(rr)
        nres = []
        if change_to_dot and aaaa_rec_match:
            for rr in res:
                if rr.type == 'AAAA':
                    rr.name = "."
            nres.append(aaaa_rec_match)
        elif subname:
            for rr in res:
                if rr.type == 'AAAA':
                    rr.name = "%s.%s" % (subname, name)

        return res + nres

    def get_txtrecords(self, subname=""):
        res = []
        zname = self._get_zonename()
        change_to_dot = None
        a_rec_match = None
        for k, record in self.zonedb.items(subname).items():
            print (zname, subname, repr(k), subname, record)
            record = json.loads(record)
            ttl = record['ttl']
            priority = None
            port = None
            rtype, rrdata = get_type_and_rdata(record)
            if rtype != 'TXT':
                continue
            name = zname # apparently should always return zone-name
            name = "%s." % name
            rr = ResourceRecord(name, rtype, ttl, rrdata, priority, port)
            res.append(rr)

        return res

    def get_cnamerecords(self, subname=""):
        res = []
        zname = self._get_zonename()
        for k, record in self.zonedb.items(subname).items():
            print ("cname", repr(k), subname, record)
            record = json.loads(record)
            ttl = record['ttl']
            priority = None
            port = None
            rtype, rrdata = get_type_and_rdata(record)
            if rtype != 'CNAME':
                continue
            if rrdata == zname + ".":
                change_to_dot = rrdata
                rrdata = "."
                print ("found cname", record)
            name = zname # apparently should always return zone-name
            name = "%s." % name
            rrdata = '%s %s' % (record['cname'], rrdata)
            rr = ResourceRecord(name, rtype, ttl, rrdata, priority, port)
            res.append(rr)

        return res

    def get_srvrecords(self, subname=""):
        res = []
        zname = self._get_zonename()
        change_to_dot = None
        a_rec_match = None
        aaaa_rec_match = None
        for k, record in self.zonedb.items(subname).items():
            print (k, subname, record)
            record = json.loads(record)
            ttl = record['ttl']
            priority = None
            port = None
            name = zname # apparently should always return zone-name
            name = "%s." % name
            rtype, rrdata = get_type_and_rdata(record)
            if "text" in record:
                continue
            elif "cname" in record:
                rrdata = record['host']
                if not rrdata.endswith('.'):
                    rrdata += "."
            elif "port" in record:
                port = record['port']
                priority = record['priority']
                if not rrdata.endswith('.'):
                    rrdata += "."
            elif "host" in record:
                print ("found ", rtype, rrdata, zname)
                if rtype == 'A':
                    change_to_dot = rrdata
                    a_rec_match = ResourceRecord('.', rtype, ttl, rrdata,
                                                   priority, port)
                    rrdata = '.'
                if rtype == 'AAAA':
                    if subname:
                        _name = "%s.%s" % (subname, name)
                    elif k:
                        _name = "%s.%s" % (k, name)
                    else:
                        _name = name
                    aaaa_rec_match = ResourceRecord(_name, rtype, ttl, rrdata,
                                                   priority, port)
                    rrdata = _name

            else:
                raise Exception("unknown record type %s search %s in %s" % \
                                (repr(record), subname, self.db.nsname))
            if subname and rtype != 'AAAA':
                name = "%s.%s" % (subname, name)
            if rtype == 'CNAME':
                rrdata = '%s %s' % (record['cname'], rrdata)
            rr = ResourceRecord(name, rtype, ttl, rrdata, priority, port)
            res.append(rr)
        nres = []
        count = 0
        for rr in res:
            if rr.type in ['A', 'AAAA', 'CNAME', 'SRV']:
                count += 1
        for rr in res:
            if rr.type in ['A', 'AAAA', 'CNAME', 'SRV']:
                rr.weight = int(math.floor(100 / count))
        for rr in res:
            if rr.type in ['A', 'AAAA', 'CNAME']:
                rr.type = 'SRV'
                rr.priority = 10
                rr.port = 0
        if change_to_dot and a_rec_match:
            nres.append(a_rec_match)
        if aaaa_rec_match:
            nres.append(aaaa_rec_match)

        return res + nres

    def get_records(self, subname="", qtype=None):
        """ this function is extremely similar to "host" and "dig".
            pass in the subname (if needed) and pass in the record
            type (if needed).

            $ host -t TXT x1.skydns.local server OR
            $ dig @server x1.skydns.local TXT

                ==>

            $ js_shell
            d = j.clients.coredns.get()
            z = d.zone_get('local/skydns/x1')
            print (z.get_records('', 'txt')

        """
        if qtype is None:
            qtype = 'A'
        qtype = qtype.lower()
        if qtype == 'a':
            return self.get_arecords(subname)
        elif qtype == 'aaaa':
            return self.get_aaaarecords(subname)
        elif qtype == 'txt':
            return self.get_txtrecords(subname)
        elif qtype == 'cname':
            return self.get_cnamerecords(subname)
        elif qtype == 'srv':
            return self.get_srvrecords(subname)
        return []
