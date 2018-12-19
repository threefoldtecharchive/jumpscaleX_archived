from Jumpscale import j

JSBASE = j.application.JSBaseClass


class TreeItem(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)
        self.id = ""
        self.description = ""
        self.path = ""
        self.item = None
        self.changed = False
        self.tree = None
        self.cat = None
        self.selected = False
        self.deleted = False
        self.data = None

    @property
    def parent(self):
        if "." in self.path:
            pathParent = ".".join(self.path.split(".")[:-1])
            return self.tree.items[pathParent]

    @property
    def name(self):
        return self.path.split(".")[-1]

    @property
    def children(self):
        r = []
        depth = self.path.count(".")
        for key, val in self.tree.items.items():
            if key.startswith(self.path):
                depth2 = val.path.count(".")
                if depth2 == depth + 1:
                    r.append(val)
        return r

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.selected == True:
            selected = "X"
        else:
            selected = " "
        cat = "%s" % self.cat
        return ("%-60s  %-20s  [%s]" % (self.path, cat, selected))


class Tree(JSBASE):

    def __init__(self, data=None):
        JSBASE.__init__(self)
        self.items = {}
        self.changed = False
        self.set("")  # will set the root
        if data != None:
            self.loads(data)

    @property
    def children(self):
        return self.items[""].children

    def _pathNormalize(self, path):
        path = path.strip()
        return path

    def setDeleteState(self, state=True):
        for key in self.items.keys():
            self.items[key].deleted = state

    def getDeletedItems(self):
        res = []
        for key in self.items.keys():
            item = self.items[key]
            if item.deleted and item.path != "":
                res.append(item)
        return res

    def removeDeletedItems(self):
        res = self.getDeletedItems()
        for item in res:
            self.items.pop(item.path)

        return res

    def exists(self, path):
        path = self._pathNormalize(path)
        return path in self.items

    def set(self, path, id=None, cat=None, selected=None, description=None, item=None, data=None):
        """
        @param item, item is any object you want to remember but keep in mind that this will not be serialized
        @path is dot separated path e.g. root.child.childsub
        """

        path = self._pathNormalize(path)
        if path not in self.items:
            self.items[path] = TreeItem()

        ti = self.items[path]

        if path == "":
            self.root = ti

        if id is not None and ti.id != id:
            ti.id = id
            ti.changed = True
        if description is not None and ti.description != description:
            ti.description = description
            ti.changed = True
        if item is not None and ti.item != item:
            ti.item = item
            ti.changed = True
        if cat is not None and ti.cat != cat:
            ti.cat = cat
            ti.changed = True
        if selected is not None and selected is not ti.selected:
            ti.selected = selected
            ti.change = True
        if data is not None and data is not ti.data:
            ti.data = data
            ti.change = True

        ti.path = path
        ti.tree = self

        ti.deleted = False

        if ti.changed:
            self.changed = True

    def dumps(self):
        r = []
        for key, val in self.items.items():
            cat = val.cat or ""
            id = val.id or ""
            data = val.data or ""
            description = val.description or ""
            if val.selected:
                selected = "1"
            else:
                selected = "0"
            line = "%s:%s:%s:%s:%s:%s" % (
                val.path, cat, id, selected, description, data)
            r.append(line)
        r.sort()

        out = ""
        for line in r:
            out += "%s\n" % line

        return out

    def loads(self, data):
        lines = [line for line in data.split("\n") if line.strip(
        ) is not "" and not line.strip().startswith("#")]
        lines.sort()
        self.items = {}
        self.set(path="")
        for line in lines:
            path, cat, id, selected, descr, data = line.split(":")
            selected = selected.strip().casefold() == "true" or selected.strip().casefold() == "1"
            path = path.strip()

            id = id.strip()
            if id == "":
                id = None

            cat = cat.strip()
            if cat == "":
                cat = None

            data = data.strip()
            if data == "":
                data = None

            descr = descr.strip()
            if descr == "":
                descr = None
            if cat == "":
                cat = None
            self.set(path=path, id=id, cat=cat, description=descr,
                     item=None, selected=selected, data=data)

    def find(self, partOfPath="", maxAmount=400, getItems=False, selected=None, cat=None):
        """
        @param if getItems True then will return the items in the treeobj
        """
        r = []
        for key in self.items.keys():
            if key.find(partOfPath) != -1:
                r.append(self.items[key])

        if len(r) == 0:
            raise j.exceptions.Input(
                "could not find %s in %s" % (partOfPath, self))

        if len(r) > maxAmount:
            raise j.exceptions.Input(
                "found more than %s %s in %s" % (maxAmount, partOfPath, self))

        if getItems:
            r = [item.item for item in r if item.item is not None]

        if selected is not None:
            r = [item for item in r if item.selected == selected]

        if cat is not None:
            r = [item for item in r if item.cat == cat]

        return r

    def findOne(self, path, getItems=False):
        for key in self.items.keys():
            if key == path:
                return self.items[key]
        raise j.exceptions.Input("could not find %s in \n%s" % (path, self))

    def findByName(self, name, die=True):
        for item in self.find():
            if item.name == name:
                return item
        if die:
            raise j.exceptions.Input(
                "could not find %s in \n%s" % (name, self))
        else:
            return None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        out = ""
        for item, val in self.items.items():
            out += "%s\n" % val

        return (out)


class TreemanagerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.treemanager"
        JSBASE.__init__(self)

    def get(self, data=""):
        return Tree(data=data)

    def _test(self):

        t = self.get()
        t.set("root.test", id="1", cat="acat", selected=False,
              description="my descriptio1n", item=None)
        t.set("root.test.sub", id="2", cat="acat", selected=True,
              description="my description2", item=None)
        t.set("root.test2.sub", id="3", cat="acat2", selected=False,
              description="my description3", item=None)
        t.set("root", id="4", cat="acat", selected=True,
              description="my description4", item=None)

        dumped = t.dumps()

        self._logger.debug(dumped)

        t2 = self.get(dumped)

        ee = t2.findOne("root.test.sub")
        assert ee.id == "2"
        assert ee.selected == True
        assert ee.description == "my description2"

        ee = t2.find("root.test.sub", maxAmount=200,
                     getItems=False, selected=None)[0]
        assert ee.id == "2"
        assert ee.selected == True

        ee = t2.findOne("root.test")
        assert ee.id == "1"
        assert ee.selected == False

        ee = t2.find("", maxAmount=200, getItems=False, selected=True)
        assert len(ee) == 2

        self._logger.debug("TEST OK")
