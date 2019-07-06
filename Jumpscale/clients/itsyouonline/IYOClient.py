import urllib
import requests

try:
    import jose.jwt
except ImportError:
    raise RuntimeError("jose not installed ")

from jose import jwt
from time import time

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

    def _init(self, **kwargs):
        # self.delete()
        self.reset()
        if self.application_id is "" or self.secret is "":
            self.application_id = j.tools.console.askString(
                "Please provide itsyouonline application id:\ncan find on https://itsyou.online/#/settings\n"
            )
            self.secret = j.tools.console.askString(
                "Please provide itsyouonline secret:\ncan find on https://itsyou.online/#/settings\n"
            )
            self.save()

    @property
    def client(self):
        """Generated itsyou.online client"""
        if self._client is None:
            self._client = Client(base_uri=self.baseurl)
        return self._client

    @property
    def api(self):
        """Generated itsyou.online client api"""
        if self._api is None:
            self._api = self.client.api
            if self._lastjwt is None:
                self.jwt_get()
            self._api.session.headers.update({"Authorization": "bearer {}".format(self._lastjwt)})

        return self._api

    @property
    def oauth2_client(self):
        """Generated itsyou.online client oauth2 client"""
        if self._oauth2_client is None:
            self._oauth2_client = self.client.Oauth2ClientOauth_2_0  # WEIRD NAME???
        return self._oauth2_client

    def jwt_get(self, name="default", refreshable=True, validity=2592000, scope=None, die=False, reset=False):
        """
        returns a jwt if not set and update authorization header with that jwt
        :param name: jwt name
        :param refreshable: True if the jwt token will be refreshable
        :param validity: the validity of the jwt token
        :param scope: jwt scope, read itsyouonline docs to learn what scope to use
        :param die: die if the jwt name not found
        :return:
        """

        if self.application_id == "" or self.secret == "":
            raise RuntimeError("please go to j.clients.itsyouonline.get() to get a new client")
        x = 0
        for item in self.data.jwt_list:
            if item.name == name:
                if reset:
                    self.data.jwt_list.pop(x)
                else:
                    item.jwt = j.clients.itsyouonline.jwt_refresh(item.jwt)
                    self._lastjwt = item.jwt
                    return item
            x += 1
        if die:
            raise RuntimeError("could not find jwt with name:%s" % name)

        jwt_obj = self.data.jwt_list.new()
        jwt_obj.name = name
        jwt_obj.refreshable = refreshable
        jwt_obj.scope = scope
        jwt_obj.validity = validity

        jwt_text = self._jwt_new(scope=scope, refreshable=refreshable, validity=validity)
        jwt_data = jwt.get_unverified_claims(jwt_text)

        jwt_obj.scope = ",".join(jwt_data["scope"])
        jwt_obj.username = jwt_data["username"]
        jwt_obj.refresh_token = jwt_data["refresh_token"]
        jwt_obj.expires = jwt_data["exp"]
        jwt_obj.jwt = jwt_text
        jwt_obj.last_refresh = j.data.time.epoch

        self._lastjwt = jwt_obj.jwt

        self.save()
        # force reset self api to use the new jwt
        self._api = None
        return jwt_obj

    def _jwt_new(self, scope=None, refreshable=True, validity=2592000):
        """
        gets a new JWT from auth server
        :param scope: jwt scope, please see itsyou online docs to decide what scope to use
        :param refreshable: if true it will request a refreshable token
        :param validity: the validity of the requested token
        :return: return the token as string
        """
        if scope is None:
            scope = ""
        url = urllib.parse.urljoin(self.baseurl, "/v1/oauth/access_token")
        if refreshable:
            if scope.find("offline_access") == -1:
                scope += ", offline_access"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.application_id,
            "client_secret": self.secret,
            "response_type": "id_token",
            "scope": scope,
            "validity": validity or None,
        }

        resp = requests.post(url, params=params)
        resp.raise_for_status()

        return resp.content.decode("utf8")

    def reset(self):
        self._client = None
        self._api = None
        self._oauth2_client = None
        self._lastjwt = None
