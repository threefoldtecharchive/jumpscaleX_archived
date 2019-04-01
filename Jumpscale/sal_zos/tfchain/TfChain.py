import json
import logging
import re
import signal

from .. import templates

logging.basicConfig(level=logging.INFO)



class TfChainDaemon:
    """
    TfChain Daemon
    """

    def __init__(self, name, container, data_dir='/mnt/data', rpc_addr='localhost:23112', api_addr='localhost:23110', network='standard'):
        self.name = name
        self.id = 'tfchaind.{}'.format(self.name)
        self.container = container
        self.data_dir = data_dir
        self.rpc_addr = rpc_addr
        self.api_addr = api_addr
        self.network = network

    def start(self, timeout=150):
        """
        Start tfchain daemon
        :param timeout: time in seconds to wait for the tfchain daemon to start
        """
        if self.is_running():
            return

        cmd_line = '/tfchaind \
            --rpc-addr {rpc_addr} \
            --api-addr {api_addr} \
            --persistent-directory {data_dir} \
            --network {network} \
            '.format(rpc_addr=self.rpc_addr,
                     api_addr=self.api_addr,
                     data_dir=self.data_dir,
                     network=self.network)

        cmd = self.container.client.system(cmd_line, id=self.id)

        port = int(self.api_addr.split(":")[1])
        while not self.container.is_port_listening(port, timeout):
            if not self.is_running():
                result = cmd.get()
                raise RuntimeError("Could not start tfchaind.\nstdout: %s\nstderr: %s" % (
                    result.stdout, result.stderr))

    def stop(self, timeout=30):
        """
        Stop the tfchain daemon
        :param timeout: time in seconds to wait for the daemon to stop
        """
        if not self.is_running():
            return

        j.tools.logger._log_debug('stop %s', self)
        self.container.stop_job(self.id, signal=signal.SIGINT, timeout=timeout)

    def is_running(self):
        return self.container.is_job_running(self.id)


class TfChainExplorer:
    """
    TfChain Explorer Daemon
    """

    def __init__(self, name, container, domain, data_dir='/mnt/data', rpc_addr='localhost:23112', api_addr='localhost:23110', network='standard'):
        self.name = name
        self.domain = domain
        self.tf_ps_id = 'tfchaind.{}'.format(self.name)
        self.caddy_ps_id = 'caddy.{}'.format(self.name)
        self.container = container
        self.data_dir = data_dir
        self.rpc_addr = rpc_addr
        self.api_addr = api_addr
        self.network = network

    def start(self, timeout=30):
        """
        Start tfchain explorer daemon and caddy as reverse proxy
        :param timeout: time in seconds to wait for the both process to start
        """
        self._start_tf_deamon(timeout=timeout)
        self._start_caddy(timeout=timeout)

    def _start_tf_deamon(self, timeout=150):
        """
        Start tfchain daemon
        :param timeout: time in seconds to wait for the tfchain daemon to start
        """
        if self.is_running():
            return

        cmd_line = '/tfchaind \
            --rpc-addr {rpc_addr} \
            --api-addr {api_addr} \
            --persistent-directory {data_dir} \
            --modules gcte \
            --network {network} \
            '.format(rpc_addr=self.rpc_addr,
                     api_addr=self.api_addr,
                     data_dir=self.data_dir,
                     network=self.network)

        cmd = self.container.client.system(cmd_line, id=self.tf_ps_id)

        port = int(self.api_addr.split(":")[1])
        while not self.container.is_port_listening(port, timeout):
            if not self.is_running():
                result = cmd.get()
                raise RuntimeError("Could not start tfchaind.\nstdout: %s\nstderr: %s" % (result.stdout, result.stderr))

    def _start_caddy(self, timeout=150):
        """
        Start caddy
        :param timeout: time in seconds to wait for caddy to start
        """
        if self.is_running():
            return

        j.tools.logger._log_info('Creating caddy config for %s' % self.name)
        config_location = '/mnt/explorer/explorer/caddy/Caddyfile'
        config = templates.render('tf_explorer_caddy.conf', domain=self.domain)
        self.container.upload_content(config_location, config)

        cmd_line = '/mnt/explorer/bin/caddy -conf %s' % config_location
        cmd = self.container.client.system(cmd_line, id=self.caddy_ps_id)

        port = 443
        while not self.container.is_port_listening(port, timeout):
            if not self.is_running():
                result = cmd.get()
                raise RuntimeError("Could not start caddy.\nstdout: %s\nstderr: %s" % (result.stdout, result.stderr))

    def stop(self, timeout=30):
        """
        Stop the tfchain daemon
        :param timeout: time in seconds to wait for the daemon to stop.
        """
        self._stop_caddy_daemon(timeout)
        self._stop_tf_daemon(timeout)

    def _stop_tf_daemon(self, timeout=30):
        if not self._is_tf_running():
            return

        j.tools.logger._log_debug('stop tf daemon %s', self)
        self.container.stop_job(self.tf_ps_id, signal=signal.SIGINT, timeout=timeout)

    def _stop_caddy_daemon(self, timeout=30):
        if not self._is_caddy_running():
            return

        j.tools.logger._log_debug('stop caddy %s', self)
        self.container.stop_job(self.caddy_ps_id, signal=signal.SIGINT, timeout=timeout)

    def is_running(self):
        return self._is_tf_running() and self._is_caddy_running()

    def _is_tf_running(self):
        return self.container.is_job_running(self.tf_ps_id)

    def _is_caddy_running(self):
        return self.container.is_job_running(self.caddy_ps_id)

    def consensus_stat(self):
        return consensus_stat(self.container, self.api_addr)

    def gateway_stat(self):
        return gateway_stat(self.container, self.api_addr)


