from importlib import util
import os
import subprocess
import sys
import inspect

BRANCH = "development"

# get current install.py directory
rootdir = os.path.dirname(os.path.abspath(__file__))

path = os.path.join(rootdir, "InstallTools.py")

if not os.path.exists(path):
    cmd = "cd %s;rm -f InstallTools.py;curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/master/install/InstallTools.py?$RANDOM > InstallTools.py" % rootdir
    subprocess.call(cmd, shell=True)

spec = util.spec_from_file_location("IT", path)
IT = spec.loader.load_module()

def dexec(cmd):
    cmd2 = "docker exec -ti %s bash -c '%s'"%(args["name"],cmd)
    IT.Tools.execute(cmd2,interactive=True,showout=False,replace=False,asfile=True)

def sshexec(cmd):
    cmd2 = "ssh -t root@localhost -A -p %s '%s'"%(args["port"],cmd)
    IT.Tools.execute(cmd2,interactive=True,showout=False,replace=False,asfile=True)

def docker_names():
    names = IT.Tools.execute("docker container ls -a --format='{{json .Names}}'",showout=False,replace=False)[1].split("\n")
    names = [i.strip("\"'") for i in names if i.strip()!=""]
    return names

def image_names():
    names = IT.Tools.execute("docker images --format='{{.Repository}}:{{.Tag}}'",showout=False,replace=False)[1].split("\n")
    names = [i.strip("\"'") for i in names if i.strip()!=""]
    return names

# FOR DEBUG purposes can install ipython & pip3 will allow us to use the shell
# IT.UbuntuInstall.base_install()

def help():
    T="""
    Jumpscale X Installer
    ---------------------

    options

    # type of installation
    -1 = in system install
    -2 = sandbox install
    -3 = install in a docker (make sure docker is installed)

    -y = answer yes on every question (for unattended installs)
    -c = will confirm all filled in questions at the end (useful when using -y)
    -d = if set will delete e.g. container if it exists (d=delete), otherwise will just use it if container install

    -r = reinstall, basically means will try to re-do everything without removing (keep data)

    -p = pull code from git, if not specified will only pull if code directory does not exist yet

    -w = install the wiki at the end, which includes openresty, lapis, lua, ...

    --name = name of docker, only relevant when docker option used

    --codepath = "/sandbox/code" can overrule, is where the github code will be checked out

    --portrange = 1 is the default means 8000-8099 on host gets mapped to 8000-8099 in docker
                  1 means 8100-8199 on host gets mapped to 8000-8099 in docker
                  2 means 8200-8299 on host gets mapped to 8000-8099 in docker

    --image=/path/to/image.tar or name of image (use docker images)
                  ...
    --port = port of container SSH std is 9022 (normally not needed to use because is in portrange:22 e.g. 9122 if portrange 1)

    -h = this help

    """
    print(IT.Tools.text_replace(T))
    sys.exit(0)


