import hashlib
import re
import time
import urllib

import netaddr
from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass


def apply_changes(sshclient, network=False):
    sshclient.execute('uci commit')
    if network:
        try:
            sshclient.execute('/etc/init.d/network restart && sleep 3 && /etc/init.d/zerotier restart',
                              timeout=12)  # added sleep to prevent race condition
        except j.exceptions.SSHTimeout:
            pass
        code, _, _ = j.sal.process.execute('ping -c 2 {}'.format(sshclient.addr), die=False)
        timeout_limit = time.time() + 70
        while time.time() < timeout_limit:
            if code == 0:
                break
            time.sleep(5)
            code, _, _ = j.sal.process.execute('ping -c 2 {}'.format(sshclient.addr), die=False)
        else:
            raise j.exceptions.RuntimeError('Lost connection to the router')
    else:
        sshclient.execute('/etc/init.d/dnsmasq restart')


class zero_bootClient(JSConfigClient):
    """zero_boot client
    using racktivity
    """
    _SCHEMATEXT = """
    @url =jumpscale.zeroboot.client
    name* = "" (S)
    sshclient_instance = "" (S)
    zerotier_instance = "" (S)
    network_id = "" (S)
    """

    def _init(self):
        self.sshclient = j.clients.ssh.get(
            instance=self.sshclient_instance)
        self.networks = Networks(self.sshclient)
        zerotier_instance = self.zerotier_instance
        if zerotier_instance:
            ztier = j.clients.zerotier.get(instance=zerotier_instance)
            network = self.networks.get()
            cidr = str(netaddr.IPNetwork(network.subnet).cidr)
            route = {'target': cidr, 'via': self.sshclient.addr}
            znetwork = ztier.network_get(self.network_id)
            znetwork.add_route(route)

    def power_info_get(self, rack_client, module_id=None):
        """gets power info for opened ports
        :param rack_client: racktivity client
        :param module_id: power module id if racktivity model has multiple power modules ex: P1, won't be used if None
        :type module_id: str
        """
        return rack_client.power.getPower(moduleID=module_id)

    def port_power_on(self, port_number, rack_client, module_id=None):
        """turn port on
        :param rack_client: racktivity client
        :param module_id: power module id if racktivity model has multiple power modules ex: P1, won't be used if None
        :type module_id: str
        """
        return rack_client.power.setPortState(moduleID=module_id, value=1, portnumber=port_number)

    def port_power_off(self, port_number, rack_client, module_id=None):
        """turn port off
        :param rack_client: racktivity client
        :param module_id: power module id if racktivity model has multiple power modules ex: P1, won't be used if None
        :type module_id: str
        """

        return rack_client.power.setPortState(moduleID=module_id, value=0, portnumber=port_number)

    def port_power_cycle(self, port_numbers, rack_client, module_id=None):
        """
        Power off, wait 5 sec then turn on again.
        :param port_numbers: ports to power cycle on
        :type port_numbers: list
        :param rack_client: racktivity client
        :param module_id: power module id if racktivity model has multiple power modules ex: P1, won't be used if None
        :type module_id: str
        """
        for port_number in port_numbers:
            self.port_power_off(port_number, rack_client, module_id)
            time.sleep(5)
            self.port_power_on(port_number, rack_client, module_id)

    def port_info(self, port_number, rack_client, module_id=None):
        """get port info
        :param rack_client: racktivity client
        :param module_id: power module id if racktivity model has multiple power modules ex: P1, won't be used if None
        :type module_id: str
        """
        return rack_client.power.getStatePortCur(moduleID=module_id, portnumber=port_number)


class Network:
    def __init__(self, subnet, sshclient, networkname="lan", leasetime="60m"):
        self.subnet = subnet
        self.sshclient = sshclient
        self.networkname = networkname

        # get leasetime if present, else set provided
        self.leasetime = self._get_leasetime() or leasetime
        self.hosts = Hosts(self.sshclient, self.subnet, self.leasetime, networkname=networkname)

    def _get_leasetime(self):
        _, out, _ = self.sshclient.execute("uci show dhcp.{name}.leasetime".format(name=self.networkname), die=False)
        if not out or not "=" in out:
            return None
        out = out.strip()
        out = out.split('=')[1]
        return out.strip("\'")

    def configure_lease_time(self, leasetime):
        """configure expiration time for all the network's leases

        :param leasetime: follows the format h for hours m for minutes ex: 5m
        :type leasetime: str
        """
        self.sshclient.execute("uci set dhcp.{name}.leasetime='{leasetime}'".format(
            name=self.networkname, leasetime=leasetime))
        apply_changes(self.sshclient)
        self.leasetime = leasetime

    def add(self):
        raise NotImplementedError()

    def configure(self, subnet):
        """
        Configure the subnet of the network
        """
        net = netaddr.IPNetwork(subnet)
        self.sshclient.execute("uci set network.{name}.ipaddr='{ip}'".format(name=self.networkname, ip=str(net.ip)))
        self.sshclient.execute("uci set network.{name}.netmask='{mask}'".format(
            name=self.networkname, mask=str(net.netmask)))
        apply_changes(self.sshclient, network=True)
        self.subnet = subnet
        for host in self.hosts.list():
            self.hosts.remove(host)
        self.hosts = Hosts(self.sshclient, self.subnet, self.leasetime, networkname=self.networkname)

    def remove(self):
        raise NotImplementedError()