class TfChainClient:
    """
    TfChain Client
    """

    def __init__(self, name, container, wallet_passphrase, addr='localhost:23110'):
        self.name = name
        self.container = container
        self.addr = addr
        self._recovery_seed = None
        self._wallet_addresses = None
        self._wallet_password = wallet_passphrase

    @property
    def recovery_seed(self):
        return self._recovery_seed

    @property
    def wallet_password(self):
        return self._wallet_password

    def create_new_wallet_address(self):
        """ Create a new wallet address """

        cmd = 'curl -A "Rivine-Agent" "{}/wallet/address"'.format(self.addr)
        result = self.container.client.system(cmd).get()

        error_check(result, message='"Could not create a wallet address', parse=True)

        new_wallet_address = json.loads(result.stdout)

        return new_wallet_address['address']

    @property
    def wallet_addresses(self):
        """ Get all wallet addresses """

        cmd = 'curl -A "Rivine-Agent" "{}/wallet/addresses"'.format(self.addr)
        result = self.container.client.system(cmd).get()
        error_check(result, message='Could not get wallet addresses', parse=True)

        self._wallet_addresses = json.loads(result.stdout)['addresses']
        return self._wallet_addresses

    def wallet_init(self):
        """ Initialize wallet """

        cmd = 'curl -A "Rivine-Agent" --data "passphrase={}" "{}/wallet/init"'.format(self.wallet_password, self.addr)
        result = self.container.client.system(cmd).get()
        error_check(result, message='Could not initialize wallet', parse=True)
        stdout = json.loads(result.stdout)
        self._recovery_seed = stdout['primaryseed']

    def wallet_unlock(self):
        """ Unlock wallet """

        cmd = 'curl -A "Rivine-Agent" --data "passphrase={}" "{}/wallet/unlock"'.format(self.wallet_password, self.addr)
        result = self.container.client.system(cmd, stdin=self.wallet_password).get()
        error_check(result, message="Could not unlock wallet", parse=True)

    def wallet_lock(self):
        """ Lock wallet """

        cmd = 'curl -A "Rivine-Agent" --data " " "{}/wallet/lock"'.format(self.addr)
        result = self.container.client.system(cmd, stdin=self.wallet_password).get()
        error_check(result, message="Could not lock wallet", parse=True)

    def wallet_amount(self):
        """
        return the amount of token and block stake in the wallet
        """
        return self._get_wallet_info()

    def discover_local_peers(self, link=None, port='23112'):
        """ List local peers in subnet @addr with open port @port

            @link: network interface name
            @port: port for scanning
        """
        ipn = self.container.default_ip(link)
        subnet = "%s/%s" % (ipn.network, ipn.prefixlen)
        cmd = 'nmap {} -p {}'.format(subnet, port)

        scan = self.container.client.system(cmd, stdin=self.wallet_password)
        while True:
            try:
                result = scan.get()
                break
            except TimeoutError:
                continue

        error_check(result, "Could not list peers")

        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', result.stdout)
        states = re.findall("tcp \w+", result.stdout)
        all_peers = dict(zip(ips, states))
        active_peers = []
        for ip in all_peers:
            # get peers with open port, exclude own address
            if all_peers[ip] == 'tcp open' and ip != str(ipn.ip):
                active_peers.append("{}:{}".format(ip, port))

        return active_peers

    def add_peer(self, addr, port='23112'):
        cmd = 'curl -A "Rivine-Agent" --data " " "{}/gateway/connect/{}:{}"'.format(self.addr, addr, port)
        result = self.container.client.system(cmd, stdin=self.wallet_password).get()
        error_check(result, "Could not connect to a peer")

    def _get_wallet_info(self):
        """ Get wallet info """

        cmd = 'curl -A "Rivine-Agent" "{}/wallet"'.format(self.addr)
        result = self.container.client.system(cmd).get()
        error_check(result, message="Could not get wallet info")

        return json.loads(result.stdout)

    def wallet_status(self, wallet_info=None):
        """
        Returns the wallet status [locked/unlocked]

        parameters:
        - wallet_info: Optional parameter containing the result of the _get_wallet_info method

        return the status of the wallet [locked/unlocked]
        """

        wallet_info = wallet_info or self._get_wallet_info()
        return "unlocked" if wallet_info["unlocked"] else "locked"

    def consensus_stat(self):
        return consensus_stat(self.container, self.addr)

    def gateway_stat(self):
        return gateway_stat(self.container, self.addr)

    def get_report(self):
        """ Get wallet report """

        result = dict()
        wallet_info = self._get_wallet_info()
        wallet_status = self.wallet_status(wallet_info=wallet_info)
        result["wallet_status"] = wallet_status

        if wallet_status == "unlocked":
            result["active_blockstakes"] = int(wallet_info['blockstakebalance'])
            result["confirmed_balance"] = int(wallet_info['confirmedcoinbalance'])
            result["address"] = "not supported by tfchaind yet"
        else:
            result["active_blockstakes"] = -1
            result["confirmed_balance"] = -1
            result["address"] = "not supported by tfchaind yet"

        consensus = self.consensus_stat()
        result["block_height"] = consensus["height"]
        gateways = self.gateway_stat()
        result["connected_peers"] = len(gateways["peers"])
        return result


