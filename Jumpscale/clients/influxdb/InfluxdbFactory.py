from Jumpscale import j

from influxdb import client as influxdb
import requests
from requests.auth import HTTPBasicAuth

JSConfigFactory = j.application.JSFactoryBaseClass
JSConfigClient = j.application.JSBaseClass

TEMPLATE = """
host = "localhost"
port = 8086
username = "root"
password = ""
database = ""
ssl = false
verify_ssl = false
timeout = 0
use_udp = false
udp_port = 4444
"""




class InfluxdbFactory(JSConfigFactory):

    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.influxdb"
        self.__imports__ = "influxdb"
        JSConfigFactory.__init__(self, InfluxClient)


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
        #dont use prefab (can copy code from there for sure)
        #check is ubuntu
        #deploy influxdb


#TODO: move to separate file
class InfluxClient(JSConfigClient, influxdb.InfluxDBClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        c = self.config.data
        influxdb.InfluxDBClient.__init__(
            self,
            host=c['host'],
            port=c['port'],
            username=c['username'],
            password=c['password'] or None,
            database=c['database'] or None,
            ssl=c['ssl'],
            verify_ssl=c['verify_ssl'],
            timeout=c['timeout'] or None,
            use_udp=c['use_udp'],
            udp_port=c['udp_port'])
