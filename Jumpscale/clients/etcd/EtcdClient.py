import socket

import gevent.socket

import etcd3
from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass


if socket.socket is gevent.socket.socket:
    # this is needed when running from within 0-robot
    import grpc.experimental.gevent as grpc_gevent
    grpc_gevent.init_gevent()


class EtcdClient(JSConfigClient):
    _SCHEMATEXT = """
    @url = jumpscale.etcd.client
    host = "127.0.0.1" (S)
    port = 2379 (ipport)
    user = "" (S)
    password_ = "" (S)
    """

    def _init_new(self):
        self._logger.debug(self.user)
        self._api = None

    @property
    def api(self):
        if self._api is None:
            kwargs = {
                'host': self.host,
                'port': self.port,
            }
            if self.user and self.password_:
                kwargs.update({
                    'user': self.user,
                    'password': self.password_
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