def consensus_stat(container, addr):
    """ Get consensus info """

    cmd = 'curl -A "Rivine-Agent" "{}/consensus"'.format(addr)
    result = container.client.system(cmd).get()
    error_check(result, "Could not get consensus info")

    return json.loads(result.stdout)


def gateway_stat(container, addr):
    """ Get gateway info """

    cmd = 'curl -A "Rivine-Agent" "{}/gateway"'.format(addr)
    result = container.client.system(cmd).get()
    error_check(result, "Could not get gateway info")

    return json.loads(result.stdout)


def error_check(result, message='', parse=False):
    """ Raise error on errorred curl call

        @result: object returned by curl
        @message: arbitrary error message
        @parse: when set to True tries to parse result.stdout as json
    """
    if result.state != 'SUCCESS':
        # check if curl was executed correctly
        err = '{}: {} \n {}'.format(message, result.stderr, result.data)
        raise RuntimeError(err)

    if not parse:
        return

    # add errorcheck for field 'message' if output is json
    if result.stdout:
        try:
            # extract error message if result.stdout is in json format
            stdout_error = json.loads(result.stdout).get('message')
        except json.JSONDecodeError:
            stdout_error = 'failed parsing JSON: "%s"' % result.stdout

        if stdout_error:
            # check tfclient error
            err = '{}: {}'.format(message, stdout_error)
            raise RuntimeError(err)
