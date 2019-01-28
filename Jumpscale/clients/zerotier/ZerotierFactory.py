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

from Jumpscale import j

JSConfigs = j.application.JSBaseConfigsClass


JSBASE = j.application.JSFactoryBaseClass


class ZerotierFactory(JSConfigs):
    __jslocation__ = "j.clients.zerotier"
    _CHILDCLASS = ZerotierClient

    def _init(self):
        self.__imports__ = "zerotier"
        self.connections = {}


    def test(self):
        """
        j.clients.zerotier.test()
        """
        import time

        # create a test client using a test token
        TOKEN = 'txBz8dHAyBy6tuPqhywhr9cR6ceacwWg'

        zt_client = j.clients.zerotier.get(name='testclient', token_=TOKEN})

        # make sure zerotier is installed and started
        # j.builder.network.zerotier.build()

        # start the daemon
        # j.builder.network.zerotier.start()

        # create a new test network
        network = zt_client.network_create(public=True, name='mytestnet', subnet='10.0.0.0/24')

        # try to make the the current machine join the new network
        j.builder.network.zerotier.network_join(network_id=network.id)
        time.sleep(20)

        # lets list the members then
        members = network.members_list()

        assert len(members) == 1, "Unexpected number of members. Expected 1 found {}".format(len(members))

        # lets try to authorize the member, shouldnt affect anything since it a public netowrk
        member = members[0]
        member.authorize()
        assert member.data['config']['authorized'] == True, "Members of public networks should be authorized"

        # now lets unauthorize, shouldnt have any effect
        member.deauthorize()
        assert member.data['config']['authorized'] == True, "Members of public networks should be authorized"

        # lets list all the networks for our current user
        networks = zt_client.networks_list()

        # lets get the network object using the network id we just created
        network = zt_client.network_get(network_id=network.id)
        assert network.name == 'mytestnet'

        # now lets delete the testnetwork we created
        zt_client.network_delete(network_id=network.id)
