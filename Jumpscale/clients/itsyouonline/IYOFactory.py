import time

import requests

from jose import jwt
from Jumpscale import j

from .IYOClient import IYOClient

DEFAULT_BASE_URL = "https://itsyou.online/api"


class IYOFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.clients.itsyouonline"
    _CHILDCLASS = IYOClient

    def _init(self, **kwargs):
        self.raml_spec = (
            "https://raw.githubusercontent.com/itsyouonline/identityserver/master/specifications/api/itsyouonline.raml"
        )
        self._default = None

    @property
    def default(self):
        """ return default itsyou.online instance"""
        if self._default is None:
            self._default = self.get(name="default")
        return self._default

    def jwt_refresh(self, jwt_token, validity=2592000, die=True):
        """
        refreshes a jwt token, if the jwt isn't expired return the same jwt
        :param jwt_token: the jwt to be refreshed
        :param validity: the validity of the new jwt
        :param die: die if the jwt is not refreshable
        :return: jwt token text
        """
        claims = jwt.get_unverified_claims(jwt_token)

        if not claims["refresh_token"]:
            if die:
                raise j.exceptions.Base("jwt token can't be refreshed, no refresh token claim found")
            else:
                return

        headers = {"Authorization": "bearer %s" % jwt_token}
        params = {"validity": validity}
        resp = requests.get("https://itsyou.online/v1/oauth/jwt/refresh", headers=headers, params=params)
        resp.raise_for_status()
        return resp.content.decode("utf8")

    def jwt_expire_timestamp(self, jwt_token):
        claims = jwt.get_unverified_claims(jwt_token)
        return claims["exp"]

    def test(self):
        """
        do:
        kosmos 'j.clients.itsyouonline.test()'
        """

        client = j.clients.itsyouonline.get(name="test_")
        jwt = client.jwt_get(scope="user:admin")
        name = client.name
        self._log_debug("Creating a test organization")
        test_globa_id = "test_org_"
        client.api.organizations.CreateNewOrganization(
            {
                "globalid": test_globa_id,
                "owners": [client.name],
                "dns": [],
                "includes": [],
                "includesuborgsof": [],
                "members": [],
                "orgmemmbers": [],
                "orgowners": [],
                "publicKeys": [],
                "requiredscopes": [],
            }
        )
        self._log_debug("getting the test organization details")
        org = client.api.organizations.GetOrganization(test_globa_id)
        assert org.data.globalid == test_globa_id
        self._log_debug("deleting the test organization")
        res = client.api.organizations.DeleteOrganization(test_globa_id)
        assert res.ok

        # Read all the API keys registered for your user
        ### needs authorization
        # self._log_debug("list all API keys")
        # for key in client.api.users.ListAPIKeys(name, headers={"Authorization": jwt.jwt}).data:
        #     self._log_debug("label: %s" % key.label)
        #     self._log_debug("app ID %s" % key.applicationid)

        # # Create a new API key (is really a developer way though)
        # from requests.exceptions import HTTPError

        # try:
        #     key = client.api.users.AddApiKey({"label": "test"}, name).data
        #     self._log_debug("create new API key: ")
        #     self._log_debug("label: %s" % key.label)
        #     self._log_debug("app ID %s" % key.applicationid)
        # except HTTPError as err:
        #     # example of how to deal with exceptions
        #     if err.response.status_code == 409:
        #         # the key with this label already exists, no need to do anything
        #         pass
        #     else:
        #         raise err

        # key_labels = [k.label for k in client.api.users.ListAPIKeys(name).data]
        # assert "test_" in key_labels

        # self._log_debug("delete api key")
        # client.api.users.DeleteAPIkey("test_", name)

        # key_labels = [k.label for k in client.api.users.ListAPIKeys(name).data]
        # assert "test_" not in key_labels

        # test jwt
        self._test_jwt()

    def _test_jwt(self):
        client = j.clients.itsyouonline.get(name="test_")
        token = client.jwt_get(scope="user:admin", validity=5)
        token2 = client.jwt_get()

        assert token.jwt == token2.jwt
        print("TEST OK")

        # test is still very minimal would be good to do more

        # from time import sleep
        # sleep(10)
        #
        # token3 = client.jwt_get()
        # assert token3.jwt != token.jwt
