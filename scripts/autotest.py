from utils import Utils
import os
import sys


class RunTests(Utils):

    def run_tests(self, image_name, run_cmd, commit):
        """Run tests with specific image and commit.

        :param image_name: docker image name.
        :type image_name: str
        :param run_cmd: command line that will be run tests. 
        :type run_cmd: str
        :param commit: commit hash 
        :type commit: str
        """
        self.image_check(image_name)
        hub_image = '{}/jumpscalex'.format(self.username)
        docker_cmd = 'docker run --rm -t {} /bin/bash -c'.format(image_name)
        env_cmd = 'export {};'.format(self.exports)
        if image_name == hub_image:
            commit_cmd = 'cd /sandbox/code/github/threefoldtech/jumpscaleX/; git pull; git reset --hard {};'.format(commit)
        else:
            commit_cmd = ""
        cmd = '{} "{} {} {}"'.format(docker_cmd, env_cmd, commit_cmd, run_cmd)
        response = self.execute_cmd(cmd)
        return response

    def report(self, status, file_link, branch, commit, committer):
        """Report the result to github commit status and Telegram chat.

        :param status: test status. 
        :type status: str
        :param file_link: result file link. 
        :type file_link: str
        :param branch: branch name. 
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github. 
        :type committer: str
        """
        if status:
            self.github_status_send('success', file_link, commit=commit)
            if branch == 'development':
                self.send_msg('Tests Passed ' + file_link, commit=commit, committer=committer)

        else:
            self.github_status_send('failure', file_link, commit=commit)
            if branch == 'development':
                self.send_msg('Tests had errors ' + file_link, commit=commit, committer=committer)

    def image_check(self, image_name):
        """Check if the docker image exist before run tests.

        :param image_name: docker image name 
        :type image_name: str
        """
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
        images_name = response.stdout.split()
        if image_name not in images_name:
            self.send_msg('Could not find image')
            sys.exit()
