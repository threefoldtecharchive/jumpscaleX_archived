import urllib
import requests

try:
    import jose.jwt
except ImportError:
    raise RuntimeError('jose not installed ')

from jose import jwt

from Jumpscale import j
from clients.itsyouonline.generated.client import Client

# TODO:*1 regenerate using proper goraml new file & newest generation tools ! (had to fix manually quite some issues?)



class IYOClient(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
        @url = jumpscale.itsyouonline.1
        name* = "" (S)
        baseurl = "https://itsyou.online/api" (S)
        application_id = "" (S)
        secret = "" (S)
        jwt = "" (S)
        jwt_scope = "" (S)
        jwt_validity = 2592000 (I)  #the time in sec when to expire after last refresh, std 1 month
        jwt_expires =  (D)
        jwt_last_refresh = (D)
        jwt_refreshable = true (B)
        """

    def _data_trigger_new(self):
        self.delete()
        if self.jwt_validity < 10:
            self.jwt_validity = 2592000 #1 month
        self.jwt_refreshable = True #the default does not work above TODO:*1
        if self.application_id is "" or self.secret is "":
            self.application_id  = j.tools.console.askString("Please provide itsyouonline application id:\ncan find on https://itsyou.online/#/settings\n")
            self.secret = j.tools.console.askString("Please provide itsyouonline secret:\ncan find on https://itsyou.online/#/settings\n")
            self.save()

    def _init(self):
        self._api = None
        self._client = None
        if self.jwt == "" or self.jwt_expires<j.data.time.epoch:
            self.jwt_refresh()
        #TODO: *1 need to enable next line again, was blocked for now
        # self.api.session.headers.update({"Authorization": 'bearer {}'.format(self.jwt)})

    @property
    def client(self):
        """Generated itsyou.onine client"""
        if self._client is None:
            self._client = Client( base_uri=self.baseurl)
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

    def jwt_refresh(self):
        """returns a jwt if not set and update authorization header with that jwt"""

        if self.application_id == "" or self.secret == "":
            raise RuntimeError("Please configure your itsyou.online, do this by calling js_shell "
                               "'j.tools.configmanager.configure(j.clients.itsyouonline,...)'")

        # if j.clients.itsyouonline.jwt_is_expired(expires):
        #     if refreshable:
        #         jwt = j.clients.itsyouonline.refresh_jwt_token(jwt, validity)
        #         self._add_jwt_to_cache(key, jwt)
        #         return jwt
        # else:
        #     return jwt


        base_url = self.baseurl

        params = {
            'grant_type': 'client_credentials',
            'client_id': self.application_id,
            'client_secret': self.secret,
            'response_type': 'id_token'
        }

        if self.jwt_validity>0:
            params["validity"] = self.jwt_validity

        if self.jwt_refreshable:
            if self.scope.find("offline_access") == -1:
                self.scope += ',offline_access'

        url = urllib.parse.urljoin(base_url, '/v1/oauth/access_token')
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        self.jwt = resp.content.decode('utf8')
        self.jwt_expires = self.jwt_data["exp"]
        self.jwt_last_refresh =  j.data.time.epoch
        self.save()

        return self.jwt

    @property
    def jwt_data(self):
        """Get expiration date of jwt token

        :param token: jwt token
        :type token: str
        :return: return expiration date(timestamp) for the token
        :rtype: int
        """
        jwt_data = jwt.get_unverified_claims(self.jwt)
        return jwt_data


    def reset(self):
        self._client = None
        self._api = None
        self._oauth2_client = None
        self.jwt_refresh()


