from utils import Utils
from datetime import datetime
import sys
import os


class BuildImage(Utils):

    def image_bulid(self):
        image_name = '{}/jumpscalex'.format(self.username)
        self.images_clean(image_name=image_name)
        cmd = 'docker build --force-rm -t {} /sandbox/code/github/threefoldtech/jumpscaleX/scripts'.format(image_name)
        response = self.execute_cmd(cmd)
        if response.returncode:
            file_name = '{}.log'.format(str(datetime.now())[:10])
            file_link = self.write_file(response.stdout, file_name=file_name)
            self.images_clean()
            self.image_pull(file_link)
            sys.exit()

    def images_clean(self, image_name=None):
        if image_name:
            response = self.execute_cmd('docker rmi -f {}/jumpscalex'.format(self.username))
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
        images_name = response.stdout.split()
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$3}"')
        images_id = response.stdout.split()
        for i in range(0, len(images_id)):
            if images_name[i] == '<none>':
                response = self.execute_cmd('docker rmi -f {}'.format(images_id[i]))

    def image_push(self):
        response = self.execute_cmd('docker login --username={} --password={}'.format(self.username, self.password))
        if not response:
            self.send_msg('jumpscaleX installed Successfully, but could not login')

        response = self.execute_cmd('docker push {}/jumpscalex:latest'.format(self.username))
        if response.returncode:
            self.send_msg('jumpscaleX installed Successfully, but could not push')
        else:
            self.send_msg('jumpscaleX installed and pushed Successfully')

    def image_pull(self, file):
        response = self.execute_cmd('docker login --username={} --password={}'.format(self.username, self.password))
        if not response:
            self.send_msg('Failed to install jumpscaleX {} and could not login'.format(file))

        response = self.execute_cmd('docker pull {}/jumpscalex:latest'.format(self.username))
        if response.returncode:
            self.send_msg('Failed to install jumpscaleX {} and could not pull'.format(file))
        else:
            self.send_msg('Failed to install jumpscaleX {} and pulled Successfully'.format(file))


if __name__ == "__main__":
    build = BuildImage()
    build.image_bulid()
    build.image_push()
