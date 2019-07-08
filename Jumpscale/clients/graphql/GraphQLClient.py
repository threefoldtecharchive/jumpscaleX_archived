from Jumpscale import j
import requests
import ujson as json

JSConfigClient = j.application.JSBaseConfigClass

class GraphQLClient(JSConfigClient):
    """
    Client of graphql services
    """
    _SCHEMATEXT = """
        @url = jumpscale.graphql.client
        name* = "" (S)
        url = "http://127.0.0.1" (S)
        port = 7777 (I)
        subscriptions_port = 7778 (I)
        """

    def _init(self, **kwargs):
        self.URL = '{0}:{1}/graphql'.format(self.url, str(self.port))
        self.SUBSCRIPTION_URL = '{0}:{1}/graphql'.format(self.url, str(self.subscriptions_port))
        self._session = requests.Session()


    # client.query("{posts{id}}")
    def query(self, query):
        data={

            'query' : query
        }

        res = self._session.post(self.URL, headers={'content-type':'application/json'}, json=data)

        if res.status_code != 200:
            self._log_debug('Error during request')
            self._log_debug(res.reason)
            return res.reason

        return res.json()

    def mutation(self, mutation):
        return self.query('mutation{1}'.format(mutation))

    def subscription(self, subscription):
        pass
