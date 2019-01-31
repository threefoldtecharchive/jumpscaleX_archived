"""
Tfchain Client
"""

from Jumpscale import j

from .types.errors import ExplorerNoContent, ExplorerCallError
from Jumpscale.clients.http.HttpClient import HTTPError

# TODO: support a shuffle feature in the idGenerator module of JS
#       or make sure we can do it using the already available generateRandomInt functionality
import random

class TFChainExplorerClient(j.application.JSBaseClass):
    """
    Client to get data from a tfchain explorer.
    """

    def get(self, addresses, endpoint):
        """
        get data from an explorer at the endpoint from any explorer that is available
        on one of the given urls. The list of urls is traversed in random order until
        an explorer returns with a 200 OK status.

        @param urls: the list of urls of all available explorers
        @param endpoint: the endpoint to get the data from
        """
        assert len(addresses) > 0
        indices = list(range(len(addresses)))
        random.shuffle(indices)
        for idx in indices:
            try:
                address = addresses[idx]
                assert isinstance(address, str)
                # this is required in order to be able to talk directly a daemon
                headers = {'User-Agent': 'Rivine-Agent'}
                # do the request and check the response
                resp = j.clients.http.get(url=address+endpoint, headers=headers)
                if resp.getcode() == 200:
                    return resp.readline()
                if resp.getcode() == 204:
                    raise ExplorerNoContent("nothing could be found at endpoint {}".format(endpoint))
                raise ExplorerCallError("call to {} resulted in error {}".format(endpoint, resp.getcode()))
            except HTTPError as e:
                if e.status_code == 400 and b'unrecognized hash' in e.msg:
                    raise ExplorerNoContent("nothing could be found at endpoint {}".format(endpoint))
                if e.status_code:
                    raise ExplorerCallError("call to {} resulted in an error {}: {}".format(endpoint, e.status_code, e.msg))
                self._logger.debug("tfchain explorer get exception at endpoint {} on {}: {}".format(endpoint, address, e))
                pass
        raise Exception("no explorer was available to fetch endpoint {}".format(endpoint))

    def post(self, addresses, endpoint, data):
        """
        put data to an explorer at the endpoint from any explorer that is available
        on one of the given urls. The list of urls is traversed in random order until
        an explorer returns with a 200 OK status.

        @param urls: the list of urls of all available explorers
        @param endpoint: the endpoint to geyot the data from
        """
        assert len(addresses) > 0
        indices = list(range(len(addresses)))
        random.shuffle(indices)
        for idx in indices:
            try:
                address = addresses[idx]
                assert isinstance(address, str)
                # this is required in order to be able to talk directly a daemon,
                # and to specify the data format correctly
                headers = {
                    'User-Agent': 'Rivine-Agent',
                    'content-type': 'application/json',
                }
                # ensure the data is already JSON encoded and bytes
                if isinstance(data, dict):
                    data = j.data.serializers.json.dumps(data)
                if isinstance(data, str):
                    data = data.encode('utf-8')
                assert isinstance(data, bytes)
                # do the request and check the response
                resp = j.clients.http.post(url=address+endpoint, data=data, headers=headers)
                if resp.getcode() == 200:
                    return resp.readline()
                raise ExplorerCallError("call to {} resulted in an unexpected error {}".format(endpoint, resp.getcode()))
            except HTTPError as e:
                if e.status_code:
                    raise ExplorerCallError("call to {} resulted in an error {}: {}".format(endpoint, e.status_code, e.msg))
                self._logger.debug("tfchain explorer get exception at endpoint {} on {}: {}".format(endpoint, address, e))
                pass
        raise Exception("no explorer was available to fetch endpoint {}".format(endpoint))

    def test(self):
        """
        js_shell 'j.clients.tfchain.explorer.test()'
        """
        resp = self.get(addresses=['https://explorer2.threefoldtoken.com'], endpoint='/explorer/constants')
        data = j.data.serializers.json.loads(resp)
        assert data['chaininfo']['Name'] == 'tfchain'
        assert data['chaininfo']['CoinUnit'] == 'TFT'
