import os
import sys
import json
import fcntl
import pystache
from subprocess import Popen, PIPE
from ...core.JSBase import JSBase, jwalk

import functools
import types

# for monkey-patching the j instance to add namespace... "things"
patchers = [
]

def find_jslocation(line):
    """ finds self.__jslocation__ for class-instance declaration version
        OR __jslocation__ with whitespace in front of it, indicating
        static version:

        class Foo:
            def __init__(...)
                self.__jslocation__ = 'j.foo'
        OR:

        class Foo:
            __jslocation__ = 'j.foo'
    """
    if line.find("self.__jslocation__") != -1:
        return True
    idx = line.find("__jslocation__")
    if idx == -1:
        return False
    # ok found something like '<space><space>__jsinstance__ = ......' ?
    prefix = line[:idx]
    return prefix.isspace()


# used (during bootstrapping) to find the plugin path
# gets down to the Jumpscale core9 subdirectory from here
# (.../Jumpscale/tools/loader/JSLoader.py)
plugin_path = os.path.dirname(os.path.abspath(__file__))
plugin_path = os.path.dirname(plugin_path)
top_level_path = os.path.dirname(plugin_path)

def add_dynamic_instance(j, parent, child, module, kls):
    """ very similar to dynamic_generate, needs work
        to morph into using same code
    """
    #print ("adding", parent, child, module, kls)
    if not parent:
        parent = j
    else:
        parent = j.jget(parent)
    if kls:
        # assume here that modules are imported from Jumpscale *only*
        # (*we're in boostrap mode so it's ok), and hand-create
        # a full module path.
        #print (top_level_path)
        if "." in module:
            mname = "%s.py" % module.replace(".", "/")
            fullpath = os.path.join(top_level_path, mname)
        else:
            mname = "%s/__init__.py" % module.replace(".", "/")
            fullpath = os.path.join(top_level_path, mname)
        #print ("fullpath", fullpath)
        return parent._add_instance(child, "Jumpscale." + module, kls,
                                    fullpath, basej=j)
        #print ("added", parent, child)
    else:
        walkfrom = j
        for subname in module.split('.'):
            walkfrom = getattr(walkfrom, subname)
        childlast = child.split('.')[-1]
        pj = parent.jget(child, stealth=True, end=-1)
        pj.__aliases__[childlast] = walkfrom



def remove_dir_part(path):
    "only keep part after jumpscale or digitalme"
    state = 0
    res = []
    for item in path.split("/"):
        if state == 0:
            if item.find("Jumpscale") != - \
                    1 or item.find("DigitalMe") != -1:
                state = 1
        if state == 1:
            res.append(item)
    if len(res) < 2:
        raise RuntimeError("could not split path in jsloader")
    if res[0] == res[1]:
        if res[0].casefold().find("jumpscale") != - \
                1 or res[0].casefold().find("digitalme") != -1:
            res.pop(0)
    return "/".join(res)


