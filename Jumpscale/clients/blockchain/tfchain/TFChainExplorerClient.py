"""
Tfchain Client
"""

from Jumpscale import j
from Jumpscale.clients.http.HttpClient import HTTPError

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
        if not isinstance(addresses, list) or len(addresses) == 0:
            raise j.exceptions.Value(
                "addresses expected to be a non-empty list of string-formatted explorer addresses, not {}".format(
                    type(addresses)
                )
            )
        indices = list(range(len(addresses)))
        random.shuffle(indices)
        for idx in indices:
            try:
                address = addresses[idx]
                if not isinstance(address, str):
                    raise j.exceptions.Value("explorer address expected to be a string, not {}".format(type(address)))
                # this is required in order to be able to talk directly a daemon
                headers = {"User-Agent": "Rivine-Agent"}
                # do the request and check the response
                resp = j.clients.http.get_response(url=address + endpoint, headers=headers)
                if resp.getcode() == 200:
                    return resp.readline()
                if resp.getcode() == 204:
                    raise j.clients.tfchain.errors.ExplorerNoContent("GET: no content available (code: 204)", endpoint)
                raise j.clients.tfchain.errors.ExplorerServerError("error (code: {})".format(resp.getcode()), endpoint)
            except HTTPError as e:
                if e.status_code == 400:
                    msg = e.msg
                    if isinstance(msg, (bytes, bytearray)):
                        msg = msg.decode("utf-8")
                    if isinstance(msg, str) and (("unrecognized hash" in msg) or ("not found" in msg)):
                        raise j.clients.tfchain.errors.ExplorerNoContent(
                            "GET: no content available for specified hash (code: 400)", endpoint
                        )
                if e.status_code:
                    raise j.clients.tfchain.errors.ExplorerServerError(
                        "GET: error (code: {}): {}".format(e.status_code, e.msg), endpoint
                    )
                self._log_debug("tfchain explorer get exception at endpoint {} on {}: {}".format(endpoint, address, e))
                pass
        raise j.clients.tfchain.errors.ExplorerNotAvailable(
            "no explorer was available", endpoint=endpoint, addresses=addresses
        )

    def post(self, addresses, endpoint, data):
        """
        put data to an explorer at the endpoint from any explorer that is available
        on one of the given urls. The list of urls is traversed in random order until
        an explorer returns with a 200 OK status.

        @param urls: the list of urls of all available explorers
        @param endpoint: the endpoint to geyot the data from
        """
        if not isinstance(addresses, list) or len(addresses) == 0:
            raise j.exceptions.Value(
                "addresses expected to be a non-empty list of string-formatted explorer addresses, not {}".format(
                    type(addresses)
                )
            )
        indices = list(range(len(addresses)))
        random.shuffle(indices)
        for idx in indices:
            try:
                address = addresses[idx]
                if not isinstance(address, str):
                    raise j.exceptions.Value("explorer address expected to be a string, not {}".format(type(address)))
                # this is required in order to be able to talk directly a daemon,
                # and to specify the data format correctly
                headers = {"User-Agent": "Rivine-Agent", "content-type": "application/json"}
                # ensure the data is already JSON encoded and bytes
                if isinstance(data, dict):
                    data = j.data.serializers.json.dumps(data)
                if isinstance(data, str):
                    data = data.encode("utf-8")
                if not isinstance(data, bytes):
                    raise j.exceptions.Value("expected post data to be bytes, not {}".format(type(data)))
                # do the request and check the response
                resp = j.clients.http.post(url=address + endpoint, data=data, headers=headers)
                if resp.getcode() == 200:
                    return resp.readline()
                raise j.clients.tfchain.errors.ExplorerServerPostError(
                    "POST: unexpected error (code: {})".format(resp.getcode()), endpoint, data=data
                )
            except HTTPError as e:
                if e.status_code:
                    raise j.clients.tfchain.errors.ExplorerServerPostError(
                        "POST: error (code: {}): {}".format(e.status_code, e.msg), endpoint, data=data
                    )
                self._log_debug("tfchain explorer get exception at endpoint {} on {}: {}".format(endpoint, address, e))
                pass
        raise j.clients.tfchain.errors.ExplorerNotAvailable(
            "no explorer was available", endpoint=endpoint, addresses=addresses
        )

    def test(self):
        """
        kosmos 'j.clients.tfchain.explorer.test()'
        """
        resp = self.get(addresses=["https://explorer2.threefoldtoken.com"], endpoint="/explorer/constants")
        data = j.data.serializers.json.loads(resp)
        assert data["chaininfo"]["Name"] == "tfchain"
        assert data["chaininfo"]["CoinUnit"] == "TFT"
