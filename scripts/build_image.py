from utils import Utils
from datetime import datetime
import sys
import os


class BuildImage(Utils):

    def image_bulid(self, image_name, branch, commit=''):
        """Build docker image with specific branch and commit.

        :param image_name: docker image name.
        :type image_name: str
        :param branch: branch name.
        :type branch: str
        :param commit: commit hash (default='' for last commit).
        :type commit: str
        """
        cmd = 'docker build --force-rm -t {} . --build-arg branch={} --build-arg commit={}'.format(image_name, branch, commit)
        response = self.execute_cmd(cmd)
        return response

    def images_clean(self, image_name=None):
        """Clean docker images.

        :param image_name: docker image name (default=None to clean all incomplete images).
        :type image_name: str
        """
        if image_name:
            response = self.execute_cmd('docker rmi -f {}'.format(image_name))
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
        images_name = response.stdout.split()
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$3}"')
        images_id = response.stdout.split()
        for i in range(0, len(images_id)):
            if images_name[i] == '<none>':
                response = self.execute_cmd('docker rmi -f {}'.format(images_id[i]))

    def image_push(self):
        """Push docker image on docker hub report the status to Telegram chat.
        """
        response = self.execute_cmd('docker login --username={} --password={}'.format(self.username, self.password))
        if not response:
            self.send_msg('jumpscaleX installed Successfully, but could not login')

        response = self.execute_cmd('docker push {}/jumpscalex:latest'.format(self.username))
        if response.returncode:
            self.send_msg('jumpscaleX installed Successfully, but could not push')
        else:
            self.send_msg('jumpscaleX installed and pushed Successfully')

    def image_pull(self, file_link):
        """Pull image from docker hub in case of fail to build one.

        :param file_link: result file link .
        :type file_link: str
        """
        response = self.execute_cmd('docker login --username={} --password={}'.format(self.username, self.password))
        if not response:
            self.send_msg('Failed to install jumpscaleX {} and could not login'.format(file_link))

        response = self.execute_cmd('docker pull {}/jumpscalex:latest'.format(self.username))
        if response.returncode:
            self.send_msg('Failed to install jumpscaleX {} and could not pull'.format(file_link))
        else:
            self.send_msg('Failed to install jumpscaleX {} and pulled Successfully'.format(file_link))


if __name__ == "__main__":
    build = BuildImage()
    image_name = '{}/jumpscalex'.format(build.username)
    build.images_clean(image_name=image_name)
    response = build.image_bulid(image_name=image_name, branch='development')
    if response.returncode:
        file_name = '{}.log'.format(str(datetime.now())[:10])
        build.write_file(text=response.stdout, file_name=file_name)
        build.images_clean()
        file_link = '{}/{}'.format(build.serverip, file_name)
        build.image_pull(file_link)
        sys.exit()
    else:
        build.image_push()
