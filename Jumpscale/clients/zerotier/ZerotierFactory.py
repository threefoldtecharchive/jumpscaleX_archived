from .ZerotierClient import ZerotierClient

"""
zc = j.clients.zerotier.get(name="geert", data={'token_':"jkhljhbljb"})
mynetworks = zc.networks_list()-> [ZerotierNetwork]
mynetwork = zc.network_get(networkid='khgfghvhgv') -> ZerotierNetwork
zc.network_create(public=True, subnet="10.0.0.0/24", auto_assign=True, routes=[])
mymembers = mynetwork.members_list() -> [ZerotierNetworkMember]
mymember = mynetwork.member_get(address='hfivivk' || name='geert' || public_ip='...' || private_ip='...')
mymember.authorize()
mymember.deauthorize()
"""

import time
from Jumpscale import j

JSConfigs = j.application.JSBaseConfigsClass


JSBASE = j.application.JSFactoryConfigsBaseClass


class ZerotierFactory(JSConfigs):
    __jslocation__ = "j.clients.zerotier"
    _CHILDCLASS = ZerotierClient

    def _init(self, **kwargs):
        self.__imports__ = "zerotier"
        self.connections = {}
        self.config_path = None

    def client_start(self):
        # make sure zerotier is installed and started
        j.builders.network.zerotier.build()

        # start the daemon
        j.builders.network.zerotier.start()

    def _cmd_get(self, cmd, pre=None, post=None):

        CLI = j.builders.network.zerotier._replace("{CLI}")
        c = CLI + " "
        if self.config_path:
            c += "-D%s " % self.config_path
        if pre:
            c += "%s " % pre
        c += cmd
        if post:
            c += " %s " % post
        self._log_debug(cmd)
        return c

    def _cmd(self, cmd, pre=None, post=None):
        cmd1 = self._cmd_get(cmd, pre, post)
        rc, out, _ = j.sal.process.execute(cmd1, die=True, showout=False)
        return out

    def network_join(self, network_id, zerotier_client=None):
        """
        join the netowrk identied by network_id and authorize it into the network if a zerotier_client would be given
        """
        cmd = self._cmd_get("join", post=network_id)
        rc, out, err = j.sal.process.execute(cmd, die=False)
        if rc != 0 or out.find("OK") == -1:
            raise j.exceptions.RuntimeError("error while joinning network: \n{}".format(err))

        ok = False
        while not ok:
            networks_joined = self.networks_joined()
            for network in networks_joined:
                if network["network_id"] == network_id and network["status"] == "OK":
                    ok = True
            if not ok:
                time.sleep(0.2)
                self._log_debug("wait join: %s" % network_id)

        if zerotier_client:
            machine_address = self.get_zerotier_machine_address()
            zerotier_client.client.network.updateMember(
                address=machine_address, id=network_id, data={"config": {"authorized": True}}
            )

    def network_leave(self, network_id):
        """
        leave the network identied by network_id
        """
        cmd = self._cmd_get("leave", post=network_id)
        rc, out, _ = j.sal.process.execute(cmd, die=False)
        if rc != 0 or out.find("OK") == -1:
            error_msg = "error while joinning network: "
            if out.find("404") != -1:
                error_msg += "not part of the network {}".format(network_id)
            else:
                error_msg += out
            raise j.exceptions.RuntimeError(error_msg)

    def networks_joined(self):
        """
        list all joined networks.
        return a list of dict
        network = {
            'network_id': ,
            'name': ,
            'mac': ,
            'status': ,
            'type': ,
            'dev': ,
            'ips': ,
        }
        """
        out = self._cmd("listnetworks", pre="-j")
        lines = j.data.serializers.json.loads(out)
        if len(lines) < 1:
            return {}

        networks = []
        for line in lines:
            network = {
                "network_id": line["id"],
                "name": line["name"],
                "mac": line["mac"],
                "status": line["status"],
                "type": line["type"],
                "dev": line["portDeviceName"],
                "ips": line["assignedAddresses"],
            }
            networks.append(network)

        return networks

    def get_network_interface_name(self, network_id):
        """
        Get the zerotier network interface device name.
        """
        for net in self.networks_list():
            if net["network_id"] == network_id:
                return net["dev"]
        raise j.exceptions.NotFound("Network connection with id %s was not found!" % network_id)

    def get_zerotier_machine_address(self):
        """
        Get the zerotier machine address.
        """
        out = self._cmd("info")
        return out.split()[2]

    def peers_list(self):
        """
        list connected peers.
        return a list of dict
        network = {
            'ztaddr': ,
            'paths': ,
            'latency': ,
            'version': ,
            'role': ,
        }
        """
        out = self._cmd("listpeers")
        lines = out.splitlines()
        if len(lines) < 2:
            return {}
        peers = []
        for line in out.splitlines()[1:]:
            ss = line.split(" ")
            peer = {"ztaddr": ss[2], "paths": ss[3], "latency": ss[4], "version": ss[5], "role": ss[6]}
            peers.append(peer)
        return peers

    def network_name_get(self, network_id):
        """"gets a network name with ip

        Arguments:
            network_id {string} -- network id to look for

        Raises:
            RuntimeError -- if there is no networks with the given id

        Returns:
            string -- network name
        """

        networks = self.networks_list()
        for network in networks:
            if network["network_id"] == network_id:
                return network["name"]
        raise j.exceptions.Base(
            "no networks found with id {}, make sure that you properly joined this network".format(network_id)
        )

    def test(self):
        """
        kosmos 'j.clients.zerotier.test()'
        """

        # self.client_start()

        import time

        # create a test client using a test token
        TOKEN = "txBz8dHAyBy6tuPqhywhr9cR6ceacwWg"

        zt_client = j.clients.zerotier.get(name="testclient", token_=TOKEN)

        # create a new test network
        network = zt_client.network_create(public=True, name="mytestnet", subnet="10.0.0.0/24")

        # try to make the the current machine join the new network
        self.network_join(network_id=network.id)

        # lets list the members then
        members = network.members_list()

        assert len(members) == 1, "Unexpected number of members. Expected 1 found {}".format(len(members))

        # lets try to authorize the member, shouldnt affect anything since it a public netowrk
        member = members[0]
        member.authorize()
        assert member.data["config"]["authorized"] == True, "Members of public networks should be authorized"

        # now lets unauthorize, shouldnt have any effect
        member.deauthorize()
        assert member.data["config"]["authorized"] == True, "Members of public networks should be authorized"

        # lets list all the networks for our current user
        networks = zt_client.networks_list()

        # lets get the network object using the network id we just created
        network = zt_client.network_get(network_id=network.id)
        assert network.name == "mytestnet"

        # now lets delete the testnetwork we created
        zt_client.network_delete(network_id=network.id)

        self._log_info("TEST OK")
