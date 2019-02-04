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
    name* = "" (S)
    host = "127.0.0.1" (ipaddr)
    port = 2379 (ipport)
    user = "" (S)
    password_ = "" (S)
    """

    def _init(self):
        self._log_debug(self.user)
        self._api = None

    @property
    def api(self):
        """ Get ETCD3 client object
        :return: etcd3 client object
        :rtype: Object
        """
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

    def backup(self, file_obj="snapshot.db", dirs="/root", remote="", AWS_ACCESS_KEY_ID="",
               AWS_SECRET_ACCESS_KEY="", password="rooter", backet="etcd"):

        f_obj = open("{}/{}".format(dirs, file_obj), "wb")
        j.sal.fs.writeFile("password.txt", password)

        self.api.snapshot(f_obj)

        if remote:
            rc, _, _ = j.builder.tools.run("which restic")
        if rc != 0:
            print("please make sure that restic is installed")
            return
        env = {
            'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY
        }
        j.builder.tools.run("restic -r s3:{}/{} init -p password.txt".format(remote, backet), env=env)
        j.builder.tools.run(
            "restic -r s3:{}/{} backup {}/{} -p password.txt".format(remote, backet, dirs, file_obj), env=env)
        j.builder.tools.run("rm password.txt")
        return "{}/{}".format(dirs, file_obj)
