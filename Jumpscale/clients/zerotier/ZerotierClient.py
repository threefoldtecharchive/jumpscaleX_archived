from Jumpscale import j

import zerotier
import copy
import time
import ipcalc

JSConfigClient = j.application.JSBaseConfigClass


class NetworkMember(j.application.JSBaseClass):
    """
    Represent a zerotier network member
    """

    def _init2(self, network, address, data):
        """
        Initialize new memeber
        """
        self.data = data
        self._network = network
        self.address = address
        self._private_ip = None

    def get_private_ip(self, timeout=120):
        """
        Gets the private ip address of the member node
        """
        if not self._private_ip:
            while not self.data["config"]["ipAssignments"] and timeout:
                timeout -= 2
                time.sleep(2)
                self._refresh()
            if not self.data["config"]["ipAssignments"]:
                raise j.exceptions.Value("Cannot get private ip address for zerotier member")
            self._private_ip = self.data["config"]["ipAssignments"][0]
        return self._private_ip

    @property
    def private_ip(self):
        return self.get_private_ip()

    @property
    def nodeid(self):
        return self.data["nodeId"]

    def nodeid_check(self, nodeids=[]):
        for item in nodeids:
            item = item.lower()
            if item == self.nodeid:
                return True
        return False

    def _refresh(self):
        """
        Refresh the data of the member by querying the lastest info from the server
        """
        member = self._network.member_get(address=self.address)
        self.data = member.data

    def _update_authorization(self, authorize=True, timeout=30):
        """
        Update authorization setting
        """
        # check if the network is private/public, it does not make sense to authorize on public nets
        if self._network.config["private"] is False:
            self._log_warning("Cannot authorize on public network.")
            return
        if self.data["config"]["authorized"] != authorize:
            data = copy.deepcopy(self.data)
            data["config"]["authorized"] = authorize
            self._network._client.network.updateMember(data=data, address=self.address, id=self._network.id)
            self._refresh()
            timeout_ = timeout
            while self.data["config"]["authorized"] != authorize and timeout_:
                self._refresh()
                time.sleep(2)
                timeout_ -= 2
            if self.data["config"]["authorized"] != authorize:
                self._log_warning(
                    "{}uthorization request sent but data is not updated after {} seconds".format(
                        "A" if authorize else "Dea", timeout
                    )
                )
        else:
            self._log_info(
                "Member {}/{} already {}".format(
                    self._network.id, self.address, "authorized" if authorize else "deauthorized"
                )
            )

    def authorize(self, timeout=30):
        """
        Authorize the member if not already authorized

        @param timeout: Timeout to wait until giving up updating the current state of the member
        """
        self._update_authorization(authorize=True, timeout=timeout)

    def deauthorize(self, timeout=30):
        """
        Deauthorize the member if already authorized

        @param timeout: Timeout to wait until giving up updating the current state of the member
        """
        self._update_authorization(authorize=False, timeout=timeout)

    def __str__(self):
        return "ZTMember <{}:{}>".format(self.address, self.data.get("name"))

    __repr__ = __str__


