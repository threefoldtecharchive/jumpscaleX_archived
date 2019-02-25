from utils import Utils
from datetime import datetime
import sys


class BuildImage(Utils):

    def build_image(self):
        cmd = 'docker build --force-rm -t jumpscaleX /sandbox/code/github/threefoldtech/jumpscaleX/scripts'
        response = self.execute_cmd(cmd)
        if response.returncode:
            file_name = str(datetime.now())[:10]
            file_link = self.write_file(response.stdout, file_name=file_name)
            self.send_msg('Failed to install jumpscaleX ' + file_link, push=False)
            self.images_clean()
            sys.exit()
        else:
            self.send_msg('jumpscaleX installed Successfully')

    def images_clean(self):
        response = self.execute_cmd('docker rmi -f jumpscale')
        if response.returncode:
            self.send_msg('Failed to remove old image', push=False)
        return response


if __name__ == "__main__":
    build = BuildImage()
    build.build_image()
    build.images_clean()
