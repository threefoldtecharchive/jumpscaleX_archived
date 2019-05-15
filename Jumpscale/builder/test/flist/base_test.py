from Jumpscale import j
from random import randint
from unittest import TestCase
import requests
from pytest_testconfig import config


class BaseTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.client_id = self.config['itsyou']['client_id']
        self.client_secret = self.config['itsyou']['client_secret']
        self.username = self.config['itsyou']['username']
        self.node_ip = self.config['zos_node']['node_ip']

    def setUp(self):
        self.iyo_instance = 'iyo_instance_{}'.format(randint(1, 1000))
        self.iyo_client = j.clients.itsyouonline.get(self.iyo_instance, application_id=self.client_id,
                                                     secret=self.client_secret)
        self.jwt = self.iyo_client.jwt_get().jwt
        self.hub_instance = 'hub_instance_{}'.format(randint(1, 1000))
        self.zhub = j.clients.zhub.get(name=self.hub_instance, token_=self.jwt, username=self.username)
        self.zhub.authenticate()
        self.zhub.save()

        self.node_instance = 'node_instance_{}'.format(randint(1, 1000))
        self.node = j.clients.zos.get(name=self.node_instance, password=self.jwt, host=self.node_ip)

    def tearDown(self):
        pass

    def deploy_flist_container(self, builder):
        self.cont = self.node.client.container.create("https://hub.grid.tf/{}/{}.flist".format(self.username, builder))
        self.cont_client = self.node.client.container.client(self.cont.get())


