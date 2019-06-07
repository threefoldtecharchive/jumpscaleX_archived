from Jumpscale import j


class ExecutorInstallers:
    def __init__(self, executor):
        self.executor = executor

    def kosmos(self):
        self.jumpscale()
        j.shell()

    def base(self):
        if not self.executor.state_exists("install_base"):
            self.executor.execute("apt update")
            self.executor.execute("apt upgrade -y", interactive=True)
        self.executor.state_set("install_base")

    def mosh(self):
        if not self.executor.state_exists("install_mosh"):
            self.executor.execute("apt install mosh -y")
        self.executor.state_set("install_mosh")

    def jumpscale(self):
        if not self.executor.state_exists("install_jumpscale"):
            self.base()

            self.executor.execute(
                "curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX/development_installer/install/jsx.py\?$RANDOM > /tmp/jsx"
            )
            self.executor.execute("chmod 777 /tmp/jsx")
            self.executor.execute("/tmp/jsx install", interactive=True)
        self.executor.state_set("install_jumpscale")

    def _check_base(self):
        if not self.__check_base:

            def do():
                if self.state_exists("check_base") is False:
                    C = """
                    if ! grep -Fq "deb http://mirror.unix-solutions.be/ubuntu/ bionic" /etc/apt/sources.list; then
                        echo >> /etc/apt/sources.list
                        echo "# Jumpscale Setup" >> /etc/apt/sources.list
                        echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
                    fi
                    apt update
                    apt install rsync curl wget -y
                    apt install git -y
                    # apt install mosh -y
                    """
                    self.execute(j.core.text.strip(C))
                    self.state_set("check_base")
                return "OK"

            self.cache.get("_check_base", method=do, expire=3600, refresh=False, retry=2, die=True)

            self.__check_base = True
