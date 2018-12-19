""" A Jumpscale-configurable wrapper for CoreDNS

    unit tests are in core9 tests/jumpscale_tests/test12_etcd_coredns.py
"""

class CoreDNSFactory:

    __jslocation__ = "j.clients.coredns"
    __jsbase__ = 'j.tools.configmanager._base_class_configs'

    @property
    def _child_class(self):
        return self._jsbase(('CoreDNS', '.CoreDNS'))

    def configure(self, instance="main", etcpath="/skydns",
                  ):
        """ :param instance:
            :param etcdpath:
            :return:
        """

        data = {}
        data["etcdpath"] = etcdpath
        #data["port"] = str(port)

        return self.get(instance=instance, data=data, create=True,
                        interactive=False)

    def test(self):
        d = self._j.clients.coredns.get()
        z = d.zone_get('local/skydns')
        #print (z.get_records())
        #print (z.get_records('x1','txt'))

        #print (z.get_records('','txt'))
        for x in z.get_records('x1','a'):
            print (x)

        z2 = d.zone_get('local/skydns/x1')
        for x in z2.get_records('','a'):
            print (x)
        return

        print (z.get_records('','srv'))
        print (z.get_records('','aaaa'))
        print (z.get_records(''))
        z = d.zone_get('local/skydns/x5')
        print (z.get_records('','srv'))

        z = d.zone_get('local/skydns/x1')
        print (z.get_records('','txt'))

        z = d.zone_get('local/skydns/x3')
        print (z.get_records(''))
        print (z.get_records('', 'aaaa'))
