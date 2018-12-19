from Jumpscale import j

from .service import Service
from .errors import ServiceExistError, ServiceNotFoundError

JSConfigBase = j.application.JSBaseClass

TEMPLATE = """
etcd_instance = "main"
public_ips = []
"""


class WebGateway(JSConfigBase):
    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        self.etcd = j.clients.etcd.get(self.config.data['etcd_instance'])
        self.traefik = j.sal.traefik.configure(instance,
                                               host=self.etcd.config.data['host'],
                                               port=self.etcd.config.data['port'],
                                               user=self.etcd.config.data['user'],
                                               password=self.etcd.config.data['password_'])
        self.coredns = j.sal.coredns.configure(instance,
                                               host=self.etcd.config.data['host'],
                                               port=self.etcd.config.data['port'],
                                               user=self.etcd.config.data['user'],
                                               password=self.etcd.config.data['password_'])
        self.public_ips = self.config.data.get('public_ips') or []
        self._services = None

    def public_ips_set(self, public_ips):
        """
        change the public ip that are used by the webgateway

        this method will update the webgateway config wit the new pulic ips
        and update all the configuration of the existing service to use the new ips

        :param public_ips: list of public ips to be used by te webgateway
        :type public_ips: [str]
        """
        self.config.data_set('public_ips', public_ips)
        self.config.data.save()

        # update
        for service in self.services:
            service.public_ips = public_ips
            service.deploy()

    @property
    def services(self):
        """
        list all the service exposed by the webgateway

        :return: list of service
        :rtype: list
        """
        if not self._services:
            self._services = self._load_services()
        return self._services

    def _load_services(self):
        services = []
        for name in self.traefik.proxies.keys():
            services.append(Service(name, self.public_ips, self.traefik, self.coredns))
        return services

    def service_create(self, name):
        """
        create a new service that you want to expose using the webgateway
        :param name: name of your service
        :type name: str
        :raises ServiceExistError: raised if  service with the same name already exists
        :return: service object
        :rtype: sal.webgateway.service.Service
        """
        if name in [s.name for s in self.services]:
            raise ServiceExistError("a service with name %s already exist. maybe you are looking for `service_get(%s)`" % (name, name))

        service = Service(name, self.public_ips, self.traefik, self.coredns)
        self.services.append(service)
        return service

    def service_get(self, name):
        """
        retrieve an existing service

        :param name: name of the service
        :type name: str
        :raises ServiceNotFoundError: raised when not service with the name provided is found
        :return: service object
        :rtype: sal.webgateway.service.Service
        """

        for service in self.services:
            if service.name == name:
                return service
        raise ServiceNotFoundError("no service named %s found" % name)
