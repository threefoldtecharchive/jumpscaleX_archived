import argparse
import inspect
import os
import shutil
import sys
from importlib import util
from urllib.request import urlopen

DEFAULT_BRANCH = "master"
CONTAINER_BASE_IMAGE = "phusion/baseimage:master"
# CONTAINER_BASE_IMAGE = "despiegk/3bot:latest"
CONTAINER_NAME = "3bot"


def load_install_tools():
    # get current install.py directory
    rootdir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(rootdir, "InstallTools.py")

    if not os.path.exists(path):
        os.chdir(rootdir)
        url = "https://raw.githubusercontent.com/threefoldtech/jumpscaleX/%s/install/InstallTools.py" % DEFAULT_BRANCH
        with urlopen(url) as resp:
            if resp.status != 200:
                raise RuntimeError("fail to download InstallTools.py")
            with open(path, "w+") as f:
                f.write(resp.read().decode("utf-8"))

    spec = util.spec_from_file_location("IT", path)
    IT = spec.loader.load_module()
    sys.excepthook = IT.my_excepthook
    return IT


# DO NOT DO THIS IN ANY OTHER WAY !!!
IT = load_install_tools()


def install_ui(args):
    IT.Tools.shell()
    if not IT.MyEnv.sshagent_active_check():
        T = """
        Did not find an SSH key in ssh-agent, is it ok to continue without?
        It's recommended to have a SSH key as used on github loaded in your ssh-agent
        If the SSH key is not found, repositories will be cloned using https

        if you never used an ssh-agent or github, just say "y"

        """
        if args.y is False:
            if not IT.Tools.ask_yes_no("OK to continue?"):
                sys.exit(1)

    if not args.s and not args.y and not args.r:
        if IT.Tools.ask_yes_no("\nDo you want to redo the full install? (means redo pip's ...)"):
            args.r = True

        if CONTAINER_NAME in IT.Docker.docker_names() and args.d is False and args.y is False:
            args.d = IT.Tools.ask_yes_no(
                "docker:%s exists, ok to remove? Will otherwise keep and install inside." % CONTAINER_NAME
            )

    if args.pull is None:
        if args.y is False:
            args.pull = IT.Tools.ask_yes_no("Do you want to pull code changes from git?")
        else:
            args.pull = False  # default is not pull

    if not args.secret:
        if args.y:
            args.secret = IT.MyEnv.sshagent_key_get() if IT.MyEnv.sshagent_active_check() else "1234"
        else:
            if IT.MyEnv.sshagent_active_check():
                args.secret = IT.Tools.ask_string(
                    "Optional: provide secret to use for passphrase, if ok to use SSH-Agent just press 'ENTER'",
                    default="SSH",
                )
            else:
                args.secret = IT.Tools.ask_string("please provide secret passphrase for the BCDB.", default="1234")

    if not args.private_key and not args.y:
        args.private_key = IT.Tools.ask_string(
            "please provide 24 words of the private key, or just press 'ENTER' for autogeneration."
        )


def install_summary(args):
    T = """

    Jumpscale X Installer
    ---------------------

    """
    T = IT.Tools.text_replace(T)

    if IT.MyEnv.sshagent_active_check():
        T += " - sshkey used will be: %s\n" % args.secret

    if args.code_path:
        T += " - location of code path is: %s\n" % args.code_path
    if args.pull:
        T += " - code will be pulled from github\n"
    if args.wiki:
        T += " - will install wiki system at end\n"
    T += " - name of container is: %s\n" % CONTAINER_NAME
    if CONTAINER_NAME in IT.Docker.docker_names():
        if "d" in args:
            T += " - will remove the docker, and recreate\n"
        else:
            T += " - will keep the docker container and install inside\n"

    T += " - will use docker image: '%s'\n" % args.image

    # portrange = args["portrange"]

    # a = 8000+int(portrange)*10
    # b = 8004+int(portrange)*10
    # portrange_txt = "%s-%s:8000-8004" % (a, b)
    # port = 9000+int(portrange)*100 + 22

    # T += " - will map ssh port to: '%s'\n" % port
    # T += " - will map portrange '%s' (8000-8004) always in container.\n" % portrange_txt

    if args.debug:
        IT.MyEnv.debug = True
        T += " - runs in debug mode (means will use debugger when error).\n"

    T += "\n"
    print(T)

    if args.c or not args.y:
        if not IT.Tools.ask_yes_no("Ok to continue?"):
            sys.exit(1)


def install(args):
    install_ui(args)
    install_summary(args)

    docker = IT.Docker(
        name=CONTAINER_NAME, delete=args.d, portrange=args.port_range, sshkey=args.secret, image=args.image
    )
    docker.jumpscale_install(secret=args.secret, private_key=args.private_key)


def docker_get(existcheck=True):
    docker = IT.Docker(name=CONTAINER_NAME, delete=False, portrange=1)
    if existcheck and CONTAINER_NAME not in docker.docker_names():
        print("container does not exists. please install first")
        sys.exit(1)
    return docker


def import_container(args):
    docker = docker_get(existcheck=False)
    docker.import_(path=args.input)


def export_container(args):
    docker = docker_get()
    docker.export(path=args.output)


def stop_container(args):
    docker = docker_get(existcheck=False)
    docker.stop()


def start_container(args):
    docker = docker_get(existcheck=False)
    docker.start()


