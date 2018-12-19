from Jumpscale import j
import requests
from requests.auth import HTTPBasicAuth
import os

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class GrafanaFactory(JSConfigBaseFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.grafana"
        self.__imports__ = "requests"
        JSConfigBaseFactory.__init__(self, GrafanaClient)


    def install(self):
        pass
        #dont use prefab (can copy code from there for sure)
        #check is ubuntu
        #deploy grafana & call influxdb installer


TEMPLATE = """
url = ""
username = ""
password_ = ""
verify_ssl = 1
"""

JSConfigBase = j.application.JSBaseClass


class GrafanaClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        c = self.config.data
        self._url = c['url']
        self.setAuth(c['username'], c['password_'])
        self._verify_ssl = c['verify_ssl']

    def ping(self):
        url = os.path.join(self._url, 'api/org/')
        try:
            self._session.get(url, timeout=5)
            return True
        except BaseException:
            return False

    def setAuth(self, username, password):
        self._username = username
        self._password = password
        auth = HTTPBasicAuth(username, password)
        self._session = requests.session()
        self._session.auth = auth

    def updateDashboard(self, dashboard):
        if j.data.types.string.check(dashboard):
            dashboard = j.data.serializers.json.loads(dashboard)
        url = os.path.join(self._url, 'api/dashboards/db')
        data = {'dashboard': dashboard, 'overwrite': True}
        result = self._session.post(url, json=data, verify=self._verify_ssl)
        return result.json()

    def deleteDashboard(self, slug):
        url = os.path.join(self._url, 'api/dashboards/db/{}'.format(slug))
        result = self._session.delete(url, verify=self._verify_ssl)
        return result.json()

    def listDashBoards(self):
        url = os.path.join(self._url, 'api/search/')
        return self._session.get(url, verify=self._verify_ssl).json()

    def isAuthenticated(self):
        url = os.path.join(self._url, 'api/org/')
        return self._session.get(url).status_code != 401

    def delete(self, dashboard):
        url = os.path.join(self._url, 'api/dashboards', dashboard['uri'])
        return self._session.delete(url, verify=self._verify_ssl)

    def changePassword(self, newpassword):
        url = os.path.join(self._url, 'api/user/password')
        data = {'newPassword': newpassword, 'oldPassword': self._password}
        result = self._session.put(url, json=data).json()
        self.setAuth(self._username, newpassword)
        return result

    def listDataSources(self):
        url = os.path.join(self._url, 'api/datasources/')
        return self._session.get(url, verify=self._verify_ssl).json()

    def addDataSource(self, data):
        url = os.path.join(self._url, 'api/datasources/')
        return self._session.post(url, json=data, verify=self._verify_ssl).json()

    def deleteDataSource(self, name):
        url = os.path.join(self._url, 'api/datasources/name/{}'.format(name))
        return self._session.delete(url, verify=self._verify_ssl).json()
