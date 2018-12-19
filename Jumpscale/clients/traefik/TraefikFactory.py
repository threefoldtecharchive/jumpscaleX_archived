from Jumpscale import j

from .TraefikClient import (Backend, BackendServer, Frontend, FrontendRule,
                            TraefikClient)

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class TraefikFactory(JSConfigBaseFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.traefik"
        JSConfigBaseFactory.__init__(self, TraefikClient)

    def configure(self, instance_name, host, port="2379", user="root", password="root"):
        """
        gets an instance of traefik client with etcd configurations directly
        """
        j.clients.etcd.get(instance_name, data={"host": host, "port": port, "user": user, "password_": password})
        return self.get(instance_name, data={"etcd_instance": instance_name})

    def test(self):
        cl = self.configure("test", host="10.102.64.236", user="root", password="v16ffehxnq")

        # create a proxy object. A proxy has a name and is combination of frontends and backends
        proxy = cl.proxy_create('myproxy')

        # set a backend on your proxy
        backend = proxy.backend_set(endpoints=['http://192.168.1.5:8080'])
        # add another server to your backend
        server = backend.server_add('http://192.168.1.15:8080')
        # set the weight for the load balancing on the second backend server
        server.weight = '20'

        # set a frontend on your proxy
        frontend = proxy.frontend_set('my.domain.com')

        # write the configuration into etcd
        proxy.deploy()
        # delete all frontend and backend configuration of this proxy from etcd
        proxy.delete()
