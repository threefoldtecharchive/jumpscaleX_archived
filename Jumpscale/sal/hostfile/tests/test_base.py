from Jumpscale import j


def test_main(self=None):
    """
    to run:

    js_shell 'j.sal.hostfile._test(name="base")'

    """
    try:
        hostfile = HostFile()
        path = hostfile._host_filepath
        backup = '{}.bu'.format(path)
        if j.sal.fs.exists(path):
            j.sal.fs.moveFile(path, backup)

        j.sal.process.execute('echo "194.45.24.74 test" >> {}'.format(path))
        assert hostfile.ip_exists('194.45.24.74') is True
        hostfile.hostnames_set('194.45.24.74', ['testhostname'])
        assert 'testhostname' in hostfile.hostnames_get('194.45.24.74')
        hostfile.ip_remove('194.45.24.74')
        assert hostfile.ip_exists('194.45.24.74') is False
    finally:
        if j.sal.fs.exists(backup):
            j.sal.fs.moveFile(backup, path)
