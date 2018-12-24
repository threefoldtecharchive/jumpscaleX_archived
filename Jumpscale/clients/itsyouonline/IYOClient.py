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
        jwt_list =  (LO) !jumpscale.itsyouonline.jwt.1 
        
        @url = jumpscale.itsyouonline.jwt.1    
        name = "" (S)    
        jwt = "" (S)
        scope = "" (S)
        validity = 2592000 (I)  #the time in sec when to expire after last refresh, std 1 month
        expires =  (D)
        last_refresh = (D)
        refreshable = true (B)
        refresh_token = "" (S)
        
        
        """

    def _data_trigger_new(self):
        self.delete()
        if self.application_id is "" or self.secret is "":
            self.application_id  = j.tools.console.askString("Please provide itsyouonline application id:\ncan find on https://itsyou.online/#/settings\n")
            self.secret = j.tools.console.askString("Please provide itsyouonline secret:\ncan find on https://itsyou.online/#/settings\n")
            self.save()

    def _init(self):
        self.reset()

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
            if self._lastjwt is None:
                self.jwt_get()
            self._api.session.headers.update({"Authorization": 'bearer {}'.format(self._lastjwt)})

        return self._api

    @property
    def oauth2_client(self):
        """Generated itsyou.onine client oauth2 client"""
        if self._oauth2_client is None:
            self._oauth2_client = self.client.Oauth2ClientOauth_2_0  #WEIRD NAME???
        return self._oauth2_client


    def jwt_get(self,name="default",die=True):

        for item in self.data.jwt_list:
            if item.name == name:
                #TODO: need to check if we need to refresh
                # if self.jwt == "" or self.jwt_expires<j.data.time.epoch:
                #     self.jwt_refresh()
                self._lastjwt = item.jwt
                return item
        if die:
            raise RuntimeError("could not find jwt with name:%s"%name)


    def jwt_get_from_iyo(self,name="default",refreshable=True,validity=2592000,scope=None):
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

        if refreshable:
            if scope.find("offline_access") == -1:
                scope += ',offline_access'

        jwt_obj = self.jwt_get(name=name, die=False)
        if jwt_obj is None:
            jwt_obj = self.data.jwt_list.new()
        jwt_obj.name=name
        jwt_obj.refreshable = refreshable
        jwt_obj.scope = scope
        jwt_obj.validity = validity


        params = {
            'grant_type': 'client_credentials',
            'client_id': self.application_id,
            'client_secret': self.secret,
            'response_type': 'id_token',
            'scope': scope,
        }

        if jwt_obj.validity>0:
            params["validity"] = validity


        url = urllib.parse.urljoin(base_url, '/v1/oauth/access_token')
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        jwt_text = resp.content.decode('utf8')
        jwt_data = jwt.get_unverified_claims(jwt_text)

        jwt_obj.scope = ",".join(jwt_data["scope"])
        jwt_obj.username = jwt_data["username"]
        jwt_obj.refresh_token = jwt_data["refresh_token"]
        jwt_obj.expires = jwt_data["exp"]
        jwt_obj.jwt = jwt_text
        jwt_obj.last_refresh = j.data.time.epoch

        self._lastjwt = jwt_obj.jwt

        self.save()

        return jwt_obj


    def reset(self):
        self._client = None
        self._api = None
        self._oauth2_client = None
        self._lastjwt = None




