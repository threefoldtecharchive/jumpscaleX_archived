from utils import Utils
import os


class RunTests(Utils):
    def run_tests(self):
        docker_cmd = 'docker run --rm -t jumpscale /bin/bash -c'.format()
        env_cmd = 'source /sandbox/env.sh; export NACL_SECRET={};'.format(os.environ.get('Nacl'))
        commit_cmd = 'git pull; git reset --hard {};'.format(os.environ.get('commit'))
        run_cmd = 'python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/test.py 1>/dev/null'
        cmd = '{} "{} {} {}"'.format(docker_cmd, env_cmd, commit_cmd, run_cmd)
        response = self.execute_cmd(cmd)
        if 'Error In' in response.stdout:
            file_link = self.write_file(response.stdout[response.stdout.find('Error In'):])
            self.send_msg('Tests had errors ' + file_link)
        else:
            self.send_msg('Tests Passed')


if __name__ == "__main__":
    test = RunTests()
    test.run_tests()
