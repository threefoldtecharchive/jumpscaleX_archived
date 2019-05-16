# TODO: *3


@task
def setupNetwork(ifaces):
    with settings(shell="ash -c"):
        interfaces = """config interface 'loopback'
    option ifname 'lo'
    option proto 'static'
    option ipaddr '127.0.0.1'
    option netmask '255.0.0.0'

config interface 'wan6'
    option ifname '@wan'
    option proto 'dhcpv6'

config globals 'globals'
    option ula_prefix 'fd6f:a61e:5c05::/48'
    """
        for iface, config in ifaces.items():
            interfaces += """
config interface '%s'
    option ifname '%s'
    option proto 'static'
    option ipaddr '%s'
    option netmask '%s'
""" % (
                iface,
                iface,
                config[0],
                config[1],
            )
            if iface == "eth1":
                interfaces += "    option gateway '%s'\n" % config[2]
        run('echo "%s" > /etc/config/network' % interfaces)
        run("/etc/init.d/network restart", timeout=1)


@task
def pushSshKey(sshkey):
    with settings(shell="ash -c"):
        run('touch /etc/dropbear/authorized_keys; echo "%s" > /etc/dropbear/authorized_keys' % sshkey)
