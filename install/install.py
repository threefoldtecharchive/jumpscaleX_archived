from importlib import util
import os
import subprocess
import sys

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


insystem = input("\nDo you want to install in the system or using the sandbox?, default is the sandbox, if 1 or Y will be in system : ")
if str(insystem).lower().strip() in ["1","y"]:
    IT.MyEnv.config["INSYSTEM"]=True
    if IT.Tools.ask_yes_no("\nDo you want to redo the full install? (means redo pip's ...)"):
        IT.Tools.delete(IT.MyEnv.state_file_path)
        IT.MyEnv.state_load()
else:
    IT.MyEnv.config["INSYSTEM"]=False

if not IT.MyEnv.sshagent_active_check():
    print ("\nDID NOT FIND KEY IN SSH-AGENT, is it ok to continue without?")
    print("It's recommended to have a SSH key as used on github loaded in your ssh-agent")
    print("If you don't have an ssh key it will not be possible to modify jumpscale code.")

print("\n\n - Will install jumpscale in /sandbox")
if IT.MyEnv.config["INSYSTEM"]:
    print (" - jumpscale will be installed in the system")
else:
    print (" - jumpscale will be installed as sandbox")
print("")

if not IT.Tools.ask_yes_no("Is it ok to continue, press 1 or Y"):
    sys.exit(1)

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
