import unittest
import subprocess
from loguru import logger
from testconfig import config


class BaseTest(unittest.TestCase):
    LOGGER = logger
    LOGGER.add("installtion_{time}.log")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.js_branch = config["main"]["branch"]
        self.js_container = config["main"]["container_name"]

    def setUp(self):
        pass

    def info(self, message):
        self.LOGGER.info(message)

    def linux_os(self, command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = process.communicate()
        return output, error

    def jumpscale_installtion(self):
        self.info("curl installtion script")
        command = "curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/{}/install/jsx.py?$RANDOM > /tmp/jsx".format(
            self.js_branch
        )

        self.linux_os(command)

        self.info("Change installer script [/tmp/jsx]to be executed ")
        command = "chmod +x /tmp/jsx"
        self.linux_os(command)

        self.info("Run script with container-install")
        command = "/tmp/jsx container_install -n {}".format(self.container_name)
        output, error = self.linux_os(command)
        return output, error
