from Jumpscale import j

from .CoreDnsClient import CoreDnsClient

JSConfigs = j.application.JSBaseConfigsClass


class CoreDnsFactory(JSConfigs):
    __jslocation__ = "j.sal.coredns"
    _CHILDCLASS = CoreDnsClient

    def get(
        self,
        name=None,
        id=None,
        die=True,
        create_new=True,
        childclass_name=None,
        host="127.0.0.1",
        port=2379,
        user="root",
        password="root",
        **kwargs,
    ):
        """Get Coredns client instance after getting an etcd client instance 
            If client found with name in param 'etcd_instance' , the client instance is used. Otherwise a new etcd client instance is created

        :param name: coredns client name, defaults to None
        :type name: str
        :param id: id of the obj to find, is a unique id
        :param name: of the object, can be empty when searching based on id or the search criteria (kwargs)
        :param search criteria (if name not used) or data elements for the new one being created
        :param die, means will give error when object not found
        :param create_new, if True it will automatically create a new one
        :param childclass_name, if different typen of childclass, specify its name, needs to be implemented in _childclass_selector
        :param etcd_instance: etcd client instance name, defaults to "main"
        :type etcd_instance: str
        :param host: etcd host IPAddress, defaults to "127.0.0.1"
        :type host: str (ipaddr in schema), optional
        :param port: etcd port, defaults to "2379"
        :type port: str (ipport in schema), optional
        :param user: etcd user, defaults to "root"
        :type user: str, optional
        :param password: etcd password, defaults to "root"
        :type password: str, optional
        :return: CoreDns client
        :rtype: CoreDns
        """
        if "etcd_instance" not in kwargs:
            raise j.exceptions.Value("New or existing etcd_instance name required")
        j.clients.etcd.get(name=kwargs["etcd_instance"], host=host, port=port, user=user, password_=password)
        return JSConfigFactory.get(
            self, name=name, id=id, die=die, create_new=create_new, childclass_name=childclass_name, **kwargs
        )

    def test(self):
        # create etcd client
        cl = j.sal.coredns.get(name="main", host="127.0.0.1", password="1234")
        # create zones
        zone1 = cl.zone_create("test.example.com", "10.144.13.199", record_type="A")
        zone2 = cl.zone_create("example.com", "2003::8:1", record_type="AAAA")
        # add records in etcd
        cl.deploy()
        # create zones
        zone2 = cl.zone_create("test.example.com", "10.144.13.198", record_type="A")
        zone3 = cl.zone_create("example.com", "2003::8:2", record_type="AAAA")
        zone4 = cl.zone_create("test2.example.com", "10.144.13.198", record_type="A")
        zone5 = cl.zone_create("example2.com", "2003::8:2", record_type="AAAA")
        # add records in etcd
        cl.deploy()
        # get records from etcd
        cl.zones
        # remove records from etcd
        cl.remove([zone1, zone2, zone3, zone4, zone5])