def ui():

    args= IT.Tools.cmd_args_get()

    if "h" in args:
        help()


    if "incontainer" not in args:

        rc,out,err=IT.Tools.execute("cat /proc/1/cgroup",die=False,showout=False)
        if rc==0 and out.find("/docker/")!=-1:
            args["incontainer"]=True
            #means we are in a docker
        else:
            args["incontainer"]=False

    if not "1" in args and not "2" in args and not "3" in args:

        if "incontainer" in args:
            #means we are inside a container
            T="""
            Installer choice for jumpscale in the docker
            --------------------------------------------

            Do you want to install
             - in system (development)                : 1
             - using a sandbox                        : 2

            """

            mychoice = int(IT.Tools.ask_choices(T,[1,2]))

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
        args[str(mychoice)]=True

    #means interactive

    if not args["incontainer"]:
        if not IT.MyEnv.sshagent_active_check():
            T="""
            Did not find an SSH key in ssh-agent, is it ok to continue without?
            It's recommended to have a SSH key as used on github loaded in your ssh-agent
            If the SSH key is not found, repositories will be cloned using https
            """
            print("Could not continue, load ssh key.")
            sys.exit(1)
        else:
            sshkey = IT.MyEnv.sshagent_key_get()
            sshkey+=".pub"
            if not IT.Tools.exists(sshkey):
                print ("ERROR: could not find SSH key:%s"%sshkey)
                sys.exit(1)
            sshkey2 = IT.Tools.file_text_read(sshkey)

        args["sshkey"]=sshkey2

    if not "codepath" in args:
        if IT.Tools.exists("/sandbox/code"):
            codepath = "/sandbox/code"
        else:
            codepath = "~/code"
        codepath=codepath.replace("~",IT.MyEnv.config["DIR_HOME"])
        args["codepath"] = codepath

    if "y" not in args and "r" not in args and IT.Tools.exists(IT.MyEnv.state_file_path):
        if IT.Tools.ask_yes_no("\nDo you want to redo the full install? (means redo pip's ...)"):
            args["r"]=True


    if "3" in args: #means we want docker

        if "name" not in args:
            args["name"] = "default"

        container_exists = args["name"] in docker_names()
        args["container_exists"]=container_exists

        if "name" not in args:
            dockername = IT.Tools.ask_string("What name do you want to use for your docker (default jsx): ",default="jsx")
            if dockername == "":
                dockername = "jsx"
            args["name"] = dockername

        if container_exists:
            if "d" not in args:
                if not "y" in args:
                    if IT.Tools.ask_yes_no("docker:%s exists, ok to remove? Will otherwise keep and install inside."%args["name"]):
                        args["d"]=True
                # else:
                #     #is not interactive and d was not given, so should not continue
                #     print("ERROR: cannot continue, docker: %s exists."%args["name"])
                #     sys.exit(1)

        if "image" in args:
            if ":" not in args["image"]:
                args["image"]="%s:latest"%args["image"]
            if args["image"] not in image_names():
                if IT.Tools.exists(args["image"]):
                    IT.Tools.shell()
                    w
                else:
                    print("Cannot continue, image '%s' specified does not exist."%args["image"])
                    sys.exit(1)
            args["d"]=True

        if "portrange" not in args:
            if "y" in args:
                args["portrange"] = 0
            else:
                if container_exists:
                    args["portrange"] = int(IT.Tools.ask_choices("choose portrange, std = 0",[0,1,2,3,4,5,6,7,8,9]))
                else:
                    args["portrange"] = 0

        a=8000+int(args["portrange"])*100
        b=8099+int(args["portrange"])*100
        portrange_txt="%s-%s:8000-8099"%(a,b)
        args["portrange_txt"] = "-p %s"%portrange_txt

        if "port" not in args:
            args["port"] = 9000+int(args["portrange"])*100 + 22

    else:
        if "p" not in args:
            #is not docker and not pull yet
            if "y" not in args:
                #not interactive ask
                if IT.Tools.ask_yes_no("Do you want to pull code changes from git?"):
                    args["p"]=True
            else:
                #default is not pull
                args["p"]=False

    if "y" not in args and "w" not in args:
        if IT.Tools.ask_yes_no("Do you want to install lua/nginx/openresty & wiki environment?"):
            args["w"]=True


    T="""

    Jumpscale X Installer
    ---------------------

    """
    T=IT.Tools.text_replace(T)


    if "3" in args:
        T+=" - jumpscale will be installed using docker.\n"
    elif "1" in args:
         T+=" - jumpscale will be installed in the system.\n"
    elif "2" in args:
         T+=" - jumpscale will be installed using sandbox.\n"
    if not "incontainer" in args and sshkey2:
        T+= " - sshkey used will be: %s\n"%sshkey

    T+=" - location of code path is: %s\n"%args["codepath"]
    if "w" in args:
        T+=" - will install wiki system at end\n"
    if "3" in args:
        T+=" - name of container is: %s\n"%args["name"]
        if container_exists:
            if "d" in args:
                T+=" - will remove the docker, and recreate\n"
            else:
                T+=" - will keep the docker container and install inside\n"

        if "image" in args:
            T+=" - will use docker image: '%s'\n"%args["image"]

        T+=" - will map ssh port to: '%s'\n"%args["port"]
        T+=" - will map portrange '%s' (8000-8100) always in container.\n"% portrange_txt

    T+="\n"
    print(T)

    if "c" in args or "y" not in args:
        if not IT.Tools.ask_yes_no("Ok to continue?"):
            sys.exit(1)

    return args

