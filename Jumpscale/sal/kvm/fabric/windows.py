# TODO: *2


@task
def setupNetwork(ifaces):
    with settings(user="Administrator"):
        for iface, config in ifaces.items():
            if iface == "eth1":
                run(
                    'netsh interface ip set address name="%s" static %s %s gateway=%s'
                    % (iface, config[0], config[1], config[2]),
                    timeout=1,
                )
            else:
                run('netsh interface ip set address name="%s" static %s %s' % (iface, config[0], config[1]), timeout=1)


@task
def pushSshKey(sshkey):
    with settings(user="Administrator"):
        run('mkdir ~/.ssh; touch ~/.ssh/authorized_keys; echo "%s" > ~/.ssh/authorized_keys' % sshkey)