class ZeroTierNetwork:
    """
    Represent a zerotier network
    """

    def __init__(self, network_id, name, description, config, client):
        """
        Initialize new network
        """
        self.id = network_id
        self.name = name
        self.description = description
        self.config = config
        self.client = client
        self._client = client.client

    @property
    def mynode_member(self):
        """
        check which of my nodes exist in the network and if found return that member
        :return: 
        """
        for m in self.members_list():
            if m.nodeid_check(self.client.nodeids):
                return m
        return None

    def mynode_member_authorise(self):
        if self.mynode_member is None:
            raise j.exceptions.Base("could not find mynode")
        self.mynode_member.authorize()
        return self.mynode_member

    def members_list(self, raw=False):
        """
        Lists the members of the current network

        @param raw: If true, then members info will be returned as dict and not @NetworkMember objects
        """
        resp = self._client.network.listMembers(id=self.id)
        if resp.status_code != 200:
            msg = "Failed to list network memebers. Error: {}".format(resp.text)
            self._log_error(msg)
            raise j.exceptions.Base(msg)
        items = resp.json()

        return items if raw else self._create_netork_memebers_from_dict(items=items)

    def member_add(self, identity, name=None, description=None, private_ip=None, authorized=True):
        data = {"config": {"identity": identity, "authorized": authorized}, "name": name}
        if private_ip:
            data["config"]["ipAssignments"] = [private_ip]
        address = identity.split(":")[0]
        data = self._client.network.updateMember(data, address, self.id)
        data.raise_for_status()
        return NetworkMember(self, address, data.json())

    def member_get(self, address="", name="", public_ip="", private_ip=""):
        """
        Retrieves a member of the network that match the given filter
        @TODO: handle conflict between filters like providing two filters that conflict with each other
        """
        filters = [address, name, public_ip, private_ip]
        if not any(filters):
            msg = "At least one filter need to be specified"
            self._log_error(msg)
            raise j.exceptions.Base(msg)

        filters_map = dict(zip(["nodeId", "name", "physicalAddress", "private_ip"], filters))
        members = self.members_list(raw=True)
        result = None
        for member in members:
            for filter_name, filter_value in filters_map.items():
                if filter_name == "private_ip" and filter_value and filter_value in member["config"]["ipAssignments"]:
                    result = self._create_netork_memebers_from_dict(items=[member])[0]
                    break
                elif filter_name != "private_ip" and filter_value and filter_value == member[filter_name]:
                    result = self._create_netork_memebers_from_dict(items=[member])[0]
                    break

        if result is None:
            msg = "Cannot find a member that match the provided filters"
            self._log_error(msg)
            raise j.exceptions.Base(msg)
        return result

    def _create_netork_memebers_from_dict(self, items):
        """
        Convert network members info into @NetworkMember objects
        """
        result = []
        for item in items:
            result.append(NetworkMember(network=self, address=item["nodeId"], data=item))
        return result

    def member_delete(self, address):
        """
        Deletes a member from the network
        """
        resp = self._client.network.deleteMember(address=address, id=self.id)
        if resp.status_code != 200:
            msg = "Failed to delete member. Error: {}".format(resp.text)
            self._log_error(msg)
            raise j.exceptions.Base(msg)

        return True

    def list_routes(self):
        """list available routes on the network

        :raises j.exceptions.RuntimeError: if it fails to list routes of the network
        :return: routes available
        :rtype: list
        """

        resp = self._client.network.getNetwork(id=self.id)
        if resp.status_code != 200:
            msg = "Failed to retrieve network routes. Error: {}".format(resp.text)
            self._log_error(msg)
            raise j.exceptions.RuntimeError(msg)
        return resp.json()["config"]["routes"]

    def check_route(self, route):
        """check if route data already exists and returns necessary information

        :param route: contains the target and the host that will do the routing, eg: {'target': '10.111.1.0/24', 'via': '10.126.112.302'}
        :type route: dict
        :return: true if router with correct configuration exists, returns list of routes and the index of that route in the list
        :rtype: tuple
        """
        routes = self.list_routes()
        for idx, item in enumerate(routes):
            if item["target"] == route["target"] and item["via"] == route["via"]:
                return True, idx, routes
        return False, -1, routes

    def remove_route(self, route):
        """remove route with same data

        :param route: target and route data, eg: {'target': '10.111.1.0/24', 'via': '10.126.112.302'}
        :type route: dict
        :raises j.exceptions.RuntimeError: if removing it fails
        """
        exists, idx, routes = self.check_route(route)
        if exists:
            routes.pop(idx)
            config = {"config": {"routes": routes}}
            resp = self._client.network.updateNetwork(data=config, id=self.id)
            if resp.status_code != 200:
                msg = "Failed to remove route. Error: {}".format(resp.text)
                self._log_error(msg)
                raise j.exceptions.RuntimeError(msg)

    def add_route(self, route):
        """add a managed route to the network

        :param route: contains the target and the host that will do the routing, eg: {'target': '10.111.1.0/24', 'via': '10.126.112.302'}
        :type route: dict
        """
        exists, _, routes = self.check_route(route)
        if not exists:
            routes.append(route)
            config = {"config": {"routes": routes}}
            resp = self._client.network.updateNetwork(data=config, id=self.id)
            if resp.status_code != 200:
                msg = "Failed to add route. Error: {}".format(resp.text)
                self._log_error(msg)
                raise j.exceptions.RuntimeError(msg)

    def __str__(self):
        return "ZTNetwork <{}:{}>".format(self.id, self.name)

    __repr__ = __str__


