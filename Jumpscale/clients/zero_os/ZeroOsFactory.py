import time
from urllib.parse import urlparse

from Jumpscale import j

JSFactoryBaseClass = j.application.JSFactoryBaseClass
logger = j.logger.get(__name__)


class ZeroOSClientFactory(JSFactoryBaseClass):
    """""
    A higher level zos client

    :return: Zos client from sal_zos
    :rtype: Node
    """

    __jslocation__ = "j.clients.zos"

    def get(self, name='main', data={}):
        cl = j.clients.zos_protocol.get(name=name, **data)
        return j.sal_zos.node.get(cl)

    def list(self, prefix=''):
        return j.clients.zos_protocol.list(prefix=prefix)

    def count(self):
        return j.clients.zos_protocol.count()

    def delete(self, name):
        return j.clients.zos_protocol.delete(name)

    def exists(self, name):
        return j.clients.zos_protocol.exists(name)

    def getall(self):
        return j.clients.zos_protocol.getall()

    def new(self, name, data={}):
        return j.clients.zos_protocol.new(name=name, **data)

    def get_by_id(self, node_id):
        directory = j.clients.threefold_directory.get()
        node, resp = directory.api.GetCapacity(node_id)
        resp.raise_for_status()
        u = urlparse(node.robot_address)
        node = self.get(node_id)
        if node.client.host != u.hostname:
            node.client.host = u.hostname
            node.client.save()
        return self.get(node_id)

    def zero_node_ovh_install(self, OVHHostName, OVHClient, zerotierNetworkID, zerotierClient):
        """

        OVHHostName is server name as known by OVH

        get clients as follows:
        - zerotierClient = j.clients.zerotier.get(name='main', data={'data': ZT_API_TOKEN})
        - OVHClient = j.clients.ovh.get(...)

        """

        cl = OVHClient

        logger.debug("booting server {} to zero-os".format(OVHHostName))
        task = cl.zero_os_boot(target=OVHHostName, zerotierNetworkID=zerotierNetworkID)
        logger.debug("waiting for {} to reboote".format(OVHHostName))
        cl.server_wait_reboot(OVHHostName, task['taskId'])
        ip_pub = cl.server_detail_get(OVHHostName)["ip"]
        logger.info("ip addr is:%s" % ip_pub)

        while True:
            try:
                network = zerotierClient.get_network(network_id=zerotierNetworkID)
                member = network.member_get(public_ip=ip_pub)
                ipaddr_priv = member.private_ip
                break
            except RuntimeError as e:
                # case where we don't find the member in zerotier
                logger.error(e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                logger.error("please authorize the server with the public ip %s in the zerotier network" % ip_pub)
                time.sleep(1)

        logger.debug("server found: %s" % member['id'])
        logger.debug("zerotier IP: %s" % ipaddr_priv)

        return ip_pub, ipaddr_priv

    def zero_node_packetnet_install(self, packetnetClient, zerotierClient, project_name,
                                    plan_type, location, server_name, zerotierNetworkID, ipxe_base='https://bootstrap.grid.tf/ipxe/master'):
        """
        packetnetClient = j.clients.packetnet.get('TOKEN')
        zerotierClient = j.clients.zerotier.get(name='main', data={'token': 'TOKEN'})
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
                logger.error(e)
                time.sleep(1)
            except IndexError as e:
                # case were we the member doesn't have a private ip
                logger.error("please authorize the server with the public ip %s in the zerotier network" % ip_pub[0])
                time.sleep(1)

        logger.debug("server found: %s" % device.id)
        logger.debug("zerotier IP: %s" % ipaddr_priv)

        return ip_pub, ipaddr_priv
