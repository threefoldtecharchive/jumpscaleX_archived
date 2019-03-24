""" A Jumpscale-configurable wrapper for CoreDNS

    unit tests are in core9 tests/jumpscale_tests/test12_etcd_coredns.py
"""

from .CoreDnsClient import CoreDnsClient
from Jumpscale import j
JSConfigs = j.application.JSBaseConfigsClass


class CoreDnsFactory(JSConfigs):
    __jslocation__ = "j.clients.coredns"
    __jsbase__ = 'j.tools.configmanager._base_class_configs'
    _CHILDCLASS = CoreDnsClient

    def configure(self, name, host="127.0.0.1", port="2379", user="root", password_="root", etcd_instance="main"):
        """
        gets an instance of coredns client with etcd configurations directly
        """
        j.clients.etcd.get(etcd_instance, host=host, port=port, user=user, password_=password_)
        return self.get(name, etcd_instance=etcd_instance)

    def test(self,client):
        """
        e.g. client = j.sal.coredns.configure(instance_name="main", host="127.0.0.1", password="1234")
        :param client:
        :return:
        """

        # create zones
        zone1 = client.zone_create('test.example.com', '10.144.13.199', record_type='A')
        zone2 = client.zone_create('example.com', '2003::8:1', record_type='AAAA')
        # add records in etcd
        client.deploy()
        # create zones
        zone2 = client.zone_create('test.example.com', '10.144.13.198', record_type='A')
        zone3 = client.zone_create('example.com', '2003::8:2', record_type='AAAA')
        zone4 = client.zone_create('test2.example.com', '10.144.13.198', record_type='A')
        zone5 = client.zone_create('example2.com', '2003::8:2', record_type='AAAA')
        # add records in etcd
        client.deploy()
        # get records from etcd
        client.zones
        # remove records from etcd
        client.remove([zone1, zone2, zone3, zone4, zone5])