class Networks:
    def __init__(self, sshclient):
        self._networks = {}
        self.sshclient = sshclient

        self._populate()

    def _populate(self):
        _, output, _ = self.sshclient.execute('uci show network')
        output = output.splitlines()
        data = dict()
        for line in output:
            key, value = line.split('=')
            data[key] = value

        for key, value in data.items():
            if key.endswith('.ipaddr'):
                ip = value.strip()
                ip = ip.strip("\'")
                netmask = data[key.replace('.ipaddr', '.netmask')].strip()
                netmask = netmask.strip("\'")

                subnet = str(
                    netaddr.IPNetwork("{ip}/{net}".format(ip=ip, net=netmask))
                )
                networkname = self._get_networkname(key)
                self._networks[subnet] = Network(subnet, self.sshclient, networkname=networkname)

    def _get_networkname(self, keyname):
        """Returns network name from uci network keys

        :param keyname: key of the uci show networks command (expected to end with '.ipaddr' and start with 'network.')
        :type keyname: str
        :return: name of the network contained in the key
        :rtype: str
        """
        end_key = ".ipaddr"
        start_key = "network."

        if not keyname.endswith(end_key):
            raise ValueError("keyname did not end with {search_key}, get {value}".format(
                search_key=end_key, value=keyname))

        if not keyname.startswith(start_key):
            raise ValueError("keyname did not start with {search_key}, get {value}".format(
                search_key=start_key, value=keyname))

        return keyname[len(start_key):-len(end_key)]

    def add(self, subnet, list_of_dns):
        raise NotImplementedError()

    def list(self):
        """list all subnets

        :return: list of subnets
        :rtype: list
        """
        return list(self._networks.keys())

    def get(self, ip=None):
        """get network object from the host ip

        :param ip: ip required, defaults to None in that case will get first in the list
        :type ip: str
        :raises KeyError: if ip doesn't exist in available subnets
        :return: network object
        :rtype: object
        """
        if not ip:
            ip = self.list()[0].split('/')[0]
        for subnet in self._networks:
            if netaddr.IPAddress(ip) in netaddr.IPNetwork(subnet):
                return self._networks[subnet]
        else:
            raise KeyError("Host with specified IP: %s doesn't exist" % ip)

    def remove(self, subnet):
        raise NotImplementedError()

    def __repr__(self):
        return str(self.list())


class Host:
    def __init__(self, mac, address, hostname, sshclient, index):
        self.mac = mac
        self.address = address
        self.hostname = hostname
        self.sshclient = sshclient
        self.index = index

    def configure_ipxe_boot(self, lkrn_url, tftp_root='/opt/storage'):
        """[summary]

        :param lkrn_url: url that points to a LKRN file to boot from that includes boot parameters. E.g.: https://bootstrap.grid.tf/krn/master/0/
        :type boot_url: str
        :param tftp_root: tftp root location where pxe config are stored, defaults to '/opt/storage'
        :param tftp_root: str, optional
        """
        # url parse boot parameters
        lkrn_url = lkrn_url.replace(" ", "%20")

        lkrn_hash = hashlib.md5(lkrn_url.encode('utf8')).hexdigest()
        file_name = '01-{}'.format(str(netaddr.EUI(self.mac)).lower())
        executor = j.tools.executor.ssh_get(self.sshclient)
        pxe_config_root = '{root}/pxelinux.cfg'.format(root=tftp_root)
        pxe_config_file = '{root}/{file}'.format(root=pxe_config_root, file=file_name)
        lkrn_file = '{root}/{file}'.format(root=pxe_config_root, file=lkrn_hash + ".lkrn")
        if not self.sshclient.prefab.core.exists(lkrn_file):
            # download lkrn file
            executor.execute("mkdir -p {root}".format(root=pxe_config_root))
            executor.execute("wget -O {target} {source}".format(target=lkrn_file, source=lkrn_url))
        pxe_config_data = (
            "default 1\n"
            "timeout 100\n"
            "prompt 1\n"
            "ipappend 2\n\n"
            "label 1\n"
            "\tKERNEL {}\n".format(lkrn_file))

        executor.file_write(pxe_config_file, pxe_config_data)

    def _hostname_set(self, option, value):
        self.sshclient.execute("uci set dhcp.@host[{idx}].{opt}='{val}'".format(idx=self.index, opt=option, val=value))

    def _register(self):
        self.sshclient.execute('uci add dhcp host')
        self._hostname_set('ip', self.address)
        self._hostname_set('mac', self.mac)
        self._hostname_set('name', self.hostname)
        apply_changes(self.sshclient)

    def _unregister(self):
        self.sshclient.execute('uci delete dhcp.@host[{}]'.format(self.index))
        apply_changes(self.sshclient)


