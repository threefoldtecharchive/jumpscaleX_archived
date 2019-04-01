import time
from urllib.parse import urlparse

from Jumpscale import j
from .ZeroOSClient import ZeroOSClient


class ZeroOSFactory(j.application.JSBaseConfigsClass):
    """
    """
    _CHILDCLASS = ZeroOSClient
    __jslocation__ = "j.clients.zos"

    def get_by_id(self, node_id):
        directory = j.clients.threefold_directory.get()
        node, resp = directory.api.GetCapacity(node_id)
        resp.raise_for_status()
        u = urlparse(node.robot_address)
        node = self.get(node_id)
        if node.client.config.data['host'] != u.hostname:
            node.client.config.data_set('host', u.hostname)
            node.client.config.save()
        return self.get(node_id)

    def zero_node_ovh_install(self, OVHHostName, OVHClient, zerotierNetworkID, zerotierClient):
        """

        OVHHostName is server name as known by OVH

        get clients as follows:
        - zerotierClient = j.clients.zerotier.get(instance='main', data={'data': ZT_API_TOKEN})
        - OVHClient = j.clients.ovh.get(...)

        """

        cl = OVHClient

        self._log_debug("booting server {} to zero-os".format(OVHHostName))
        task = cl.zero_os_boot(target=OVHHostName, zerotierNetworkID=zerotierNetworkID)
        self._log_debug("waiting for {} to reboote".format(OVHHostName))
        cl.server_wait_reboot(OVHHostName, task['taskId'])
        ip_pub = cl.server_detail_get(OVHHostName)["ip"]
        self._log_info("ip addr is:%s" % ip_pub)

        while True:
            try:
                network = zerotierClient.get_network(network_id=zerotierNetworkID)
                member = network.member_get(public_ip=ip_pub)
                ipaddr_priv = member.private_ip
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                self._log_error(e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                self._log_error("please authorize the server with the public ip %s in the zerotier network" % ip_pub)
                time.sleep(1)

        self._log_debug("server found: %s" % member['id'])
        self._log_debug("zerotier IP: %s" % ipaddr_priv)

        return ip_pub, ipaddr_priv

    def zero_node_packetnet_install(self, packetnetClient, zerotierClient, project_name,
                                    plan_type, location, server_name, zerotierNetworkID, ipxe_base='https://bootstrap.grid.tf/ipxe/master'):
        """
        packetnetClient = j.clients.packetnet.get('TOKEN')
        zerotierClient = j.clients.zerotier.get(instance='main', data={'token': 'TOKEN'})
        project_name = packet.net project
        plan_type: one of "Type 0", "Type 1", "Type 2" ,"Type 2A", "Type 3", "Type S"
        location: one of "Amsterdam", "Tokyo", "Synnuvale", "Parsippany"
        server_name: name of the server that is going to be created
        zerotierNetworkID: zertotier network id
        ipxe_base: change this to the version you want, use master branch by default
        """

        valid_plan_types = ("Type 0", "Type 1", "Type 2",
                            "Type 2A", "Type 3", "Type S")  # FIXME
        if plan_type not in valid_plan_types:
            j.exceptions.Input("bad plan type %s. Valid plan type are %s" % (
                plan_type, ','.join(valid_plan_types)))

        if zerotierNetworkID:
            ipxe_url = "%s/%s" % (ipxe_base, zerotierNetworkID)
        else:
            ipxe_url = None

        hostname = server_name

        # find project id
        project_ids = [project.id for project in packetnetClient.projects if project.name == project_name]
        if not project_ids:
            raise j.exceptions.NotFound(
                'No projects found with name %s' % project_name)
        project_id = project_ids[0]
        packetnetClient.project_id = project_id

        packetnetClient.startDevice(hostname=server_name, plan=plan_type, facility=location, os='ubuntu_17_04',
                                    ipxeUrl=ipxe_url, wait=True, remove=False)

        device = packetnetClient.getDevice(server_name)
        ip_pub = [netinfo['address']
                  for netinfo in device.ip_addresses if netinfo['public'] and netinfo['address_family'] == 4]

        while True:
            try:
                network = zerotierClient.get_network(network_id=zerotierNetworkID)
                member = network.member_get(public_ip=ip_pub[0])
                ipaddr_priv = member.private_ip
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                self._log_error(e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                self._log_error("please authorize the server with the public ip %s in the zerotier network" % ip_pub[0])
                time.sleep(1)

        self._log_debug("server found: %s" % device.id)
        self._log_debug("zerotier IP: %s" % ipaddr_priv)

        return ip_pub, ipaddr_priv

    def get_from_itsyouonline(self, name="default", iyo_instance="default",
                              iyo_organization=None, host="localhost", port=6379, reset=False, save=True):
        """

        :param name: name for this instance
        :param iyo_instance: the instance name of the IYO client you will use
        :param iyo_organization: the organization in IYO to connect
        :param host: addr of the zos
        :param port: por tof the zos (for the redis protocol)
        :param reset: to refresh you'r jwt
        :param save: if the resulting client will be stored on your bcdb
        :return:
        """

        if iyo_organization is None:
            raise RuntimeError("need to specify name of organization.")

        jwt_name = j.core.text.strip_to_ascii_dense("zos_%s" % iyo_organization)

        iyo = j.clients.itsyouonline.get(name=iyo_instance)
        jwt = iyo.jwt_get(name=jwt_name, scope="user:memberof:%s" % iyo_organization,
                          reset=reset)  # there should be enough protection in here to refresh

        # print(jwt)

        cl = self.get(name=name, host=host, port=port, password=jwt.jwt, ssl=True)
        print(cl)
        cl.ping()
        if save:
            cl.save()
        return cl

    def test(self):
        """
        js_shell 'j.clients.zos.test()'
        :return:
        """

        cl = j.clients.zos.get_from_itsyouonline(
            name="default", host="10.102.90.219", port=6379, iyo_organization="tf-production", reset=True)

        print(cl)

        print(cl.ping())

        # use j.clients.zoscmd... to start a local zos
        # connect client to zos do quite some tests
