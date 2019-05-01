from importlib import util
import os
import subprocess
import sys

BRANCH = "master"
SANDBOX = "~/3bot"

# get current install.py directory
rootdir = os.path.dirname(os.path.abspath(__file__))

path = os.path.join(rootdir, "InstallTools.py")

if not os.path.exists(path):
    cmd = "cd %s;rm -f InstallTools.py;curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/%s/install/InstallTools.py?$RANDOM > InstallTools.py" % (rootdir, BRANCH)
    subprocess.call(cmd, shell=True)

spec = util.spec_from_file_location("IT", path)
IT = spec.loader.load_module()

IT.MyEnv._init()

sys.excepthook = IT.my_excepthook

args={}

def dexec(cmd,interactive=False):
    if "'" in cmd:
        cmd = cmd.replace("'","\"")
    if interactive:
        cmd2 = "docker exec -ti %s bash -c '%s'"%(args["name"],cmd)
    else:
        cmd2 = "docker exec -t %s bash -c '%s'"%(args["name"],cmd)
    IT.Tools.execute( cmd2, interactive=interactive,showout=True,replace=False,asfile=True)

def sshexec(cmd):
    if "'" in cmd:
        cmd = cmd.replace("'","\"")
    cmd2 = "ssh -oStrictHostKeyChecking=no -t root@localhost -A -p %s '%s'"%(args["port"],cmd)
    IT.Tools.execute(cmd2,interactive=True,showout=False,replace=False,asfile=True)



def docker_running():
    names = IT.Tools.execute("docker ps --format='{{json .Names}}'",showout=False,replace=False)[1].split("\n")
    names = [i.strip("\"'") for i in names if i.strip()!=""]
    return names



def docker_names():
    names = IT.Tools.execute("docker container ls -a --format='{{json .Names}}'",showout=False,replace=False)[1].split("\n")
    names = [i.strip("\"'") for i in names if i.strip()!=""]
    return names

def image_names():
    names = IT.Tools.execute("docker images --format='{{.Repository}}:{{.Tag}}'",showout=False,replace=False)[1].split("\n")
    names = [i.strip("\"'") for i in names if i.strip()!=""]
    return names


def help():
    T="""
    3bot development environment based on docker
    --------------------------------------------

    # options

    -h = this help
    -y = answer yes on every question (for unattended installs)
    -c = will confirm all filled in questions at the end (useful when using -y)
    -r = reinstall, basically means will try to re-do everything without removing the data
    -d = if set will delete e.g. container if it exists (d=delete), otherwise will just use it if container install    

    --debug will launch the debugger if something goes wrong

    ## encryption

    --secret = std is '1234', if you use 'SSH' then a secret will be derived from the SSH-Agent (only if only 1 ssh key loaded
    --private_key = std is '' otherwise is 24 words, use '' around the private key
                if secret specified and private_key not then will ask in -y mode will autogenerate

    ## code related

    --codepath = "~/code" can overrule, is where the github code will be checked out
    -p = pull code from git, if not specified will only pull if code directory does not exist yet
    --branch = jumpscale branch: normally 'master' or 'development' for unstable release


    """
    print(IT.Tools.text_replace(T))
    sys.exit(0)


