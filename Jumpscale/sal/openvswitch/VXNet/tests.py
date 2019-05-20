__author__ = "delandtj"
from .vxlan import *
from netaddr import *


def rebuildVXLan():
    nl = NetLayout()
    layout = nl.load()


if __name__ == "__main__":
    print("Getting Config")
    a = NetLayout()
    layout = a.load()
    layout = a.nicdetail
    pprint_dict(layout)
    ip_layout = add_ips_to(layout)
    # full_layout = add_bridgeconfig_to(ip_layout)
    pprint_dict(ip_layout)

    print("vx1, ff31")

    vx1 = VXNet(0xFF33, backend="p2p1")
    vx1.innamespace = True
    vx1.ipv4 = IPNetwork("192.168.1.254/24")
    vx1.apply()

    # vxbackend implied (check for it)
    if "vxbackend" not in get_all_ifaces():
        print("Error: vxbackend doensn't exist")
        backend = Bridge("vxbackend")
        backend.create()
        backend.connect("dummy0")
        disable_ipv6("dummy0")

    print("\n")
    print("vx2, ff32")
    vx2 = VXNet("ff32")
    vx2.innamespace = False
    vx2.inbridge = True
    vx2.router = True
    vx2.ipv4 = IPNetwork("192.168.1.254/24")
    vx2.apply()

    print("\n")
    print("vxlan, 3456")
    vxlan = VXNet(3456)
    vxlan.ipv4 = IPNetwork("10.101.111.9/24")
    vxlan.ipv6 = IPNetwork("2a02:578:f33:a01::1/64")
    vxlan.backend = "p2p1"
    vxlan.innamespace = False
    vxlan.inbridge = False
    vxlan.apply()

    vx1.destroy()
    vx2.destroy()
    vxlan.destroy()
