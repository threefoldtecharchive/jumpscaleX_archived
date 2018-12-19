import urllib
import requests

from Jumpscale import j
from clients.itsyouonline.generated.client import Client

TEMPLATE = """
baseurl = "https://itsyou.online/api"
application_id_ = ""
secret_ = ""
"""


# TODO:*1 FROM CLIENT import .... and put in client property
# TODO:*1 regenerate using proper goraml new file & newest generation tools ! (had to fix manually quite some issues?)

JSConfigBase = j.application.JSBaseClass


class IYOClient(JSConfigBase):
    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self,
                              instance=instance,
                              data=data,
                              parent=parent,
                              template=TEMPLATE,
                              interactive=interactive)

        self.reset()

    @property
    def client(self):
        """Generated itsyou.onine client"""
        if self._client is None:
            self._client = Client( base_uri=self.config.data['baseurl'])
        return self._client

    @property
    def api(self):
        """Generated itsyou.onine client api"""
        if self._api is None:
            self._api = self.client.api
        return self._api

    @property
    def oauth2_client(self):
        """Generated itsyou.onine client oauth2 client"""
        if self._oauth2_client is None:
            self._oauth2_client = self.client.Oauth2ClientOauth_2_0  #WEIRD NAME???
        return self._oauth2_client

    @property
    def jwt(self):
        """returns a jwt if not set and update authorization header with that jwt"""
        if self.config.data["application_id_"] == "" or self.config.data["secret_"] == "":
            raise RuntimeError("Please configure your itsyou.online, do this by calling js_shell "
                               "'j.tools.configmanager.configure(j.clients.itsyouonline,...)'")
        if not self._jwt:
            self._jwt = self.jwt_get()
            self.api.session.headers.update({"Authorization": 'bearer {}'.format(self.jwt)})
        return self._jwt

    def reset(self):
        self._jwt = None
        self._client = None
        self._api = None
        self._oauth2_client = None

    def _add_jwt_to_cache(self, key, jwt):
        """
        Add a new jwt to the client cache
        Args:
            key: key string
            jwt: jwt string
        """
        expires = j.clients.itsyouonline.jwt_expire_timestamp(jwt)
        self._cache.set(key, [jwt, expires])

    def jwt_get(self, validity=None, refreshable=True, scope=None, use_cache=False):
        """Get a a JSON Web token for an ItsYou.online organization or user.

        :param validity: time in seconds after which the JWT will become invalid, defaults to 3600
        :param validity: int, optional
        :param refreshable: If true the JWT can be refreshed, defaults to False
        :param refreshable: bool, optional
        :param scope: define scope of the jwt, defaults to None
        :param scope: str, optional
        :param use_cache: if true will add the jwt to cache and retrieve required jwt if it exists
                    if refreshable is true will refresh the cached jwt, defaults to False
        :param use_cache: bool, optional
        :return: jwt token
        :rtype: str
        """


        if use_cache:
            key = 'jwt_' + str(refreshable)
            if scope:
                key +=  '_' + scope
            if self._cache.exists(key):
                jwt = self._cache.get(key)
                jwt, expires = jwt
                if j.clients.itsyouonline.jwt_is_expired(expires):
                    if refreshable:
                        jwt = j.clients.itsyouonline.refresh_jwt_token(jwt, validity)
                        self._add_jwt_to_cache(key, jwt)
                        return jwt
                else:
                    return jwt


        base_url = self.config.data["baseurl"]

        params = {
            'grant_type': 'client_credentials',
            'client_id': self.config.data["application_id_"],
            'client_secret': self.config.data["secret_"],
            'response_type': 'id_token'
        }

        if validity:
            params["validity"] = validity

        if refreshable:
            params["scope"] = 'offline_access'

        if scope:
            if refreshable:
                params["scope"] = params["scope"] + "," + scope
            else:
                params["scope"] = scope

        url = urllib.parse.urljoin(base_url, '/v1/oauth/access_token')
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        jwt = resp.content.decode('utf8')

        if use_cache:
            self._add_jwt_to_cache(key, jwt)

        return jwt
