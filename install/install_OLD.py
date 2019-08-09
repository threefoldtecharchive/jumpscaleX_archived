from importlib import util
import os
import subprocess
import sys

BRANCH = "development"

# get current install.py directory
rootdir = os.path.dirname(os.path.abspath(__file__))

path = os.path.join(rootdir, "InstallTools.py")

if not os.path.exists(path):
    cmd = (
        "cd %s;rm -f InstallTools.py;curl \
        https://raw.githubusercontent.com/threefoldtech/jumpscaleX/%s/install/InstallTools.py?$RANDOM \
        > InstallTools.py"
        % (rootdir, BRANCH)
    )
    subprocess.call(cmd, shell=True)

spec = util.spec_from_file_location("IT", path)
IT = spec.loader.load_module()

sys.excepthook = IT.my_excepthook

args = {}


def help():
    T = """
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

    --pull = pull code from git, if not specified will only pull if code directory does not exist yet
    --branch = jumpscale branch: normally 'master' or 'development'


    """
    T = IT.Tools.text_replace(T)
    T += IT.MyEnv.configure_help()
    print(T)
    sys.exit(0)


def ui():

    args = IT.Tools.cmd_args_get()

    if not "codepath" in args:
        args["codepath"] = None

    if not "branch" in args:
        args["branch"] = BRANCH

    if "sshkey" not in args:
        args["sshkey"] = None

    if "h" in args or args == {}:
        help()

    if "3" in args:
        readonly = True
    else:
        readonly = False

    IT.MyEnv.configure(basedir=None, config={}, readonly=True, codepath=args["codepath"])
    IT.MyEnv.init()

    if "incontainer" not in args:

        rc, out, _ = IT.Tools.execute("cat /proc/1/cgroup", die=False, showout=False)
        if rc == 0 and out.find("/docker/") != -1:
            args["incontainer"] = True
            # means we are in a docker
        else:
            args["incontainer"] = False

    if not "1" in args and not "2" in args and not "3" in args:
        if args["incontainer"]:
            # means we are inside a container
            T = """
            Installer choice for jumpscale in the docker
            --------------------------------------------

            Do you want to install
             - in system                              : 1
             - using a sandbox                        : 2

            """
            mychoice = 1
            # mychoice = int(IT.Tools.ask_choices(T,[1,2]))

        else:

            T = """
            Installer choice for jumpscale
            ------------------------------

            Do you want to install
             - insystem         (ideal for development only in OSX & Ubuntu1804)        : 1
             - using a sandbox  (only in OSX & Ubuntu1804): DONT USE YET                : 2
             - using docker?                                                            : 3

            """

            mychoice = int(IT.Tools.ask_choices(T, [1, 3]))
        args[str(mychoice)] = True

    # means interactive

    if not IT.MyEnv.sshagent_active_check():
        T = """
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
        args["sshkey"] = IT.MyEnv.sshagent_sshkey_pub_get()

    if "y" not in args and "r" not in args:
        if IT.Tools.ask_yes_no("\nDo you want to redo the full install? (means redo pip's ...)"):
            args["r"] = True

    if "3" in args:  # means we want docker
        if "name" not in args:
            args["name"] = "default"

        container_exists = args["name"] in IT.Docker.containers_names()
        args["container_exists"] = container_exists

        if "name" not in args:
            dockername = IT.Tools.ask_string(
                "What name do you want to use for your docker (default=default): ", default="default"
            )
            if dockername == "":
                dockername = "default"
            args["name"] = dockername

        if container_exists:
            if "d" not in args:
                if not "y" in args:
                    if IT.Tools.ask_yes_no(
                        "docker:%s exists, ok to remove? Will otherwise keep and install inside." % args["name"]
                    ):
                        args["d"] = True
                # else:
                #     #is not interactive and d was not given, so should not continue
                #     print("ERROR: cannot continue, docker: %s exists."%args["name"])
                #     sys.exit(1)

        if "image" in args:
            if "d" not in args:
                args["d"] = True
            if args["image"] == "hub":
                args["image"] = "despiegk/3bot"
            if ":" not in args["image"]:
                args["image"] = "%s:latest" % args["image"]
            if args["image"] not in IT.Docker.image_names():
                if IT.Tools.exists(args["image"]):
                    IT.Tools.shell()
                else:
                    print("Cannot continue, image '%s' specified does not exist." % args["image"])
                    sys.exit(1)

        if "portrange" not in args:
            if "y" in args:
                args["portrange"] = 1
            else:
                if container_exists:
                    args["portrange"] = int(
                        IT.Tools.ask_choices("choose portrange, std = 1", [1, 2, 3, 4, 5, 6, 7, 8, 9])
                    )
                else:
                    args["portrange"] = 1

    else:
        if "pull" not in args:
            # is not docker and not pull yet
            if "y" not in args:
                # not interactive ask
                args["pull"] = IT.Tools.ask_yes_no("Do you want to pull code changes from git?")
            else:
                # default is not pull
                args["pull"] = False

    if "y" in args:

        if "secret" not in args:
            if IT.MyEnv.sshagent_active_check():
                args["secret"] = "SSH"
            else:
                args["secret"] = "1234"
        if "private_key" not in args:
            args["private_key"] = ""
    else:
        if "secret" not in args:
            if IT.MyEnv.sshagent_active_check():
                args["secret"] = IT.Tools.ask_string(
                    "Optional: provide secret to use for passphrase, if ok to use SSH-Agent just press 'ENTER'",
                    default="SSH",
                )
            else:
                args["secret"] = IT.Tools.ask_string("please provide secret passphrase for the BCDB.", default="1234")
        if "private_key" not in args:
            args["private_key"] = IT.Tools.ask_string(
                "please provide 24 words of the private key, or just press 'ENTER' for autogeneration."
            )

    # if "y" not in args and "w" not in args:
    #     if IT.Tools.ask_yes_no("Do you want to install lua/nginx/openresty & wiki environment?"):
    #         args["w"]=True

    T = """

    Jumpscale X Installer
    ---------------------

    """
    T = IT.Tools.text_replace(T)

    if "3" in args:
        T += " - jumpscale will be installed using docker.\n"
    elif "1" in args:
        T += " - jumpscale will be installed in the system.\n"
    elif "2" in args:
        T += " - jumpscale will be installed using sandbox.\n"
    if not "incontainer" in args and sshkey2:
        T += " - sshkey used will be: %s\n" % sshkey2

    T += " - location of code path is: %s\n" % IT.MyEnv.config["DIR_CODE"]

    if "w" in args:
        T += " - will install wiki system at end\n"
    if "3" in args:
        T += " - name of container is: %s\n" % args["name"]
        if args["container_exists"]:
            if "d" in args:
                T += " - will remove the docker, and recreate\n"
            else:
                T += " - will keep the docker container and install inside\n"

        if "image" in args:
            T += " - will use docker image: '%s'\n" % args["image"]

        if "portrange" not in args:
            args["portrange"] = 1
        portrange = args["portrange"]

        a = 8000 + int(portrange) * 10
        b = 8004 + int(portrange) * 10
        portrange_txt = "%s-%s:8000-8004" % (a, b)
        port = 9000 + int(portrange) * 100 + 22

        T += " - will map ssh port to: '%s'\n" % port
        T += " - will map portrange '%s' (8000-8004) always in container.\n" % portrange_txt

    if "debug" in args:
        IT.MyEnv.debug = True
        T += " - runs in debug mode (means will use debugger when error).\n"

    T += "\n"
    print(T)

    if "c" in args or "y" not in args:
        if not IT.Tools.ask_yes_no("Ok to continue?"):
            sys.exit(1)

    return args


args = ui()

if "1" in args or "2" in args:

    force = False
    if "r" in args:
        # remove the state
        IT.MyEnv.state_reset()
        args["pull"] = True
        force = True

    if "2" in args:
        raise j.exceptions.Base("sandboxed not supported yet")
        sandboxed = True
    else:
        sandboxed = False

    installer = IT.JumpscaleInstaller(branch=args["branch"])
    installer.install(
        basedir="/sandbox",
        config={},
        sandboxed=sandboxed,
        force=force,
        secret=args["secret"],
        private_key_words=args["private_key"],
        gitpull=args["pull"],
    )

    # if "w" in args:
    #     if "1" in args:

    #         #in system need to install the lua env
    #         IT.Tools.execute("source %s/env.sh;kosmos 'j.builders.runtimes.lua.install(reset=True)'"%SANDBOX, showout=False)
    #     IT.Tools.execute("source %s/env.sh;js_shell 'j.tools.markdowndocs.test()'"%SANDBOX, showout=False)
    #     print("Jumpscale X installed successfully")

elif "3" in args:

    if args["container_exists"] and "d" in args:
        IT.Tools.execute("docker rm -f %s" % args["name"])
        args["container_exists"] = False

    if "image" not in args:
        args["image"] = "phusion/baseimage:master"
        if "hub" in args:
            args["image"] = "despiegk/3bot"
    if not args["container_exists"]:
        if "port" not in args:
            args["port"] = 8022

    # docker installer
    di = IT.Docker(
        name="default", delete=False, portrange=1, image=args["image"], sshkey=None, baseinstall=True, cmd=None
    )

    # for now only support for insystem
    args_txt = "-1"
    for item in ["r", "p", "w"]:
        if item in args:
            args_txt += " -%s" % item
    args_txt += " -y"
    # args_txt+=" -c"
    for item in ["codepath", "secret", "private_key", "debug"]:
        if item in args:
            args_txt += " --%s='%s'" % (item, args[item])

    # add install from a specific branch
    install = IT.JumpscaleInstaller(branch=args["branch"])

    def getbranch():
        cmd = "cd {}/github/threefoldtech/jumpscaleX; git branch | grep r\* | cut -d ' ' -f2".format(args["codepath"])
        _, stdout, _ = IT.Tools.execute(cmd)
        return stdout.strip()

    # check if already code exists and checkout the argument branch
    if os.path.exists("{}/github/threefoldtech/jumpscaleX".format(args["codepath"])):
        if getbranch() != args["branch"]:
            print("found JS on machine, Checking out branch {}...".format(args["branch"]))
            IT.Tools.execute(
                """cd {}/github/threefoldtech/jumpscaleX
                        git remote set-branches origin '*'
                        git fetch -v
                        git checkout {} -f
                        git pull""".format(
                    args["codepath"], args["branch"]
                )
            )

        print("On {} branch".format(args["branch"]))
    else:
        print("no local code at {}".format(args["codepath"]))

    install.repos_get(pull=False)

    cmd = "python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py %s" % args_txt
    print(" - Installing jumpscaleX ")
    di.sshexec(cmd)

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
    print(k.format(port=di.port))


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
