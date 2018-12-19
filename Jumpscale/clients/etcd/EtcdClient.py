import socket

import gevent.socket

import etcd3
from Jumpscale import j

JSConfigClient = j.application.JSBaseClass


if socket.socket is gevent.socket.socket:
    # this is needed when running from within 0-robot
    import grpc.experimental.gevent as grpc_gevent
    grpc_gevent.init_gevent()


_template = """
host = "127.0.0.1"
port = 2379
#timeout = null
user = ""
password_ = ""
"""


class EtcdClient(JSConfigClient):

    def __init__(self, instance="main", data=None, parent=None, template=None, ui=None, interactive=True):
        data = data or {}
        super().__init__(instance=instance, data=data, parent=parent, template=_template, ui=ui, interactive=interactive)
        self._api = None

    @property
    def api(self):
        if self._api is None:
            data = self.config.data
            kwargs = {
                'host': data['host'],
                'port': data['port'],
            }
            if data['user'] and data['password_']:
                kwargs.update({
                    'user': data['user'],
                    'password': data['password_']
                })
            self._api = etcd3.client(**kwargs)
        return self._api

    def put(self, key, value):
        if value.startswith("-"):
            value = "-- %s" % value
        if key.startswith("-"):
            key = "-- %s" % key
        self.api.put(key, value)

    def get(self, key):
        result = self.api.get(key)[0]
        if not result:
            raise ValueError('Key {} does not exist in etcd'.format(key))
        return result.decode('utf-8')

    def delete(self, key):
        return self.api.delete(key)
