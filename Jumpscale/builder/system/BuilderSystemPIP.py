from Jumpscale import j


class BuilderSystemPIP(j.builder.system._BaseClass):


    def __init(self):



    def ensure(self, reset=False):

        if self._done_check("ensure", reset):
            return

        tmpdir = j.core.tools.text_replace("{DIR_TEMP}")
        cmd1 = """
            #important remove olf pkg_resources, will conflict with new pip
            rm -rf /usr/lib/python3/dist-packages/pkg_resources
            cd %s/
            rm -rf get-pip.py
            """ % tmpdir
        self.prefab.core.execute_bash(cmd1)
        #TODO: this does not seem to work everywhere, lets check on Ubuntu 1804 & OSX
        cmd2 = "cd %s/ && curl https://bootstrap.pypa.io/get-pip.py >  get-pip.py" % tmpdir
        j.sal.process.execute(cmd2)
        cmd3 = "python3 %s/get-pip.py" % tmpdir
        j.sal.process.execute(cmd3)

        self._done_set("ensure")

    def packageUpgrade(self, package):
        '''
        The "package" argument, defines the name of the package that will be upgraded.
        '''
        # self.prefab.core.set_sudomode()
        j.sal.process.execute('pip3 install --upgrade %s' % (package))

    def install(self, package=None, upgrade=True, reset=False):
        '''
        The "package" argument, defines the name of the package that will be installed.

        package can be list or comma separated list of packages as well

        '''
        self.ensure()
        packages = j.core.text.getList(package, "str")

        cmd = ""

        todo = []
        for package in packages:
            if reset or not self._done_get("pip_%s" % package):
                todo.append(package)
                if self.prefab.core.isArch:
                    if package in ["credis", "blosc", "psycopg2"]:
                        continue

                if self.prefab.core.isCygwin and package in ["psycopg2", "psutil", "zmq"]:
                    continue

                cmd += "pip3 install %s" % package
                if upgrade:
                    cmd += " --upgrade"
                cmd += "\n"

        if len(todo) > 0:
            j.sal.process.execute(cmd)

        for package in todo:
            self._done_set("pip_%s" % package)

    def packageRemove(self, package):
        '''
        The "package" argument, defines the name of the package that will be ensured.
        The argument "r" referes to the requirements file that will be used by pip and
        is equivalent to the "-r" parameter of pip.
        Either "package" or "r" needs to be provided
        '''
        if not self._done_get("pip_remove_%s" % package):
            return j.sal.process.execute('pip3 uninstall %s' % (package))
            self._done_set("pip_remove_%s" % package)

    def multiInstall(self, packagelist, upgrade=True, reset=False):
        """
        @param packagelist is text file and each line is name of package
        can also be list

        e.g.
            # influxdb
            # ipdb
            # ipython
            # ipython-genutils
            itsdangerous
            Jinja2
            # marisa-trie
            MarkupSafe
            mimeparse
            mongoengine

        if doneCheckMethod!=None:
            it will ask for each pip if done or not to that method, if it returns true then already done

        """
        if j.data.types.string.check(packagelist):
            packages = packagelist.split("\n")
        elif j.data.types.list.check(packagelist):
            packages = packagelist
        else:
            raise j.exceptions.Input(
                'packagelist should be string or a list. received a %s' % type(packagelist))

        to_install = []
        for dep in packages:
            dep = dep.strip()
            if dep is None or dep == "" or dep[0] == '#':
                continue
            to_install.append(dep)

        for item in to_install:
            self.install(item, reset=reset)
