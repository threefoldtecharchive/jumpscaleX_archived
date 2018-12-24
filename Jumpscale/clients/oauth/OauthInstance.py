import urllib.request
import urllib.parse
import urllib.error
import string
import requests
import time
import random
from Jumpscale import j
JSConfigClient = j.application.JSBaseConfigClass


class OauthClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.oauth.client
        addr = "" (S)
        accesstokenaddr = "" (S)
        client_id = "" (S)
        secret_ = "" (S)
        scope = "" (S)
        redirect_url = "" (S)
        user_info_url = "" (S)
        logout_url = "" (S)
        client_instance = "github" (S)
        """

    def _init(self):
        self.addr = self.addr
        self.accesstokenaddr = self.accesstokenaddr
        self.client_id = self.client_id
        self.secret = self.secret_
        self.scope = self.scope
        self.redirect_url = self.redirect_url
        self.user_info_url = self.user_info_url
        self.logout_url = self.logout_url
        self.client_instance = self.client_instance
        self._client = None
        self.instance = "main"

    @property
    def client(self):
        if self._client:
            return self._client

        if self.client_instance in ('itsyouonline', 'itsyou.online'):
            self._client = ItsYouOnline(
                self.addr,
                self.accesstokenaddr,
                self.client_id,
                self.secret,
                self.scope,
                self.redirect_url,
                self.user_info_url,
                self.logout_url,
                self.instance)
        else:
            self._client = OauthInstance(
                self.addr,
                self.accesstokenaddr,
                self.client_id,
                self.secret,
                self.scope,
                self.redirect_url,
                self.user_info_url,
                self.logout_url,
                self.instance)

        return self._client


class AuthError(Exception):
    def _init(self):
        pass


class UserInfo(object):

    def _init(self, username, emailaddress, groups):
        self.username = username
        self.emailaddress = emailaddress
        self.groups = groups


class OauthInstance():

    def __init__(
            self,
            addr,
            accesstokenaddr,
            client_id,
            secret,
            scope,
            redirect_url,
            user_info_url,
            logout_url,
            instance):
        if not addr:
            raise RuntimeError(
                "Failed to get oauth instance, no address provided")
        else:
            self.addr = addr
            self.client_id = client_id
            self.scope = scope
            self.redirect_url = redirect_url
            self.accesstokenaddress = accesstokenaddr
            self.secret = secret
            self.user_info_url = user_info_url
            self.logout_url = logout_url
        self.state = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(30))

    @property
    def url(self):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_url,
            'state': self.state,
            'response_type': 'code'}
        if self.scope:
            params.update({'scope': self.scope})
        return '%s?%s' % (self.addr, urllib.parse.urlencode(params))

    def getAccessToken(self, code, state):
        payload = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.secret,
            'redirect_uri': self.redirect_url,
            'grant_type': 'authorization_code',
            'state': state}
        result = requests.post(self.accesstokenaddress, data=payload, headers={
            'Accept': 'application/json'})

        if not result.ok or 'error' in result.json():
            msg = result.json()['error']
            self._logger.error(msg)
            raise AuthError(msg)
        return result.json()

    def getUserInfo(self, accesstoken):
        params = {'access_token': accesstoken['access_token']}
        userinforesp = requests.get(self.user_info_url, params=params)
        if not userinforesp.ok:
            msg = 'Failed to get user details'
            self._logger.error(msg)
            raise AuthError(msg)

        userinfo = userinforesp.json()
        return UserInfo(userinfo['login'], userinfo['email'], ['user'])


class ItsYouOnline(OauthInstance):
    def __init__(
            self,
            addr,
            accesstokenaddr,
            client_id,
            secret,
            scope,
            redirect_url,
            user_info_url,
            logout_url,
            instance):
        OauthInstance.__init__(
            self,
            addr,
            accesstokenaddr,
            client_id,
            secret,
            scope,
            redirect_url,
            user_info_url,
            logout_url,
            instance)

    def getAccessToken(self):
        return j.clients.itsyouonline.jwt_get(self.client_id, self.secret)

    def getUserInfo(self, accesstoken):
        import jose
        import jose.jwt
        jwt = accesstoken
        headers = {'Authorization': 'bearer %s' % jwt}

        jwtdata = jose.jwt.get_unverified_claims(jwt)
        scopes = jwtdata['scope']
        requestedscopes = set(self.scope.split(','))
        if set(jwtdata['scope']).intersection(
                requestedscopes) != requestedscopes:
            msg = 'Failed to get the requested scope for %s' % self.client_id
            raise AuthError(msg)

        username = jwtdata['username']
        userinfourl = self.user_info_url.rstrip('/') + "/%s/info" % username
        userinforesp = requests.get(userinfourl, headers=headers)
        if not userinforesp.ok:
            msg = 'Failed to get user details'
            raise AuthError(msg)

        groups = ['user']
        for scope in scopes:
            parts = scope.split(':')
            if len(parts) == 3 and parts[:2] == ['user', 'memberof']:
                groups.append(parts[-1].split('.')[-1])

        userinfo = userinforesp.json()
        return UserInfo(
            userinfo['username'],
            userinfo['emailaddresses'][0]['emailaddress'],
            groups)
