from importlib import util
import os
import subprocess

print("")
print("    Jumpscale Installer")
print("")

# get current install.py directory
rootdir = os.path.dirname(os.path.abspath(__file__))
# print("- setup root directory: %s" % rootdir)

path = os.path.join(rootdir, "InstallTools.py")

if not os.path.exists(path):
    cmd = "cd %s;rm -f InstallTools.py;curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/master/install/InstallTools.py?$RANDOM > InstallTools.py"%rootdir
    subprocess.call(cmd, shell=True)

spec = util.spec_from_file_location("IT", path)
IT = spec.loader.load_module()

#FOR DEBUG purposes can install ipython & pip3 will allow us to use the shell
# IT.UbuntuInstall.base_install()


installer = IT.JumpscaleInstaller()
installer.install()


"""
#TO TEST:
python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py
"""


"""
#env arguments

export INSYSTEM=1

export GITMESSAGE=

"""