def ui():

    args= IT.Tools.cmd_args_get()

    if "h" in args:
        help()


    rc,out,_=IT.Tools.execute("cat /proc/1/cgroup",die=False,showout=False)
    if rc==0 and out.find("/docker/")!=-1:
        args["incontainer"]=True
        mychoice = 1
        #means we are in a docker
    else:
        args["incontainer"]=False
        mychoice = 3
        
    args[str(mychoice)]=True


    if not args["incontainer"]:
        if not IT.MyEnv.sshagent_active_check():
            T="""
            Did not find an SSH key in ssh-agent, is it ok to continue without?
            It's recommended to have a SSH key as used on github loaded in your ssh-agent
            If the SSH key is not found, repositories will be cloned using https

            if you never used an ssh-agent or github, just say "y"

            """
            print("Could not continue, load ssh key in ssh-agent and try again.")
            if "3" in args:
                sys.exit(1)
            if "y" not in args:
                if not IT.Tools.ask_yes_no("OK to continue?"):
                    sys.exit(1)
        else:
            sshkey2 = IT.Tools.execute("ssh-add -L",die=False,showout=False)[1].strip().split(" ")[-2].strip()
            args["sshkey"]=sshkey2

    if not "codepath" in args:
        codepath = "%s/code"%SANDBOX
        if "1" in args or "2" in args or IT.Tools.exists("/sandbox"):
            codepath = "%s/code"%SANDBOX
        else:
            codepath = "~/code"
        codepath=codepath.replace("~",IT.MyEnv.config["DIR_HOME"])
        args["codepath"] = codepath

    if not "branch" in args:
        args["branch"]="master"

    if "y" not in args and "r" not in args and IT.MyEnv.installer_only is False and IT.Tools.exists(IT.MyEnv.state_file_path):
        if IT.Tools.ask_yes_no("\nDo you want to redo the full install? (means redo pip's ...)"):
            args["r"]=True


    if "3" in args: #means we want docker
        if "name" not in args:
            args["name"] = "3bot"

        if IT.MyEnv.platform()=="linux" and not IT.Tools.cmd_installed("docker"):
            IT.UbuntuInstall.docker_install()

        container_exists = args["name"] in docker_names()
        args["container_exists"]=container_exists

        if container_exists:
            if "d" not in args:
                if not "y" in args:
                    if IT.Tools.ask_yes_no("docker:%s exists, ok to remove? Will otherwise keep and install inside."%args["name"]):
                        args["d"]=True
                else:
                    #is not interactive and d was not given, so should not continue
                    print("ERROR: cannot continue, docker: %s exists."%args["name"])
                    sys.exit(1)

        if "image" in args:
            if "d" not in args:
                args["d"]=True
            if args["image"] == "hub":
                args["image"] = "despiegk/jsx_develop"
            if ":" not in args["image"]:
                args["image"]="%s:latest" % args["image"]
            if args["image"] not in image_names():
                if IT.Tools.exists(args["image"]):
                    IT.Tools.shell()
                else:
                    print("Cannot continue, image '%s' specified does not exist."%args["image"])
                    sys.exit(1)


        if "portrange" not in args:
            if "y" in args:
                args["portrange"] = 1
            else:
                if container_exists:
                    args["portrange"] = int(IT.Tools.ask_choices("choose portrange, std = 1",[1,2,3,4,5,6,7,8,9]))
                else:
                    args["portrange"] = 1

        a=8000+int(args["portrange"])*10
        b=8004+int(args["portrange"])*10
        portrange_txt="%s-%s:8000-8004"%(a,b)
        portrange_txt +=" -p %s:9999/udp"%(a+9)  #udp port for wireguard

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

    if "y" in args:

        if "secret" not in args:
            if  IT.MyEnv.sshagent_active_check():
                args["secret"] = "SSH"
            else:
                args["secret"] = "1234"
        if "private_key" not in args:
            args["private_key"] = ""
    else:
        if "secret" not in args:
            if  IT.MyEnv.sshagent_active_check():
                args["secret"] = IT.Tools.ask_string("Optional: provide secret to use for passphrase, if ok to use SSH-Agent just press 'ENTER'",default="SSH")
            else:
                args["secret"] = IT.Tools.ask_string("please provide secret passphrase for the BCDB.",default="1234")
        if "private_key" not in args:
            args["private_key"] = IT.Tools.ask_string("please provide 24 words of the private key, or just press 'ENTER' for autogeneration.")


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
        T+= " - sshkey used will be: %s\n"%sshkey2

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

    if "debug" in args:
        IT.MyEnv.debug = True
        T+=" - runs in debug mode (means will use debugger when error).\n"

    T+="\n"
    print(T)

    if "c" in args or "y" not in args:
        if not IT.Tools.ask_yes_no("Ok to continue?"):
            sys.exit(1)

    return args



