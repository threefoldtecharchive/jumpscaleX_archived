from importlib import util
import os
import subprocess
import sys
import inspect

BRANCH = "master"
SANDBOX = "/sandbox"

# get current install.py directory
rootdir = os.path.dirname(os.path.abspath(__file__))

path = os.path.join(rootdir, "InstallTools.py")

if not os.path.exists(path):
    cmd = "cd %s;rm -f InstallTools.py;curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/%s/install/InstallTools.py?$RANDOM > InstallTools.py" % (rootdir, BRANCH)
    subprocess.call(cmd, shell=True)

spec = util.spec_from_file_location("IT", path)
IT = spec.loader.load_module()

sys.excepthook = IT.my_excepthook

args={}

def help():
    T="""
    3bot development environment based on docker
    --------------------------------------------

    -h = this help

    commands:
        install             : get docker & install 3bot
        export $file        : export the container
        import $file        : import the container & start
        stop                : stop the container
        kosmos              : is the kosmos shell (JSX shell)
        bash                : is the bash shell inside the container

    e.g. python3 3bot_dev.py install -d -y -c

    install options
    ---------------

    -y = answer yes on every question (for unattended installs)
    -c = will confirm all filled in questions at the end (useful when using -y)
    -s = from scratch, means will start from empty ubuntu and re-install everything
    -r = reinstall, basically means will try to re-do everything without removing the data
    -d = if set will delete the docker container if it already exists

    --debug will launch the debugger if something goes wrong

    ## encryption

    --secret = std is '1234', if you use 'SSH' then a secret will be derived from the SSH-Agent (only if only 1 ssh key loaded
    --private_key = std is '' otherwise is 24 words, use '' around the private key
                if secret specified and private_key not then will ask in -y mode will autogenerate

    ## code related

    --codepath = is where the github code will be checked out, default /sandbox/code if it exists otherwise ~/code
    --pull = pull code from git, if not specified will only pull if code directory does not exist yet
    --branch = jumpscale branch: normally 'master' or 'development' for unstable release

    """
    print(IT.Tools.text_replace(T))
    sys.exit(0)

args= IT.Tools.cmd_args_get()

if not "codepath" in args:
    args["codepath"] = None

if not "branch" in args:
    args["branch"]=BRANCH

if "name" not in args:
    args["name"] = "3bot"

if "sshkey" not in args:
    args["sshkey"] = None

if "h" in args or args=={}:
    help()

IT.MyEnv.init(basedir=None,config={},readonly=True,codepath=args["codepath"])

def install_ui(args):

    if "o" in args:
        args["image"] = "despiegk/3bot"

    if not IT.MyEnv.sshagent_active_check():
        T="""
        Did not find an SSH key in ssh-agent, is it ok to continue without?
        It's recommended to have a SSH key as used on github loaded in your ssh-agent
        If the SSH key is not found, repositories will be cloned using https

        if you never used an ssh-agent or github, just say "y"

        """
        if "y" not in args:
            if not IT.Tools.ask_yes_no("OK to continue?"):
                sys.exit(1)

    if "y" not in args and "r" not in args:
        if IT.Tools.ask_yes_no("\nDo you want to redo the full install? (means redo pip's ...)"):
            args["r"]=True

        if args["name"] in docker.docker_names():
            if "d" not in args:
                if not "y" in args:
                    if IT.Tools.ask_yes_no("docker:%s exists, ok to remove? Will otherwise keep and install inside."%args["name"]):
                        args["d"]=True


    if "image" in args:
        if "d" not in args:
            #because if we specify image we want to delete the running docker
            args["d"]=True
        if ":" not in args["image"]:
            args["image"]="%s:latest" % args["image"]
        if args["image"] not in docker.image_names():
            if IT.Tools.exists(args["image"]):
                IT.Tools.shell()
            else:
                print("Cannot continue, image '%s' specified does not exist."%args["image"])
                sys.exit(1)

    if "pull" not in args:
        if "y" not in args:
            #not interactive ask
            if IT.Tools.ask_yes_no("Do you want to pull code changes from git?"):
                args["pull"]=True
        else:
            #default is not pull
            args["pull"]=False

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

    # if "y" not in args and "w" not in args:
    #     if IT.Tools.ask_yes_no("Do you want to install lua/nginx/openresty & wiki environment?"):
    #         args["w"]=True


    T="""

    Jumpscale X Installer
    ---------------------

    """
    T=IT.Tools.text_replace(T)

    if IT.MyEnv.sshagent_active_check():
        T+= " - sshkey used will be: %s\n"%IT.MyEnv.sshagent_key_get()

    T+=" - location of code path is: %s\n"%args["codepath"]
    if "w" in args:
        T+=" - will install wiki system at end\n"
    if "3" in args:
        T+=" - name of container is: %s\n"%args["name"]
        if args["container_exists"]:
            if "d" in args:
                T+=" - will remove the docker, and recreate\n"
            else:
                T+=" - will keep the docker container and install inside\n"

        if "image" in args:
            T+=" - will use docker image: '%s'\n"%args["image"]

        portrange = args["portrange"]

        a=8000+int(portrange)*10
        b=8004+int(portrange)*10
        portrange_txt="%s-%s:8000-8004"%(a,b)
        port = 9000+int(portrange)*100 + 22

        T+=" - will map ssh port to: '%s'\n"%port
        T+=" - will map portrange '%s' (8000-8004) always in container.\n"% portrange_txt

    if "debug" in args:
        IT.MyEnv.debug = True
        T+=" - runs in debug mode (means will use debugger when error).\n"

    T+="\n"
    print(T)

    if "c" in args or "y" not in args:
        if not IT.Tools.ask_yes_no("Ok to continue?"):
            sys.exit(1)

    return args

if "portrange" not in args:
    args["portrange"]=1

if "install" in args:
    args = install_ui(args)

delete = "d" in args
docker=IT.Docker(name="3bot",delete=delete, portrange=args["portrange"],sshkey=args["sshkey"])

if "install" in args:
    docker.jumpscale_install(secret=args["secret"],private_key=args["private_key"])

elif "stop" in args:
    if args["name"] in docker_running():
        IT.Tools.execute("docker stop %s"% args["name"])
else:
    print (help())

