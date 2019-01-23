""" A Jumpscale-configurable wrapper for CoreDNS

    unit tests are in core9 tests/jumpscale_tests/test12_etcd_coredns.py
"""

from Jumpscale import j
from .CoreDNS import CoreDNS
JSConfigFactory = j.application.JSFactoryBaseClass


class CoreDNSFactory(JSConfigFactory):

    __jslocation__ = "j.clients.coredns"
    __jsbase__ = 'j.tools.configmanager._base_class_configs'
    _CHILDCLASS = CoreDNS

    # @property
    # def _child_class(self):
    #     return self._jsbase(('CoreDNS', '.CoreDNS'))


    def test(self):
        d = j.clients.coredns.get()
        z = d.zone_get('local/skydns')
        #print (z.get_records())
        #print (z.get_records('x1','txt'))

        #print (z.get_records('','txt'))
        for x in z.get_records('x1', 'a'):
            print (x)

        z2 = d.zone_get('local/skydns/x1')
        for x in z2.get_records('', 'a'):
            print (x)
        return

        print (z.get_records('', 'srv'))
        print (z.get_records('', 'aaaa'))
        print (z.get_records(''))
        z = d.zone_get('local/skydns/x5')
        print (z.get_records('', 'srv'))

        z = d.zone_get('local/skydns/x1')
        print (z.get_records('', 'txt'))

        z = d.zone_get('local/skydns/x3')
        print (z.get_records(''))
        print (z.get_records('', 'aaaa'))
