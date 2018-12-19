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

JSConfigFactory = j.application.JSFactoryBaseClass


from .ZerotierClient import ZerotierClient


JSBASE = j.application.JSBaseClass



class ZerotierFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.zerotier"
        self.__imports__ = "zerotier"
        self.connections = {}
        JSConfigFactory.__init__(self, ZerotierClient)

    def configure(self,instance,token,nodeids="",networkid_default="",interactive=False):
        """
        @PARAM networkid is optional
        @PARAM nodeids is optional, comma separated list of nodeids, used to define your connection (you're a member of a network)
        """
        data={}
        data["token_"]=token
        data["networkid"]=networkid_default
        return self.get(instance=instance,data=data,interactive=interactive)

    def test(self):
        """
        j.clients.zerotier.test()
        """
        import time

        # create a test client using a test token
        TOKEN = 'txBz8dHAyBy6tuPqhywhr9cR6ceacwWg'

        zt_client = j.clients.zerotier.get(instance='testclient', data={'token_': TOKEN})

        # make sure zerotier is installed and started
        # j.tools.prefab.local.network.zerotier.build()

        # start the daemon
        # j.tools.prefab.local.network.zerotier.start()

        # create a new test network
        network = zt_client.network_create(public=True, name='mytestnet', subnet='10.0.0.0/24')

        # try to make the the current machine join the new network
        j.tools.prefab.local.network.zerotier.network_join(network_id=network.id)
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
