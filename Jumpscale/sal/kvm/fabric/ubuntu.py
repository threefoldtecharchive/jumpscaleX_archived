# TODO: *3


@task
def setupNetwork(ifaces):
    interfaces = """auto lo
iface lo inet loopback
"""
    for iface, config in ifaces.items():
        interfaces += """
auto %s
iface %s inet static
    address %s
    netmask %s
""" % (
            iface,
            iface,
            config[0],
            config[1],
        )
        if iface == "eth1":
            interfaces += "    gateway %s\n" % config[2]
    sudo('echo "%s" > /etc/network/interfaces' % interfaces)
    sudo("ifdown -a; ifup -a", timeout=1)