args = ui()
if "r" in args and IT.MyEnv.installer_only is False:
    #remove the state
    IT.Tools.delete(IT.MyEnv.state_file_path)
    IT.MyEnv.state_load()

if "p" in args:
    os.environ["GITPULL"] = "%s"%(args["p"])
else:
    os.environ["GITPULL"] = "0"

if "1" in args or "2" in args:
    # Only install on supported platforms
    IT.MyEnv.check_platform()
    IT.MyEnv._init(install=True)

if "1" in args:
    IT.MyEnv.config["INSYSTEM"] = True
    IT.Tools.execute("rm -f /sandbox/bin/pyth*")

elif "2" in args:
    #is sandbox (2)
    IT.MyEnv.config["INSYSTEM"] = False

    if "darwin" in IT.MyEnv.platform():
        print("sandbox node for darwin not yet supported.")
        sys.exit(1)


if "1" in args or "2" in args:

    IT.MyEnv.installer_only = False #need to make sure we will install
    installer = IT.JumpscaleInstaller()
    installer.install(branch=args["branch"],secret=args["secret"],private_key_words=args["private_key"])

    if "w" in args:
        if "1" in args:

            #in system need to install the lua env
            IT.Tools.execute("source /sandbox/env.sh;kosmos 'j.builder.runtimes.lua.install(reset=True)'", showout=False)
        IT.Tools.execute("source /sandbox/env.sh;js_shell 'j.tools.markdowndocs.test()'", showout=False)
        print("Jumpscale X installed successfully")

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
        if "default" not in docker_running():
            IT.Tools.execute("docker start %s"% args["name"])
            if not "default" in docker_running():
                print("could not start container:%s"%args["name"])
                sys.exit(1)
            IT.Tools.shell()

    SSHKEYS = IT.Tools.execute("ssh-add -L",die=False,showout=False)[1]
    if SSHKEYS.strip()!="":
        dexec('echo "%s" > /root/.ssh/authorized_keys'%SSHKEYS)

    dexec("/usr/bin/ssh-keygen -A")
    dexec('/etc/init.d/ssh start')
    dexec('rm -f /etc/service/sshd/down')
    print(" - Upgrade ubuntu")
    dexec('apt update; apt upgrade -y; apt install mc git -y')

    IT.Tools.execute("rm -f ~/.ssh/known_hosts")  #rather dirty hack

    #for now only support for insystem
    args_txt = "-1"
    #disabled the wiki part for now
    # for item in ["r","p","w"]:
    for item in ["r","p"]:
        if item in args:
            args_txt+=" -%s"%item
    args_txt+=" -y"
    # args_txt+=" -c"
    for item in ["codepath","secret","private_key","debug"]:
        if item in args:
            args_txt+=" --%s='%s'"%(item,args[item])

    IT.MyEnv.config["DIR_BASE"] = args["codepath"].replace("/code", "")

    # add install from a specific branch
    install = IT.JumpscaleInstaller(branch=args["branch"])

    def getbranch():
        cmd = "cd {}/github/threefoldtech/jumpscaleX; git branch | grep \* | cut -d ' ' -f2".format(args["codepath"])
        _,stdout,_ = IT.Tools.execute(cmd)
        return stdout.strip()

    # check if already code exists and checkout the argument branch
    if os.path.exists("{}/github/threefoldtech/jumpscaleX".format(args["codepath"])):
        if getbranch() != args["branch"]:
            print("found JS on machine, Checking out branch {}...".format(args["branch"])) 
            IT.Tools.execute("""cd {}/github/threefoldtech/jumpscaleX
                        git remote set-branches origin '*'
                        git fetch -v
                        git checkout {} -f
                        git pull""".format(args["codepath"], args["branch"]))

        print("On {} branch".format(args["branch"]))
    else:
        print("no local code at {}".format(args["codepath"]))

    install.repos_get()

    cmd = "python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py %s"%args_txt
    print(" - Installing jumpscaleX ")
    sshexec(cmd)



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