class ZerotierClient(JSConfigClient):
    _SCHEMATEXT = """
    @url = jumpscale.zerotier.client
    name* = "" (S)
    instance = "main" (S)
    token_ = "" (S)
    networkid = "" (S)
    nodeids = "" (S)
    """

    def _init(self, **kwargs):

        if not self.token_:
            raise j.exceptions.Base("Missing auth token in config instance {}".format(self.instance))
        self.client = zerotier.client.Client()
        self.client.set_auth_header("Bearer " + self.token_)
        # self._client = ZerotierClientInteral(self.config.data['token_'])
        self._defaultnet = None

    @property
    def nodeids(self):
        if self.nodeids:
            return [item for item in self.nodeids.split(",") if item.strip() is not ""]
        return []

    def networks_list(self):
        """
        Lists all the networks for that belongs to the current instance
        """
        resp = self.client.network.listNetworks()
        if resp.status_code != 200:
            msg = "Failed to list networks. Error: {}".format(resp.text)
            self._log_error(msg)
            raise j.exceptions.Base(msg)
        return self._network_creates_from_dict(items=resp.json())

    def network_get(self, network_id=""):
        """
        Retrieves details information about a netowrk

        @param network_id: ID of the network, if not specified will check if it is in the config
        """
        if network_id is "":
            if self.networkid is "":
                raise j.exceptions.Input("could not find network id in config")
            network_id = self.networkid

        resp = self.client.network.getNetwork(id=network_id)
        if resp.status_code != 200:
            msg = "Failed to retrieve network. Error: {}".format(resp.text)
            self._log_error(msg)
            raise j.exceptions.Base(msg)
        return self._network_creates_from_dict(items=[resp.json()])[0]

    def _network_creates_from_dict(self, items):
        """
        Will create network objects from a dictionary format
        """
        result = []
        for item in items:
            result.append(
                ZeroTierNetwork(
                    network_id=item["id"],
                    name=item["config"]["name"],
                    description=item["description"],
                    config=item["config"],
                    client=self,
                )
            )
        return result

    def network_create(self, public, subnet=None, name=None, auto_assign=True, routes=None):
        """
        Create new network
        """

        if routes is None:
            routes = []
        subnet_info = None
        if subnet is not None:
            net = ipcalc.Network(subnet)
            routes.append({"target": subnet, "via": None})
            subnet_info = [{"ipRangeStart": net.host_first().dq, "ipRangeEnd": net.host_last().dq}]

        config = {"private": not public, "v4AssignMode": {"zt": auto_assign}, "routes": routes}
        if subnet_info:
            config.update({"ipAssignmentPools": subnet_info})

        if name:
            config.update({"name": name})

        data = {"config": config}
        resp = self.client.network.createNetwork(data=data)
        if resp.status_code != 200:
            msg = "Failed to create network. Error: {}".format(resp.text)
            self._log_error(msg)
            raise j.exceptions.Base(msg)
        return self._network_creates_from_dict([resp.json()])[0]

    def network_delete(self, network_id):
        """
        Delete netowrk

        @param network_id: ID of the network to delete
        """
        resp = self.client.network.deleteNetwork(id=network_id)
        if resp.status_code != 200:
            msg = "Failed to delete network. Error: {}".format(resp.text)
            self._log_error(msg)
            raise j.exceptions.Base(msg)
        return True

    def members_nonactive_delete(self):
        """
        walks over all members, the ones which are not active get deleted
        """
        raise j.exceptions.Base("not implemented")
        # TODO: *1 yves
