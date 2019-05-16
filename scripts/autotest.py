from utils import Utils
import os
import sys


class RunTests(Utils):
    def run_tests(self, image_name, run_cmd, repo, commit):
        """Run tests with specific image and commit.

        :param image_name: docker image name.
        :type image_name: str
        :param run_cmd: command line that will be run tests. 
        :type run_cmd: str
        :param repo: full repo name
        :type repo: str
        :param commit: commit hash 
        :type commit: str
        """
        self.image_check(image_name)
        hub_image = "{}/jumpscalex".format(self.username)
        docker_cmd = "docker run --rm -t {} /bin/bash -c".format(image_name)
        env_cmd = "export {};".format(self.exports)
        if image_name == hub_image:
            commit_cmd = "cd /sandbox/code/github/{}; git pull; git reset --hard {};".format(repo, commit)
        else:
            commit_cmd = ""
        ssh_cmd = 'ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa -q -P ""; eval `ssh-agent`; ssh-add /root/.ssh/id_rsa;'
        cmd = "{} '{} {} {} {}'".format(docker_cmd, env_cmd, commit_cmd, ssh_cmd, run_cmd)
        response = self.execute_cmd(cmd)
        return response

    def image_check(self, image_name):
        """Check if the docker image exist before run tests.

        :param image_name: docker image name 
        :type image_name: str
        """
        if image_name == "{}/jumpscalex".format(self.username):
            response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
            images_name = response.stdout.split()
            if image_name not in images_name:
                self.send_msg("Could not find image")
                sys.exit()
