import unittest
import subprocess
from loguru import logger
import uuid, platform
from parameterized import parameterized

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
        output, error = self.os_command(command)
        branch = output.decode()[output.decode().find("head") + 6 : -1]
        return branch

    def get_os_type(self):
        os = platform.system()
        if os == "Darwin":
            return "Mac"
        return os

    def os_command(self, command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = process.communicate()
        process.kill()
        return output, error

    def jumpscale_installtion(self, install_type, options=" "):
        self.info("copy installtion script to /tmp")
        command = "cp {}/install/jsx.py  /tmp/jsx".format(self.repo_location)
        self.os_command(command)

        self.info("Change installer script [/tmp/jsx]to be executed ")
        command = "chmod +x /tmp/jsx"
        self.os_command(command)
        self.info("Configure the non-interactive option")
        command = "/tmp/jsx configure --no-interactive -s mysecret;"
        output, error = self.os_command(command)

        self.info("Run script with {} with branch {}".format(install_type, self.js_branch))
        command = "/tmp/jsx {}  --no-interactive -b {} {}".format(install_type, self.js_branch, options)
        output, error = self.os_command(command)
        return output, error

    def check_js_container_installtion(self):
        self.info(" Check that js container exist ,should succeed")
        command = "/tmp/jsx container-kosmos"
        output, error = self.os_command(command)
        if error:
            output, error = self.jumpscale_installtion("container-install", "-n {}".format(self.js_container))
            if error:
                return False
            if "install succesfull" not in output.decode():
                return False

        return True
