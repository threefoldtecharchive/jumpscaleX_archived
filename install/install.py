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

def dexec(cmd):
    cmd2 = "docker exec -ti %s bash -c '%s'"%(dockername,cmd)
    IT.Tools.execute(cmd2,interactive=True,showout=False,replace=False,asfile=True)

def sshexec(cmd):
    cmd2 = "ssh -t root@localhost -A -p 2224 '%s'"%cmd
    IT.Tools.execute(cmd2,interactive=True,showout=False,replace=False,asfile=True)

# FOR DEBUG purposes can install ipython & pip3 will allow us to use the shell
# IT.UbuntuInstall.base_install()

if len(sys.argv)>1:
    mychoice = int(sys.argv[-1])
else:

    T="""
    Installer choice for jumpscale
    ------------------------------

    Do you want to install
     - insystem         (ideal for development only in OSX & Ubuntu1804)        : 1
     - using a sandbox  (only in OSX & Ubuntu1804)                              : 2
     - using docker?                                                            : 3

    """

    mychoice = int(IT.Tools.ask_choices(T,[1,2,3]))

if mychoice<4:

    if not IT.MyEnv.sshagent_active_check():
        T="""
        Did not find an SSH key in ssh-agent, is it ok to continue without?
        It's recommended to have a SSH key as used on github loaded in your ssh-agent
        If you don't have an ssh key it will not be possible to modify code, code will be checked out statically.
        """
        if not IT.Tools.ask_yes_no(T, default="y"):
            print("Could not continue, load ssh key.")
            sys.exit(1)
        else:
            sshkey2 = ""
    else:
        sshkey = IT.MyEnv.sshagent_key_get()
        sshkey+=".pub"
        if not IT.Tools.exists(sshkey):
            print ("ERROR: could not find SSH key:%s"%sshkey)
            sys.exit(1)
        sshkey2 = IT.Tools.file_text_read(sshkey)
else:
    sshkey2 = ""


if mychoice == 3:
    dockername = IT.Tools.ask_string("What name do you want to use for your docker (default jsx): ",default="jsx")
    if dockername == "":
        dockername = "jsx"
    if IT.Tools.exists("/sandbox/code"):
        codepath = "/sandbox/code"
    else:
        codepath = "~/code"
    if not IT.Tools.ask_yes_no("We will install code in %s, is this ok?"%codepath):
        codepath = IT.Tools.ask_string("give path to the root of your code directory")
    codepath=codepath.replace("~",IT.MyEnv.config["DIR_HOME"])
    IT.Tools.dir_ensure(codepath)
    print("\n - jumpscale will be installed using docker")
    print(" - location of code path is: %s"%codepath)

elif mychoice == 1:
    IT.MyEnv.config["INSYSTEM"] = True
    IT.Tools.execute("rm -f /sandbox/bin/pyth*")
    if IT.Tools.exists(IT.MyEnv.state_file_path):
        if IT.Tools.ask_yes_no("\nDo you want to redo the full install? (means redo pip's ...)"):
            IT.Tools.delete(IT.MyEnv.state_file_path)
            IT.MyEnv.state_load()
    print("\n - jumpscale will be installed in the system")
elif mychoice == 4:
    if IT.Tools.ask_yes_no("Do you want to pull code changes from git?"):
        os.environ["GITPULL"] = "1"
    else:
        os.environ["GITPULL"] = "0"
    IT.MyEnv.config["INSYSTEM"] = True
else:
    #is sandbox (2)
    IT.MyEnv.config["INSYSTEM"] = False
    print("\n - Will install jumpscale in /sandbox")

if sshkey2:
    print(" - sshkey used will be: %s"%sshkey)




if mychoice<4:
    if not IT.Tools.ask_yes_no("Is it ok to continue (y)"):
        sys.exit(1)

if mychoice in [1,2,4,5]:
    installer = IT.JumpscaleInstaller()

    installer.install()
elif mychoice in [3]:


    def docker_names():
        names = IT.Tools.execute("docker container ls --format='{{json .Names}}'",showout=False,replace=False)[1].split("\n")
        names = [i.strip("\"'") for i in names if i.strip()!=""]
        return names
    exists=False
    if dockername in docker_names():
        if IT.Tools.ask_yes_no("docker:%s exists, ok to remove?"%dockername):
            IT.Tools.execute("docker rm -f %s"%dockername)
        else:
            exists = True

    cmd="""

    docker run --name {NAME} \
    --hostname jsx \
    -d \
    -p 2224:22 -p 6830-6850:6830-6850 \
    --device=/dev/net/tun \
    --cap-add=NET_ADMIN --cap-add=SYS_ADMIN \
    --cap-add=DAC_OVERRIDE --cap-add=DAC_READ_SEARCH \
    -v {CODEDIR}:/sandbox/code phusion/baseimage:master
    """
    print(" - Docker machine gets created: ")
    if exists is False:
        IT.Tools.execute(cmd,args={"CODEDIR":codepath,"NAME":dockername},interactive=True)

    print(" - Docker machine OK")
    print(" - Start SSH server")
    if sshkey:
        dexec('echo "%s" > /root/.ssh/authorized_keys'%sshkey2)
    dexec("/usr/bin/ssh-keygen -A")
    dexec('/etc/init.d/ssh start')
    dexec('rm -f /etc/service/sshd/down')
    print(" - Upgrade ubuntu")
    dexec('apt update; apt upgrade -y; apt install mc git -y')

    IT.Tools.execute("rm -f ~/.ssh/known_hosts")  #rather dirty hack

    T="""
    Installer choice for jumpscale in the docker
    --------------------------------------------

    Do you want to install
     - in system (development)                : 4
     - using a sandbox                        : 5

    """

    mychoice2 = int(IT.Tools.ask_choices(T,[4,5]))

    sshexec('curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development_kosmos/install/install.py?$RANDOM > /tmp/install.py;python3 /tmp/install.py %s'%mychoice2)

    if mychoice2 == 4:
        if IT.Tools.ask_yes_no("Do you want to install lua/nginx/openresty & wiki environment?"):
            IT.Tools.execute("js_shell 'j.builder.runtimes.lua.install()'")
            IT.Tools.shell()
    elif mychoice2 == 3:
        if IT.Tools.ask_yes_no("Do you want to install wiki environment?"):
            IT.Tools.shell()

    k = """

    install succesfull:

    # to login to the docker using ssh use:
    ssh root@localhost -A -p 2224

    # or for kosmos shell
    ssh root@localhost -A -p 2224 'source /sandbox/env.sh;kosmos'

    """
    print(IT.Tools.text_replace(k))



else:
    print ("choice:'%s' not supported."%mychoice)
    sys.exit(1)


"""
#TO TEST:
python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py
"""


"""
#env arguments

export INSYSTEM=1

export GITMESSAGE=

"""
