from utils import Utils
from datetime import datetime
import sys


class BuildImage(Utils):

    def build_image(self):
        cmd = 'docker build --force-rm -t jumpscalex /sandbox/code/github/threefoldtech/jumpscaleX/scripts'
        response = self.execute_cmd(cmd)
        if response.returncode:
            file_name = '{}.log'.format(str(datetime.now())[:10])
            file_link = self.write_file(response.stdout, file_name=file_name)
            self.send_msg('Failed to install jumpscaleX ' + file_link, push=False)
            self.images_clean()
            sys.exit()
        else:
            self.send_msg('jumpscaleX installed Successfully', push=False)

    def images_clean(self):
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
        images_name = response.stdout.split()
        response = self.execute_cmd('docker images | tail -n+2 | awk "{print \$3}"')
        images_id = response.stdout.split()
        for i in range(0, len(images_id)):
            if images_name[i] == '<none>':
                response = self.execute_cmd('docker rmi -f {}'.format(images_id[i]))
                if response.returncode:
                    self.send_msg('Failed to remove old image', push=False)


if __name__ == "__main__":
    build = BuildImage()
    build.build_image()
    build.images_clean()
