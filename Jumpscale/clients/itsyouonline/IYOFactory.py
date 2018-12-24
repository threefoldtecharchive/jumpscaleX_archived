

from Jumpscale import j
from .IYOClient import IYOClient
import requests

import time

DEFAULT_BASE_URL = "https://itsyou.online/api"


class IYOFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = 'j.clients.itsyouonline'
    _CHILDCLASS = IYOClient

    def _init(self):
        self.raml_spec = "https://raw.githubusercontent.com/itsyouonline/identityserver/master/specifications/api/itsyouonline.raml"
        self._default = None

    # def install(self):
    #     """installs python-jose library locally
    #
    #     """
    #
    #     j.builder.runtimes.pip.install("python-jose")

    # def refresh_jwt_token(self, token, validity=86400):
    #     """refresh a jwt if expired, needs to be refreshable
    #
    #     :param token: refreshable jwt token
    #     :type token: str
    #     :param validity: expiration time of the refreshed jwt, defaults to 86400
    #     :param validity: int, optional
    #     :return: refreshed token
    #     :rtype: str
    #     """
    #
    #     try:
    #         import jose.jwt
    #     except ImportError:
    #         self._logger.info('jose not installed please use install method to get jose')
    #         return
    #     expires = self.jwt_expire_timestamp(token)
    #     if 'refresh_token' not in jose.jwt.get_unverified_claims(token):
    #         self._logger.info("Specified token can't be refreshed. Please choose another refreshable token")
    #     elif self.jwt_is_expired(expires):
    #         headers = {'Authorization': 'bearer %s' % token}
    #         params = {'validity': validity}
    #         resp = requests.get('https://itsyou.online/v1/oauth/jwt/refresh', headers=headers, params=params)
    #         resp.raise_for_status()
    #         return resp.content.decode()
    #     return token


    @property
    def default(self):
        """ return default itsyou.online instance"""
        if self._default is None:
            self._default = self.get()
        return self._default


    def test(self):
        """
        do:
        js_shell 'j.clients.itsyouonline.test()'
        """

        client=j.clients.itsyouonline.get()
        jwt = client.jwt_get_from_iyo(scope="user:memberof:tf-production")
        print(jwt)


        self._logger.info(client.api.organizations.GetOrganization("threefold"))


        username = jwt.username

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

