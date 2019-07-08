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
        """

    def _init(self, **kwargs):
        self.URL = '{0}:{1}/graphql'.format(self.url, str(self.port))
        self._session = requests.Session()


    def query(self, query):
        res = self._session.post(self.URL, headers={'content-type':'application/json'}, data=json.dumps({
            'variables': None,
            'operationName': None,
            'query' : query
        }))

        if res.status_code != 200:
            self._log_debug('Error during request')
            self._log_debug(res.reason)
            return ''

        return res.json()

    def mutation(self, mutation):
        return self.query('mutation{1}'.format(mutation))

    def subscription(self, subscription):
        return self.query('subscription{1}'.format(subscription))

