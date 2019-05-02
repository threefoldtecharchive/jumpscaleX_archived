from importlib import util
import os
import subprocess
import sys

BRANCH = "master"

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
    Jumpscale X Installer
    ---------------------

    # options

    -h = this help

    ## type of installation

    -1 = in system install
    -2 = sandbox install
    -3 = install in a docker (make sure docker is installed)
    -w = install the wiki at the end, which includes openresty, lapis, lua, ... (DONT USE YET)


    ## interactivity

    -y = answer yes on every question (for unattended installs)
    -c = will confirm all filled in questions at the end (useful when using -y)
    -r = reinstall, basically means will try to re-do everything without removing (keep data)
    --debug will launch the debugger if something goes wrong

    ## encryption

    --secret = std is '1234', if you use 'SSH' then a secret will be derived from the SSH-Agent (only if only 1 ssh key loaded
    --private_key = std is '' otherwise is 24 words, use '' around the private key
                if secret specified and private_key not then will ask in -y mode will autogenerate

    ## docker related

    --name = name of docker, only relevant when docker option used
    -d = if set will delete e.g. container if it exists (d=delete), otherwise will just use it if container install
    --portrange = 1 is the default
                  1 means 8100-8199 on host gets mapped to 8000-8099 in docker
                  2 means 8200-8299 on host gets mapped to 8000-8099 in docker
    --image=/path/to/image.tar or name of image (use docker images) if "hub" then will download despiegk/jsx_development from docker hub as base
    --port = port of container SSH std is 9022 (normally not needed to use because is in portrange:22 e.g. 9122 if portrange 1)

    ## code related

    --codepath = "/sandbox/code" can overrule, is where the github code will be checked out
    --pull = pull code from git, if not specified will only pull if code directory does not exist yet
    --branch = jumpscale branch: normally 'master' or 'development'


    """
    print(IT.Tools.text_replace(T))
    sys.exit(0)


def ui():

    args= IT.Tools.cmd_args_get()

    if not "codepath" in args:
        args["codepath"] = None

    if not "branch" in args:
        args["branch"]=BRANCH

    if "sshkey" not in args:
        args["sshkey"] = None

    if "h" in args or args=={}:
        help()

    IT.MyEnv.init(basedir=None,config={},readonly=True,codepath=args["codepath"])

    if "incontainer" not in args:

        rc,out,_=IT.Tools.execute("cat /proc/1/cgroup",die=False,showout=False)
        if rc==0 and out.find("/docker/")!=-1:
            args["incontainer"]=True
            #means we are in a docker
        else:
            args["incontainer"]=False

    if not "1" in args and not "2" in args and not "3" in args:
        if args["incontainer"]:
            #means we are inside a container
            T="""
            Installer choice for jumpscale in the docker
            --------------------------------------------

            Do you want to install
             - in system                              : 1
             - using a sandbox                        : 2

            """
            mychoice = 1
            # mychoice = int(IT.Tools.ask_choices(T,[1,2]))

        else:

            T="""
            Installer choice for jumpscale
            ------------------------------

            Do you want to install
             - insystem         (ideal for development only in OSX & Ubuntu1804)        : 1
             - using a sandbox  (only in OSX & Ubuntu1804): DONT USE YET                : 2
             - using docker?                                                            : 3

            """

            mychoice = int(IT.Tools.ask_choices(T,[1,3]))
        args[str(mychoice)]=True

    #means interactive

    if not args["incontainer"]:
        if not IT.MyEnv.sshagent_active_check():
            T="""
            Did not find an SSH key in ssh-agent, is it ok to continue without?
            It's recommended to have a SSH key as used on github loaded in your ssh-agent
            If the SSH key is not found, repositories will be cloned using https
            """
            print("Could not continue, load ssh key in ssh-agent and try again.")
            if "3" in args:
                sys.exit(1)
            if "y" not in args:
                if not IT.Tools.ask_yes_no("OK to continue?"):
                    sys.exit(1)
        else:
            args["sshkey"]=IT.MyEnv.sshagent_key_get()

    if "y" not in args and "r" not in args:
        if IT.Tools.ask_yes_no("\nDo you want to redo the full install? (means redo pip's ...)"):
            args["r"]=True

    if "3" in args: #means we want docker
        if "name" not in args:
            args["name"] = "default"

        container_exists = args["name"] in IT.Docker.docker_names()
        args["container_exists"]=container_exists

        if "name" not in args:
            dockername = IT.Tools.ask_string("What name do you want to use for your docker (default=default): ",default="default")
            if dockername == "":
                dockername = "default"
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
            if "d" not in args:
                args["d"]=True
            if args["image"] == "hub":
                args["image"] = "despiegk/3bot"
            if ":" not in args["image"]:
                args["image"]="%s:latest" % args["image"]
            if args["image"] not in IT.Docker.image_names():
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

    else:
        if "pull" not in args:
            #is not docker and not pull yet
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


    if "3" in args:
        T+=" - jumpscale will be installed using docker.\n"
    elif "1" in args:
         T+=" - jumpscale will be installed in the system.\n"
    elif "2" in args:
         T+=" - jumpscale will be installed using sandbox.\n"
    if not "incontainer" in args and sshkey2:
        T+= " - sshkey used will be: %s\n"%sshkey2

    if "1" in args and args["codepath"] is None:
        T+=" - location of code path is: /sandbox/code\n"
    else:
        T+=" - location of code path is: %s\n"%IT.MyEnv.config["DIR_CODE"]

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

        if "portrange" not in args:
            args["portrange"]=1
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

args = ui()

if "1" in args or "2" in args:

    if "r" in args:
        #remove the state
        IT.MyEnv.state_reset()

    if "2" in args:
        raise RuntimeError("sandboxed not supported yet")
        sandboxed = True
    else:
        sandboxed = False

    installer = IT.JumpscaleInstaller(branch=args["branch"])
    installer.install(basedir="/sandbox",config={},sandboxed=False,force=False,
            secret=args["secret"],private_key_words=args["private_key"],gitpull= "pull" in args)

    # if "w" in args:
    #     if "1" in args:

    #         #in system need to install the lua env
    #         IT.Tools.execute("source %s/env.sh;kosmos 'j.builder.runtimes.lua.install(reset=True)'"%SANDBOX, showout=False)
    #     IT.Tools.execute("source %s/env.sh;js_shell 'j.tools.markdowndocs.test()'"%SANDBOX, showout=False)
    #     print("Jumpscale X installed successfully")

elif "3" in args:

    j.shell()

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
#OR
python3 ~/code/github/threefoldtech/jumpscaleX/install/install.py
"""


"""
#env arguments

export INSYSTEM=1

export GITMESSAGE=

"""