def delete_container(args):
    docker = docker_get(existcheck=False)
    docker.delete()


def reset_container(args):
    docker = docker_get()
    docker.reset()


def kosmos(args):
    docker = IT.Docker(name=CONTAINER_NAME, delete=False, portrange=1)
    if CONTAINER_NAME not in docker.docker_names():
        print("container does not exists. please install first")
        sys.exit(1)
    os.execv(
        shutil.which("ssh"),
        [
            "ssh",
            "root@localhost",
            "-A",
            "-t",
            "-oStrictHostKeyChecking=no",
            "-p",
            str(docker.port),
            "source /sandbox/env.sh;kosmos",
        ],
    )


def shell(args):
    docker = IT.Docker(name=CONTAINER_NAME, delete=False, portrange=1)
    if CONTAINER_NAME not in docker.docker_names():
        print("container does not exists. please install first")
        sys.exit(1)
    os.execv(
        shutil.which("ssh"), ["ssh", "root@localhost", "-A", "-t", "-oStrictHostKeyChecking=no", "-p", str(docker.port)]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3bot development environment based on docker")
    parser.add_argument("--debug", help="launch the debugger if something goes wrong")
    parser.add_argument(
        "--code-path",
        default=None,
        type=str,
        help="path where the github code will be checked out, default /sandbox/code if it exists otherwise ~/code",
    )
    subparsers = parser.add_subparsers()

    docker_parser = argparse.ArgumentParser(add_help=False)
    docker_parser.add_argument(
        "-y", help="answer yes on every question (for unattended installs)", action="store_true", default=False
    )
    docker_parser.add_argument(
        "-c",
        help="will confirm all filled in questions at the end (useful when using -y)",
        action="store_true",
        default=False,
    )
    docker_parser.add_argument(
        "-s",
        help="from scratch, means will start from empty ubuntu and re-install everything",
        action="store_true",
        default=False,
    )
    docker_parser.add_argument(
        "-r",
        help="reinstall, basically means will try to re-do everything without removing the data",
        action="store_true",
        default=False,
    )
    docker_parser.add_argument(
        "-d", help="if set will delete the docker container if it already exists", action="store_true", default=False
    )
    docker_parser.add_argument("--wiki", "-w", help="also install the wiki system", action="store_true", default=False)
    docker_parser.add_argument(
        "--secret",
        default=None,
        type=str,
        help="if you use 'SSH' then a secret will be derived from the SSH-Agent (only if only 1 ssh key loaded",
    )
    docker_parser.add_argument(
        "--private-key",
        default="",
        type=str,
        help="24 words, use '' around the private key if secret specified and private_key not then will ask in -y mode will autogenerate",
    )
    docker_parser.add_argument(
        "--pull",
        default=False,
        action="store_true",
        help="pull code from git, if not specified will only pull if code directory does not exist yet",
    )
    docker_parser.add_argument(
        "--branch",
        default=DEFAULT_BRANCH,
        type=str,
        help="jumpscale branch. default 'master' or 'development' for unstable release",
    )
    docker_parser.add_argument(
        "--image",
        default=CONTAINER_BASE_IMAGE,
        type=str,
        help="select the container image to use to create the container",
    )
    docker_parser.add_argument("--port-range", default=1, type=int)

    parser_install = subparsers.add_parser(
        "install", help="create the 3bot container and install jumpcale inside", parents=[docker_parser]
    )
    parser_install.set_defaults(func=install)

    ##EXPORT
    parser_export = subparsers.add_parser("export", help="export the 3bot container to a tar archive")
    parser_export.add_argument(
        "--output", "-o", help="export the container to a file pointed by --output", default="/tmp/3bot.tar"
    )
    parser_export.set_defaults(func=export_container)

    ##IMPORT
    parser_import = subparsers.add_parser(
        "import",
        help="re-create a 3bot container from an archive created with the export command",
        parents=[docker_parser],
    )
    parser_import.add_argument(
        "--input", "-i", help="import a container from the tar pointed by --import", default="/tmp/3bot.tar"
    )
    parser_import.set_defaults(func=import_container)

    ##STOP START DELETE RESET
    parser_stop = subparsers.add_parser("stop", help="stop the 3bot container")
    parser_stop.set_defaults(func=stop_container)

    parser_start = subparsers.add_parser("start", help="start the 3bot container")
    parser_start.set_defaults(func=start_container)

    parser_delete = subparsers.add_parser("delete", help="delete the 3bot container")
    parser_delete.set_defaults(func=delete_container)

    parser_reset = subparsers.add_parser("resetall", help="reset the 3bot container (delete all images & containers")
    parser_reset.set_defaults(func=reset_container)

    ##KOSMOS
    parser_connect = subparsers.add_parser(
        "kosmos", help="get kosmos shell (runs in container)", parents=[docker_parser]
    )
    parser_connect.set_defaults(func=kosmos)

    ##SHELL
    parser_connect = subparsers.add_parser("shell", help="ssh into the container", parents=[docker_parser])
    parser_connect.set_defaults(func=shell)

    args = parser.parse_args()

    IT.MyEnv.init(basedir=None, config={}, readonly=True, codepath=args.code_path)

    if "func" not in args:
        print("please specify a command e.g. install, if you need more help use -h")
        print("example to install:   jsx install -s -y -c")
        sys.exit(1)

    args.func(args)
