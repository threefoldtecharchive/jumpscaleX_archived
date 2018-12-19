import pytest
import unittest
import sys
from unittest import mock
from Jumpscale import j


class TestOpencCloudClientFactory(unittest.TestCase):
    def tearDown(self):
        """
        TearDown
        """
        # clean up all the imported modules from jumpscale (we know that its not clean and it does not clean up all the refences)
        for module in sorted([item for item in sys.modules.keys() if 'Jumpscale' in item], reverse=True):
            del sys.modules[module]

    @pytest.mark.ssh_factory
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Account')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.image_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.size_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.machines')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.configure_machine')
    def test_machine_create_name_empty(self, account, a, b, c, d):
        from JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory import Space

        try:
            model = dict()
            model["id"] = 123
            space = Space(account=account, model=model)
            space.machine_create(name=' ', sshkeyname='auto_0')
            assert False
        except RuntimeError:
            assert True

    @pytest.mark.ssh_factory
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Account')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.image_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.size_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.machines')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.configure_machine')
    def test_machine_create_image_find_id_called(self, account, a, b, c, d):
        from JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory import Space

        model = dict()
        model["id"] = 123
        space = Space(account=account, model=model)
        space.machine_create(name='dummy', sshkeyname='auto_0', image="imageName")

        space.image_find_id.assert_called_with("imageName")

    @pytest.mark.ssh_factory
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Account')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.image_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.size_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.machines')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.configure_machine')
    def test_machine_create_size_id(self, account, a, b, c, d):
        from JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory import Space

        model = dict()
        model["id"] = 123
        space = Space(account=account, model=model)
        space.machine_create(name='dummy', memsize=5, vcpus=5, sshkeyname='auto_0', image="imageName")

        space.size_find_id.assert_called_with(5, 5)

    @pytest.mark.ssh_factory
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Account')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.image_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.size_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.machines')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.configure_machine')
    def test_machine_create_configure_machine(self, account, a, b, c, d):
        from JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory import Space

        model = dict()
        model["id"] = 123
        space = Space(account=account, model=model)
        space.machine_create(name='dummy', sshkeyname='auto_0', sshkeypath='auto_0Path')

        space.configure_machine.assert_called_with(
            machine=space.machines['dummy'], name='dummy', sshkeyname='auto_0', sshkey_path='auto_0Path')

    @pytest.mark.ssh_factory
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Account')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.image_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.size_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.machines')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.createPortForward')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space._authorizeSSH')
    def test_machine_create_create_port_forward(self, account, a, b, c, e, d):
        from JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory import Space

        model = dict()
        model["id"] = 123
        space = Space(account=account, model=model)
        space.machine_create(name='dummy', sshkeyname='auto_0', sshkeypath='auto_0Path')

        machine = space.machines['dummy']
        space.createPortForward.assert_called_with(machine)

    @pytest.mark.ssh_factory
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Account')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.image_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.size_find_id')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.machines')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space.createPortForward')
    @mock.patch('JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory.Space._authorizeSSH')
    def test_machine_create_authorize_ssh(self, account, a, b, c, e, d):
        from JumpscaleLib.clients.openvcloud.OpenvCloudClientFactory import Space

        model = dict()
        model["id"] = 123
        space = Space(account=account, model=model)
        space.machine_create(name='dummy', sshkeyname='auto_0', sshkeypath='auto_0Path')

        machine = space.machines['dummy']
        space._authorizeSSH.assert_called_with(machine=machine, sshkeyname='auto_0', sshkey_path='auto_0Path')
