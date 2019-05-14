from .CoreDnsClient import CoreDnsClient, _get_type_and_rdata, _load, _sanitize_domain
from .ResourceRecord import ResourceRecord, RecordType
import json


class Meta:
    def __init__(self, key):
        self.key = key


class Api:
    def __init__(self, client):
        self._client = client

    def get(self, key):
        if isinstance(key, str):
            key = key.encode()
        value = self._client._data.get(key)
        return (value, Meta(key))

    def get_prefix(self, prefix):
        if isinstance(prefix, str):
            prefix = prefix.encode()
        for k, v in list(self._client._data.items()):
            if k.startswith(prefix):
                yield (v, Meta(k))

    def delete_prefix(self, prefix):
        if isinstance(prefix, str):
            prefix = prefix.encode()
        for k in list(self._client._data.keys()):
            if k.startswith(prefix):
                del self._client._data[k]


class EtcdClientMock:
    def __init__(self):
        self._data = {}
        self.api = Api(self)

    def put(self, key, value):
        if isinstance(value, str):
            value = value.encode()
        self._data[key.encode()] = value

    def get(self, key):
        return self._data.get(key)


def test_zone_deploy_remove():
    client = EtcdClientMock()
    zones = []
    zones.append(ResourceRecord("test1.example.com", "10.144.13.199", record_type="A"))
    zones.append(ResourceRecord("test2.example.com", "2003::8:1", record_type="AAAA"))
    for zone in zones:
        client.put(zone.key(), zone.rrdata)

    for key, value in client._data.items():
        assert key.decode() in [z.key() for z in zones]
        for zone in zones:
            if zone.key() == key.decode():
                assert json.loads(value.decode()) == json.loads(zone.rrdata)

    for zone in zones:
        client.api.delete_prefix(zone.key())
    assert client._data == {}


def test_backend_load():
    client = EtcdClientMock()
    client._data = {
        b"/hosts/com/example/test1": b'{"ttl": 300, "host": "10.144.13.199"}',
        b"/hosts/com/example/test2": b'{"ttl": 300, "host": "2003::8:1"}',
    }
    expected = [
        ResourceRecord("test1.example.com", "10.144.13.199", record_type=RecordType.A),
        ResourceRecord("test2.example.com", "2003::8:1", record_type=RecordType.A),
    ]
    zones = _load(client)
    assert len(zones) == 2
    zones[0].host = "test1.example.com"
    zones[0].ttl = 300
    zones[0].type = RecordType.A
    zones[1].host = "test2.example.com"
    zones[1].ttl = 300
    zones[1].type = RecordType.A


def test_type_and_rdata():
    type_of_record, metadata = _get_type_and_rdata({"ttl": 300, "host": "10.144.13.199"})
    assert type_of_record == "A"
    assert metadata == "10.144.13.199"
    type_of_record, metadata = _get_type_and_rdata({"ttl": 300, "host": "2003::8:1"})
    assert type_of_record == "AAAA"
    assert metadata == "2003::8:1"


def test_multiple_ip_per_domain():
    zones = []
    zones.append(ResourceRecord("test.example.com", "192.168.1.1", record_type="A"))
    zones.append(ResourceRecord("test.example.com", "192.168.1.2", record_type="A"))
    zones.append(ResourceRecord("test.example.com", "192.168.1.10", record_type="A"))
    zones.append(ResourceRecord("test2.example.com", "192.168.10.1", record_type="A"))
    zones.append(ResourceRecord("test2.example.com", "192.168.10.2", record_type="A"))
    zones.append(ResourceRecord("test3.example.com", "192.168.30.1", record_type="A"))
    per_domain = {}
    for zone in zones:
        if zone.domain not in per_domain:
            per_domain[zone.domain] = [zone]
        else:
            per_domain[zone.domain].append(zone)

    for domain in per_domain.keys():
        if len(per_domain[domain]) > 1:
            for i, zone in enumerate(per_domain[domain]):
                per_domain[domain][i].domain = "x%d.%s" % (i, zone.domain)


def test_sanitize_domain():
    for test in [
        {"domain": "test.example.com", "expect": "test.example.com"},
        {"domain": "x1.test.example.com", "expect": "test.example.com"},
        {"domain": "x10.test.example.com", "expect": "test.example.com"},
        {"domain": "a1.test.example.com", "expect": "a1.test.example.com"},
    ]:
        result = _sanitize_domain(test["domain"])
        assert test["expect"] == result