class Hosts:
    def __init__(self, sshclient, subnet, leasetime, networkname="lan"):
        self._hosts = {}
        self.sshclient = sshclient
        self.subnet = subnet
        self._last_index = -1
        self._populate()
        self.leasetime = leasetime
        self.networkname = networkname

    def _hosts_chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def _populate(self):
        """
        example hosts_data:
        [('0', 'ip', "'192.168.1.2'"),
        ('0', 'mac', "'00:11:22:33:44:55'"),
        ('0', 'name', "'mypc'"),
        ('1', 'ip', "'192.168.1.3'"),
        ('1', 'mac', "'00:11:22:33:44:55'"),
        ('1', 'name', "'myhost'")]
        """

        _, out, _ = self.sshclient.execute('uci show dhcp')
        hosts_data = re.findall("dhcp.@host\[(\d+)\]\.(ip|mac|name)=(.+)", out)
        if hosts_data:
            self._last_index = int(hosts_data[-1][0])
            host_data_json = {}
            for host_data in self._hosts_chunks(hosts_data, 3):
                index = host_data[0][0]
                for data in host_data:
                    if 'mac' in data:
                        host_data_json['mac'] = data[2].replace("'", "")
                    elif 'name' in data:
                        host_data_json['hostname'] = data[2].replace("'", "")
                    elif 'ip' in data:
                        host_data_json['address'] = data[2].replace("'", "")

                if netaddr.IPAddress(host_data_json['address']) in netaddr.IPNetwork(self.subnet):
                    host_data_json['sshclient'] = self.sshclient
                    host_data_json['index'] = index
                    self._hosts[host_data_json['hostname']] = Host(**host_data_json)
        else:
            self._last_index = -1

    def add(self, mac, address, hostname):
        """Adds a static lease to machine with the specified mac address

        :param mac: required mac address
        :type mac: str
        :param address: static ip to give to machine
        :type address: str
        :param hostname: hostname
        :type hostname: str
        :raises RuntimeError: if specified address not in network range
        :raises RuntimeError: if host name already exists
        :raises RuntimeError: if mac address and/or ip are already registered
        :return: object representing the host
        :rtype: object
        """
        self._populate()  # make sure dhcp list is up to date (e.g. manually/webinterface)
        if netaddr.IPAddress(address) not in netaddr.IPNetwork(self.subnet):
            raise RuntimeError("specified address: {addr} not in network: {net}".format(addr=address, net=self.subnet))
        if hostname in self._hosts:
            raise RuntimeError("Host with hostname: %s already registered to the network" % hostname)
        for host in self._hosts.values():
            if host.mac == mac or host.address == address:
                raise RuntimeError(
                    "Host with specified mac: {mac} and/or address: {addr} already registered".format(mac=mac, addr=address))
        self._last_index += 1
        host = Host(mac, address, hostname, self.sshclient, self._last_index)
        self.sshclient.execute("uci set dhcp.{name}.dynamicdhcp='0'".format(name=self.networkname))
        self.sshclient.execute("uci set dhcp.{name}.leasetime='{leasetime}'".format(
            name=self.networkname, leasetime=self.leasetime))
        host._register()
        self._hosts[hostname] = host
        return host

    def list(self):
        """list all hostnames

        :return: list of hostnames
        :rtype: list
        """

        return list(self._hosts.keys())

    def get(self, hostname):
        """get host object from hostname

        :param hostname: hostname required
        :type hostname: str
        :raises KeyError: if hostname doesn't exist in available hostnames
        :return: host object
        :rtype: object
        """

        if hostname not in self._hosts:
            raise KeyError("Host: %s doesn't exist" % hostname)
        return self._hosts[hostname]

    def remove(self, hostname):
        """removes static lease

        :param hostname: hostname specified in the lease
        :type hostname: str
        """

        host = self.get(hostname)
        host._unregister()
        self._hosts = {}
        self._populate()  # To fetch correct indexes

    def __repr__(self):
        return str(self.list())
