from Jumpscale import j
from influxdb import client as influxdb
import requests
from requests.auth import HTTPBasicAuth
from .InfluxdbClient import InfluxClient
JSConfigFactory = j.application.JSFactoryBaseClass


class InfluxdbFactory(JSConfigFactory):

    """
    """
    __jslocation__ = "j.clients.influxdb"
    _CHILDCLASS = InfluxClient

    def postraw(self, data, host='localhost', port=8086, username='root', password='root', database="main"):
        """
        format in is
        '''
        hdiops,machine=unit42,datacenter=gent,type=new avg=25,max=37 1434059627
        temperature,machine=unit42,type=assembly external=25,internal=37 1434059627
        '''

        """
        url = 'http://%s:%s/write?db=%s&precision=s' % (host, port, database)
        r = requests.post(
            url, data=data, auth=HTTPBasicAuth(username, password))
        if r.content != "":
            raise j.exceptions.RuntimeError(
                "Could not send data to influxdb.\n%s\n############\n%s" % (data, r.content))

    def install(self):
        pass
        # dont use prefab (can copy code from there for sure)
        #check is ubuntu
        # deploy influxdb
