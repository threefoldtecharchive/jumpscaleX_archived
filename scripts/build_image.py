from utils import Utils
import sys


class BuildImage(Utils):

    def build_image(self):
        cmd = 'docker build --force-rm -t jumpscaleX /sandbox/code/github/threefoldtech/jumpscaleX/scripts'
        response = self.execute_cmd(cmd)
        if response.returncode:
            file_link = self.write_file(response.stdout)
            self.send_msg('Failed to install jumpscaleX ' + file_link, push=False)
            self.images_clean()
            sys.exit()

    def images_clean(self):
        response = self.execute_cmd('docker rmi -f jumpscale')
        if response.returncode:
            self.send_msg('Failed to remove old image', push=False)
        return response


if __name__ == "__main__":
    build = BuildImage()
    build.build_image()
    build.images_clean()
