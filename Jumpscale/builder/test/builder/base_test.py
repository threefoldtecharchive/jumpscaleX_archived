from Jumpscale import j
from random import randint
from unittest import TestCase
import requests
from testconfig import config


class BaseTest(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        pass

    def tearDown(self):
        pass



