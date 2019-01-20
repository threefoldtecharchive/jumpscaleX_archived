from Jumpscale import j


class BuilderEtcd(j.builder.system._BaseClass):
    NAME = 'etcd'

    def _init(self):
        self.package_path = j.builder.runtimes.golang.package_path_get('etcd', host='go.etcd.io')
        self.bins = [
            j.sal.fs.joinPaths(self.package_path, 'bin', 'etcd'),
            j.sal.fs.joinPaths(self.package_path, 'bin', 'etcdctl')
        ]

    def build(self, reset=False):
        """
        Build etcd
        """
        if self._done_check('build', reset):
            return

        j.builder.runtimes.golang.install()
        # get a vendored etcd from master
        j.builder.runtimes.golang.get('go.etcd.io/etcd', install=False, update=False)
        # go to package path and build (for etcdctl)
        j.builder.runtimes.golang.execute('cd %s && ./build' % self.package_path)

        self._done_set('build')

    def client_get(self, name):
        """
        return the client to the installed server, use the config params of the server to create a client for
        :return:
        """
        return j.clients.etcd.get(name)

    def _test(self, name=''):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key='test_main')
