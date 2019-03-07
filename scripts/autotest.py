from utils import Utils
import os
import sys


class RunTests(Utils):

    def run_tests(self, image_name, run_cmd, commit):
        self.image_check(image_name)
        hub_image = '{}/jumpscalex'.format(self.username)
        docker_cmd = 'docker run --rm -t {} /bin/bash -c'.format(image_name)
        env_cmd = 'export {};'.format(self.exports)
        if image_name == hub_image:
            commit_cmd = 'cd /sandbox/code/github/threefoldtech/jumpscaleX/; git pull; git reset --hard {};'.format(
                commit)
        else:
            commit_cmd = ""
        cmd = '{} "{} {} {}"'.format(docker_cmd, env_cmd, commit_cmd, run_cmd)
        response = self.execute_cmd(cmd)
        return response

    def report(self, status, file_link, commit, commiter):
        if status:
            self.send_msg('Tests Passed ' + file_link, commit=commit, commiter=commiter)
            self.github_status_send('success', file_link, commit=commit)
        else:
            self.send_msg('Tests had errors ' + file_link, commit=commit, commiter=commiter)
            self.github_status_send('failure', file_link, commit=commit)

    def image_check(self, image_name):
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
        images_name = response.stdout.split()
        if image_name not in images_name:
            self.send_msg('Could not find image', push=True)
            sys.exit()
