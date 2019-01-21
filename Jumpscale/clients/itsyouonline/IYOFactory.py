from Jumpscale import j
from .IYOClient import IYOClient
import requests

import time

DEFAULT_BASE_URL = "https://itsyou.online/api"


class IYOFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = 'j.clients.itsyouonline'
    _CHILDCLASS = IYOClient

    def _init(self):
        self.raml_spec = "https://raw.githubusercontent.com/itsyouonline/identityserver/master/specifications/api/itsyouonline.raml"
        self._default = None

    @property
    def default(self):
        """ return default itsyou.online instance"""
        if self._default is None:
            self._default = self.get(name="default")
        return self._default

    def test(self):
        """
        do:
        js_shell 'j.clients.itsyouonline.test()'
        """

        client = j.clients.itsyouonline.get(name="test")
        jwt = client.jwt_get(scope="user:admin")
        username = jwt.username
        self._logger.debug("Creating a test organization")
        test_globa_id = "test_org"
        client.api.organizations.CreateNewOrganization(
            {"globalid": test_globa_id, "owners": [jwt.username], "dns": [], "includes": [], "includesuborgsof": [],
             "members": [], "orgmemmbers": [], "orgowners": [], "publicKeys": [], "requiredscopes": []})
        self._logger.debug("getting the test organization details")
        org = client.api.organizations.GetOrganization(test_globa_id)
        assert org.data.globalid == test_globa_id
        self._logger.debug("deleting the test organization")
        res = client.api.organizations.DeleteOrganization(test_globa_id)
        assert res.ok


        # Read all the API keys registered for your user
        self._logger.debug("list all API keys")
        for key in client.api.users.ListAPIKeys(username).data:
            self._logger.debug("label: %s" % key.label)
            self._logger.debug("app ID %s" % key.applicationid)

        # Create a new API key (is really a developer way though)
        from requests.exceptions import HTTPError
        try:
            key = client.api.users.AddApiKey({"label": 'test'}, username).data
            self._logger.debug("create new API key: ")
            self._logger.debug("label: %s" % key.label)
            self._logger.debug("app ID %s" % key.applicationid)
        except HTTPError as err:
            # example of how to deal with exceptions
            if err.response.status_code == 409:
                # the key with this label already exists, no need to do anything
                pass
            else:
                raise err

        key_labels = [k.label for k in client.api.users.ListAPIKeys(username).data]
        assert 'test' in key_labels

        self._logger.debug("delete api key")
        client.api.users.DeleteAPIkey('test', username)

        key_labels = [k.label for k in client.api.users.ListAPIKeys(username).data]
        assert 'test' not in key_labels

    def test_jwt(self):
        client = j.clients.itsyouonline.get(name="test")
        token = client.jwt_get(scope="user:admin", validity=5)
        token2 = client.jwt_get()

        assert token.jwt == token2.jwt

        #test is still very minimal would be good to do more

        # from time import sleep
        # sleep(10)
        #
        # token3 = client.jwt_get()
        # assert token3.jwt != token.jwt
