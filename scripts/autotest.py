from utils import Utils
import os
import sys


class RunTests(Utils):

    def run_tests(self):
        docker_cmd = 'docker run --rm -t {}/jumpscalex /bin/bash -c'.format(self.username)
        env_cmd = 'source /sandbox/env.sh; export NACL_SECRET={};'.format(self.nacl)
        commit_cmd = 'cd /sandbox/code/github/threefoldtech/jumpscaleX/; git pull; git reset --hard {};'.format(
            self.commit)
        run_cmd = 'python3.6 test.py 1>/dev/null'
        cmd = '{} "{} {} {}"'.format(docker_cmd, env_cmd, commit_cmd, run_cmd)
        response = self.execute_cmd(cmd)
        if 'Error In' in response.stdout:
            file_name = '{}.log'.format(self.commit[:7])
            file_link = self.write_file(response.stdout[response.stdout.find('Error In'):], file_name=file_name)
            self.send_msg('Tests had errors ' + file_link, push=True)
        else:
            self.send_msg('Tests Passed', push=True)

    def image_check(self):
        image_name = '{}/jumpscalex'.format(self.username)
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
        images_name = response.stdout.split()
        if image_name not in images_name:
            sys.exit()


if __name__ == "__main__":
    test = RunTests()
    test.image_check()
    test.run_tests()