args = ui()

if "r" in args:
    #remove the state
    IT.Tools.delete(IT.MyEnv.state_file_path)
    IT.MyEnv.state_load()

if "p" in args:
    os.environ["GITPULL"] = "%s"%(args["p"])
else:
    os.environ["GITPULL"] = "0"



IT.Tools.dir_ensure(args["codepath"])

if "1" in args:
    IT.MyEnv.config["INSYSTEM"] = True
    IT.Tools.execute("rm -f /sandbox/bin/pyth*")

elif "2" in args:
    #is sandbox (2)
    IT.MyEnv.config["INSYSTEM"] = False


if "1" in args or "2" in args:
    IT.MyEnv.init()
    installer = IT.JumpscaleInstaller()
    installer.install()

    if "w" in args:
        if "1" in args:
            #in system need to install the lua env
            IT.Tools.execute("source /sandbox/env.sh;js_shell 'j.builder.runtimes.lua.install()'")
        IT.Tools.execute("source /sandbox/env.sh;js_shell 'j.tools.markdowndocs.test()'", showout=False)


elif "3" in args:

    if args["container_exists"] and "d" in args:
        IT.Tools.execute("docker rm -f %s"%args["name"])
        args["container_exists"] = False

    cmd="""

    docker run --name {NAME} \
    --hostname {NAME} \
    -d \
    -p {PORT}:22 {PORTRANGE} \
    --device=/dev/net/tun \
    --cap-add=NET_ADMIN --cap-add=SYS_ADMIN \
    --cap-add=DAC_OVERRIDE --cap-add=DAC_READ_SEARCH \
    -v {CODEDIR}:/sandbox/code {IMAGE}
    """
    print(" - Docker machine gets created: ")
    if "image" not in args:
        args["image"] = "phusion/baseimage:master"
    if not args["container_exists"]:
        if "port" not in args:
            args["port"]=8022
        IT.Tools.execute(cmd,args={"CODEDIR":args["codepath"],
                                   "NAME":args["name"],
                                   "PORT":args["port"],
                                   "PORTRANGE":args["portrange_txt"],
                                   "IMAGE":args["image"]
                                   },
                         interactive=True)

        print(" - Docker machine OK")
        print(" - Start SSH server")
    else:
        print(" - Docker machine was already there.")

    if "sshkey" in args:
        dexec('echo "%s" > /root/.ssh/authorized_keys'%args["sshkey"])

    dexec("/usr/bin/ssh-keygen -A")
    dexec('/etc/init.d/ssh start')
    dexec('rm -f /etc/service/sshd/down')
    print(" - Upgrade ubuntu")
    dexec('apt update; apt upgrade -y; apt install mc git -y')

    IT.Tools.execute("rm -f ~/.ssh/known_hosts")  #rather dirty hack

    # if "2" in args:
    #     args_txt = "-2"
    # else:
    #for now only support for insystem
    args_txt = "-1"
    for item in ["y","r","p","w"]:
        if item in args:
            args_txt+=" -%s"%item
    if "codepath" in args:
        args_txt+=" --codepath=%s"%args["codepath"]

    cmd = "python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py %s"%args_txt

    dexec(cmd)



    # dirpath = os.path.dirname(inspect.getfile(IT))
    #
    # for item in ["install.py","InstallTools.py"]:
    #     src1 = "%s/%s"%(dirpath,item)
    #     cmd = "scp -P %s %s root@localhost:/tmp/" %(args["port"],src1)
    #     IT.Tools.execute(cmd)
    # cmd = "cd /tmp;python3 install.py -1 -y"

    k = """

    install succesfull:

    # to login to the docker using ssh use (if std port)
    ssh root@localhost -A -p {port}
    """
    #
    # # or for kosmos shell
    # ssh root@localhost -A -p {port} 'source /sandbox/env.sh;kosmos'
    #
    # """
    print(IT.Tools.text_replace(k,args=args))


"""
#TO TEST:
python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py
"""


"""
#env arguments

export INSYSTEM=1

export GITMESSAGE=

"""