class JSLoaderDONTUSE():

    # __jslocation__ = "j.tools.jsloader"

    def __init__(self):
        self.tryimport = False
        self._logger = None
        self._plugins = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = j.logger.get("jsloader")
        return self._logger

    @property
    def autopip(self):
        return j.core.state.configGet("system")["autopip"] in \
            [True, "true", "1", 1]

    def _installDevelopmentEnv(self):
        cmd = "apt-get install python3-dev libssl-dev -y"
        j.sal.process.execute(cmd)
        j.sal.process.execute("pip3 install pudb")

    def _pip(self, item):
        rc, out, err = j.sal.process.execute(
            "pip3 install %s" %
            item, die=False)
        if rc > 0:
            if "gcc' failed" in out:
                self._installDevelopmentEnv()
                rc, out, err = j.sal.process.execute(
                    "pip3 install %s" % item, die=False)
        if rc > 0:
            print("WARNING: COULD NOT PIP INSTALL:%s\n\n" % item)
        return rc

    def process_location(self, path, jlocationSubName, jlocationSubList):
        # import a specific location sub (e.g. j.clients.git)

        classfile, classname, imports = jlocationSubList

        classfile = os.path.join(path, classfile) # put back abspath for now
        generationParamsSub = {}
        generationParamsSub["classname"] = classname
        generationParamsSub["name"] = jlocationSubName
        if classfile.startswith("/"):
            classfile = remove_dir_part(classfile)
        importlocation = classfile[:-3].replace("//", "/").replace("/", ".")
        #print ("process", classfile, importlocation)
        generationParamsSub["importlocation"] = importlocation
        prefix = importlocation.split('.')[:-1]
        prefix = map(lambda x: x[0].upper() + x[1:], prefix)
        prefix = ''.join(prefix)
        generationParamsSub["classprefix"] = prefix

        rc = 0

        return rc, generationParamsSub

    @property
    def plugins(self):
        """ get the plugins from the config file... or get a default
            suitable for bootstrapping
        """
        # ok, set up a default based on the current location of THIS
        # file.  it's a hack however it will at least get started.
        # this will get the plugins recognised from Jumpscale
        # when there is absolutely no config file set up.
        #
        # related to issue #71
        #
        if self._plugins is None:
            defaultplugins = {'Jumpscale': top_level_path}

            state = j.tools.executorLocal.state
            plugins = state.configGet('plugins', defaultplugins)
            if 'Jumpscale' not in plugins:
                plugins['Jumpscale'] = defaultplugins['Jumpscale']
            for k in plugins:
                # issue #133, plugins are a bit fragile, have to have / on end
                if not plugins[k].endswith("/"):
                    plugins[k] += "/"
            self._plugins = plugins
        return self._plugins

    @property
    def jsonfiles(self):
        """ returns a list of the json plugin files
        """
        res = {}
        for name, _path in self.plugins.items():
            res[name] = os.path.join(_path, "%s.plugins.json" % name)
        # print("jsonfiles",res)
        return res

    def gather_modules(self, startpath=None, depth=0, recursive=True,
                       pluginsearch=None):
        """ identifies and gathers information about (only) jumpscale modules

            can be used to search specific paths (use startparth), by depth
            (0=infinite), and recursively.

            also can be restricted to search only specific plugins
            (pluginsearch)
        """
        # outCC = outpath for code completion
        # out = path for core of jumpscale

        # make sure the jumpscale toml file is set / will also link cmd files
        # to system
        j.tools.executorLocal.env_check_init()

        if not pluginsearch:
            pluginsearch = []
        if not isinstance(pluginsearch, list):
            pluginsearch = [pluginsearch]

        moduleList = {}
        baseList = {}
        if startpath is None:
            startpath = "j"
        if startpath == 'j':
            logfn = self._logger.info
        else:
            logfn = self._logger.debug

        # split the startpath (j format) to create subdirectory
        # search locations to be appended to plugin path
        startpath = startpath.split('.')[1:]

        #print ("plugins", plugins)
        for name, _path in self.plugins.items():
            if pluginsearch and name not in pluginsearch:
                continue
            path = [_path] + startpath
            path = os.path.join(*path)
            logfn("find modules in jumpscale for %s: '%s'" % (name, path))
            #print ("startpath: %s depth: %d" % (startpath, depth))
            if not j.sal.fs.exists(_path, followlinks=True):
                raise RuntimeError("Could not find plugin dir:%s" % _path)
            if not j.sal.fs.exists(path, followlinks=True):
                continue
            if False:  # XXX hmmm.... nasty hack... disable....
                pth = path
                if pth[-1] == '/':
                    pth = pth[:-1]
                pth = os.path.split(pth)[0]
                sys.path = [pth] + sys.path
            moduleList, baseList = self.find_modules(path=path,
                                                     moduleList=moduleList,
                                                     baseList=baseList,
                                                     depth=depth,
                                                     recursive=recursive)

        for jlocationRoot, jlocationRootDict in moduleList.items():
            # is per item under j e.g. j.clients

            print ("jlocationRoot", jlocationRoot, jlocationRootDict)
            if jlocationRoot == 'j':
               print (jlocationRootDict)
            if not jlocationRoot.startswith("j") and jlocationRoot != 'j':
                raise RuntimeError(
                    "jlocation should start with j, found: '%s', in %s" %
                    (jlocationRoot, jlocationRootDict))

            for subname, sublist in jlocationRootDict.items():
                rc, _ = self.process_location(path, subname, sublist)
                if rc != 0:
                    # remove unneeded items
                    del jlocationRootDict[subname]

        sdfsf

        return moduleList, baseList

    def add_submodules(self, basej, subname, sublist):
        parent = jwalk(basej, subname, end=-1)
        jname = subname.split(".")[-1]
        #print ("add_submodule", basej, parent, subname, sublist)
        modulename, classname, imports = sublist
        importlocation = remove_dir_part(modulename)[:-3]
        importlocation = importlocation.replace("//", "/").replace("/", ".")
        #print ("importlocation", importlocation)
        parent._add_instance(jname, importlocation, classname,
                             fullpath=modulename,
                             basej=basej)

    def _dynamic_merge(self, basej, moduleList, baseList, aliases=None):
        """ dynamically merges modules into a jumpscale instance.

            base (root) instance constructors are **REQUIRED** to not
            have side-effects: they get instantiated straight away
            (see use of m.getter() below).

            anything else gets created as a lazy-property
            (see BaseGetter __getattribute__ override, they
             end up in BaseGetter.__subgetters__)

             NOTE: this function MUST be called when __dynamic_ready__ == False
             as the use of getattr checking (child modules) would fire
             off dynamic filesystem-walking on every child module being
             added
        """
        assert basej.__dynamic_ready__ == False, \
            "merging must not be combined with dynamic loading"

        if isinstance(moduleList, dict):
            moduleList = moduleList.items()
        if aliases is None:
            aliases = map(lambda x: (x['from'], x['to']), patchers)

        _j = basej

        #print ("baselist", baseList)
        for jlocationRoot in baseList:
            jname = jlocationRoot.split(".")[1].strip()
            kls = baseList[jlocationRoot]
            #print ("_j", _j, jname)
            try:
                _j.jget(jname, stealth=True)
                continue
            except AttributeError:
                #print ("baselisted", jname, kls)
                m = add_dynamic_instance(_j, '', jname, jname, kls)

        for jlocationRoot, jlocationRootDict in moduleList:
            #print ("root", jlocationRoot, jlocationRootDict)
            jname = jlocationRoot.split(".")[1].strip()
            #print ("dynamic generate root", jname, jlocationRoot)
            for subname, sublist in jlocationRootDict.items():
                # XXX ONLY do this in __dynamic_ready__ == False!
                # otherwise it will kick the dynamic loading into gear
                fullchildname = "%s.%s" % (jname, subname)
                try:
                    _j.jget(fullchildname, stealth=True)
                    continue
                except AttributeError:
                    self.add_submodules(_j, fullchildname, sublist)

        for frommodule, tomodule in aliases:
            walkfrom = jwalk(_j, frommodule, end=-1)
            frommodule = frommodule.split('.')
            for fromname in frommodule[:-1]:
                walkfrom = getattr(walkfrom, fromname)
            child = frommodule[-1]
            walkto = _j
            for subname in tomodule.split('.'):
                walkto = getattr(walkto, subname)
            setattr(walkfrom, child, walkto)

        return _j

    def find_jsmodule(self, modulepath):
        """ returns nearest module in the table.  could really use a range
            search here.
        """
        if modulepath in j.__jsmodlookup__:
            return j.__jsmodlookup__[modulepath]
        for k, info in j.__jsmodlookup__.items():
            if not k.startswith(modulepath):
                continue
            #print ("match", modulepath, info)
            (modulename, classname, plugin, fullchildname) = info
            return info

    def reset_jsonmodules(self):
        self._plugins = None
        j.__jsmodlookup__ = {} # table that turns module to path
        j.__jsmodbase__ = {}

    def manage_jsonmodules(self, plugin, modbase):
        j.__jsmodbase__[plugin] = modbase
        pluginpath = os.path.dirname(self.plugins[plugin]) # strip library name
        pluginpath = os.path.realpath(pluginpath) # resolve to any symlinks
        print("pluginpath",pluginpath)
        (modlist, baselist) = modbase
        for jlocationRoot, jlocationRootDict in modlist.items():
            # print ("root", jlocationRoot, jlocationRootDict)
            jname = jlocationRoot.split(".")[1].strip()
            print ("dynamic generate root", jname, jlocationRoot)
            for subname, sublist in jlocationRootDict.items():
                fullchildname = "j.%s.%s" % (jname, subname)
                modulename, classname, imports = sublist
                print ("sublist", subname, sublist)
                if not modulename.startswith("/"): # issue #133, relative
                    ppath = os.path.dirname(pluginpath)
                    print("ppath", ppath)
                    modulename = os.path.join(ppath, modulename)
                    print ("full path, now %s" % modulename)
                    sublist = (modulename, classname, imports)
                    jlocationRootDict[subname] = sublist
                realmodname = os.path.realpath(modulename)
                plen = len(pluginpath)

                print("readlmodname", realmodname, realmodname[:plen])
                print ("pluginpath",pluginpath)

                assert realmodname[:plen] == pluginpath
                pmodname = realmodname[plen+1:-3] # strip plugpath and ".py"
                pmodname = '.'.join(pmodname.split('/'))
                info = (modulename, classname, plugin, fullchildname)
                j.__jsmodlookup__[pmodname] = info
                #print ("child", pluginpath, fullchildname, pmodname, info)


    def load_json(self):
        """ read the jumpscale json files
        """

        self.reset_jsonmodules()
        failed = False
        for plugin, outJSON in self.jsonfiles.items():
            self._logger.debug("* jumpscale json path:%s" % outJSON)
            try:
                outJSON = j.sal.fs.readFile(outJSON)
                modbase = json.loads(outJSON)
            except ValueError as e:
                modbase = ({}, {})
                failed = True
            self.manage_jsonmodules(plugin, modbase)

        return not failed

    def generate_json(self, pluginsearch=None):
        """ generates the jumpscale json file(s), walking the plugin directories
            and saving the results in $HOSTCFGDIR/jumpscale.json.  also
            stores the results in j.__jsjson__

            may be restricted to a single plugin library (pluginsearch)

            to call:
            python -c 'from Jumpscale import j;j.core.jsgenerator.generate()
        """

        if pluginsearch is None:  # reset the plugins, redoing them all
            self.reset_jsonmodules()

        for plugin, outJSON in self.jsonfiles.items():
            if pluginsearch and pluginsearch != plugin:
                continue
            # gather list of modules (also initialises environment)
            modbase = self.gather_modules(pluginsearch=plugin)

            # outCC = outpath for code completion
            # out = path for core of jumpscale

            self._logger.info("* jumpscale json path:%s" % outJSON)

            modlistout_json = json.dumps(modbase, sort_keys=True, indent=4)
            j.sal.fs.writeFile(outJSON, modlistout_json)
            self.manage_jsonmodules(plugin, modbase)

    def _pip_installed(self):
        """ return the list of all installed pip packages
        """
        _, out, _ = j.sal.process.execute(
            'pip3 list --format json', die=False, showout=False)
        pip_list = json.loads(out)
        return [p['name'] for p in pip_list]

    def find_jslocations(self, path):
        """ XXX this *REALLY* should not be done.  duplicating what
            python does already is a really, really bad idea.  several
            bugs have been found already.

            it would be much better to actually load/compile the file
            then actually walk either the AST or the module.  that
            way at least it is using a standard python library.

            returns:
                [$classname]["location"] =$location
                [$classname]["import"] = $importitems
        """
        res = {}
        C = j.sal.fs.readFile(path)
        classname = None
        locfound = False
        for line in C.split("\n"):
            if line.startswith("class "):
                locfound = False  # reset search
                classname = line.replace(
                    "class ", "").split(":")[0].split(
                    "(", 1)[0].strip()
                if classname == "JSBaseClassConfig" or \
                   classname == "_JSBaseClassConfig":
                    break
            if find_jslocation(line) and locfound == False:
                if classname is None:
                    fname = os.path.split(path)[1]
                    if fname == 'JSLoader.py':
                        # XXX sigh doing manual parsing of python files
                        # like this is never a good idea, it is much
                        # better to do an AST syntax tree walk, that's
                        # what it's for.  JSLoader.py has some occurrences
                        # of __jslocation__ that are being detected,
                        # so we skip them here.
                        continue
                    raise RuntimeError(
                        "Could not find class in %s "
                        "while loading jumpscale lib." % path)
                # XXX not a good way to get value after equals (remove " and ')
                #print ("line ------->", line, path)
                location = line.split("=", 1)[1]
                location = location.replace('"', "")
                location = location.replace("'", "").strip()
                if location.find("__jslocation__") == -1:
                    if classname not in res:
                        res[classname] = {}
                    res[classname]["location"] = location
                    locfound = True
                    self._logger.debug("%s:%s:%s" % (path, classname, location))
            if line.find("self.__imports__") != -1:
                if classname is None:
                    raise RuntimeError(
                        "Could not find class in %s " +
                        "while loading jumpscale lib." %
                        path)
                imports = line.split("=", 1)[1]
                imports = imports.replace("\"", "")
                imports = imports.replace("'", "").strip()
                imports = map(str.strip, imports.split(","))
                imports = list(filter(None, imports))
                if classname not in res:
                    res[classname] = {}
                res[classname]["import"] = imports

        return res

    def find_modules(self, path, moduleList=None, baseList=None, depth=None,
                     recursive=True, return_relative=True):
        """ walk over code files & find locations for jumpscale modules
            return as two dicts.

            format of moduleList:
            [$rootlocationname][$locsubname]=(classfile,classname,imports)

            format of baseList:
            [$rootlocationname]=(classname,jlocation)
        """
        # self._logger.debug("modulelist:%s"%moduleList)
        if moduleList is None:
            moduleList = {}
        if baseList is None:
            baseList = {}

        self._logger.debug("findmodules in %s, depth %s" % (path, repr(depth)))

        # ok search for files up to the requested depth, BUT, __init__ files
        # are treated differently: they are depth+1 because searching e.g.
        # "j.core" we want to look for Jumpscale/core/__init__.py
        initfiles = j.sal.fs.listFilesInDir(
            path, recursive, "__init__.py", depth=depth + 1)
        pyfiles = j.sal.fs.listFilesInDir(path, recursive, "*.py",
                                               depth=depth)
        pyfiles = initfiles + pyfiles
        for classfile in pyfiles:
            #print("found", classfile)
            basename = j.sal.fs.getBaseName(classfile)
            if basename.startswith('__init__'):
                for classname, item in self.find_jslocations(
                        classfile).items():
                    #print ("found __init__", classfile, classname, item)
                    # hmm probably can use moduleList but not sure...
                    if "location" not in item:
                        continue
                    location = item["location"]
                    if location == 'j': # skip root j for now
                        continue
                    baseList[location] = classname

            if basename.startswith("_"):
                continue
            if "actioncontroller" in basename.lower():
                continue
            # look for files starting with Capital
            if str(basename[0]) != str(basename[0].upper()):
                continue

            for classname, item in self.find_jslocations(classfile).items():
                # item has "import" & "location" as key in the dict
                if "location" not in item:
                    continue
                location = item["location"]
                if location == 'j': # skip root j for now
                    continue
                if "import" in item:
                    imports = item["import"]
                else:
                    imports = []

                locRoot = ".".join(location.split(".")[:-1])
                locSubName = location.split(".")[-1]
                if locRoot not in moduleList:
                    moduleList[locRoot] = {}
                if return_relative:
                    # strip path off of front
                    classfile = remove_dir_part(classfile)
                item = (classfile, classname, imports)
                moduleList[locRoot][locSubName] = item

        return moduleList, baseList

    def removeEggs(self):
        for key, path in j.clients.git.getGitReposListLocal(
                account="jumpscale").items():
            for item in [item for item in j.sal.fs.listDirsInDir(
                    path) if item.find("egg-info") != -1]:
                j.sal.fs.remove(item)

    def generate(self, autocompletepath=None):
        """
        """
        self.generate_json()
        print ("GENERATE NOW DEPRECATED. DO NOT USE. IT IS CRITICAL TO")
        print ("DELETE /usr/lib/python3/dist-packages/jumpscale.py")
        # print ("PLEASE USE j.core.jsgenerator.generate()
        return
