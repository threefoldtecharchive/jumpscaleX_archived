import unittest
import subprocess
from loguru import logger
import uuid, platform

CONTAINER_NAME = str(uuid.uuid4()).replace("-", "")[:10]

class BaseTest(unittest.TestCase):
    LOGGER = logger
    LOGGER.add("installtion_{time}.log")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repo_location = "/opt/code/github/threefoldtech/jumpscaleX"
        self.js_branch = self.get_js_branch()
        self.ssh_key = self.get_loaded_key()
        self.os_type = self.get_os_type()
        self.js_container = CONTAINER_NAME

    def setUp(self):
        pass

    def info(self, message):
        self.LOGGER.info(message)

    def get_loaded_key(self):
        command = "ssh-add -L"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = process.communicate()
        return output.decode().strip()

    def get_js_branch(self):
        command = "cd {} && cat .git/HEAD".format(self.repo_location)
        output, error = self.linux_os(command)
        branch = output.decode()[output.decode().find("head") + 6 : -2]
        return branch

    def get_os_type(self):
        os = platform.system()
        if os == "Darwin":
            return "Mac"
        return os

    def linux_os(self, command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = process.communicate()
        return output, error

    def jumpscale_installtion(self):
        self.info("copy installtion script to /tmp")
        command = "cp {}/install/jsx.py  /tmp/jsx".format(self.repo_location)
        self.linux_os(command)

        self.info("Change installer script [/tmp/jsx]to be executed ")
        command = "chmod +x /tmp/jsx"
        self.linux_os(command)

        self.info("Configure the non-interactive option")
        command = "/tmp/jsx configure --no_interactive -s mysecret;"

        self.info("Run script with container-install")
        command = "/tmp/jsx container-install  --no_interactive -n {} ".format(self.js_container)
        output, error = self.linux_os(command)
        return output, error

    def check_js_container_installtion(self):
        self.info(" Check that js container exist ,should succeed")
        command = "/tmp/jsx container-kosmos"
        output, error = self.linux_os(command)
        if error:
            output, error = self.jumpscale_installtion()
            if "install succesfull" not in output.decode():
                return False

        return True

    def jumpscale_installtion_insystem(self):
        self.info("curl installtion script")
        command = "curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/{}/install/jsx.py?$RANDOM > /tmp/jsx".format(
            self.js_branch
        )

        self.linux_os(command)

        self.info("Change installer script [/tmp/jsx]to be executed ")
        command = "chmod +x /tmp/jsx"
        self.linux_os(command)

        
        self.info("set a secret for jumpscale ")
        command = "/tmp/jsx configure --no-interactive -s mypassword"
        self.linux_os(command)
        
        self.info("Run script with install option")
        command = "/tmp/jsx install --no-interactive"
        output, error = self.linux_os(command)
        return output, error
