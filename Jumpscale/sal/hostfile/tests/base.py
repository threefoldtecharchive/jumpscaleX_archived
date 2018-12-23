from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.sal.hostfile._test(name="base")'

    """

    j.sal.process.execute('echo "194.45.24.74 test" >> /etc/hosts')
    assert j.sal.hostsfile.ip_exists('194.45.24.74') is True
    j.sal.hostsfile.hostnames_set('194.45.24.74', ['testhostname'])
    assert 'testhostname' in j.sal.hostsfile.hostnames_get('194.45.24.74')
    j.sal.hostsfile.ip_remove('194.45.24.74')
    assert j.sal.hostsfile.ip_exists('194.45.24.74') is False
