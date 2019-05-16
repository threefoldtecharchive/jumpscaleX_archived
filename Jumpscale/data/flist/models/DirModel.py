from Jumpscale import j

from data.capnp.ModelBase import ModelBase


class DirModel(ModelBase):
    """
    Model Class for an Issue object
    """

    def index(self):
        pass

    def fileExists(self, name):
        return not self.fileGet(name) is None

    def fileSpecialExists(self, name):
        return not self.get(name, "special") is None

    def linkExists(self, name):
        return not self.get(name, "link") is None

    def get(self, name, type_):
        """
        Get file/link/specialfile object
        """
        for item in self.dbobj.contents:
            which = item.attributes.which()
            if which != type_:
                continue
            if name == item.name:
                return item
        return None

    def fileGet(self, name):
        return self.get(name=name, type_="file")

    def fileReplace(self, file_obj, create=True):
        """
        Replace a file object in the directory with the provided file
        """
        changed = False
        attrs = ("name", "size", "aclkey", "modificationTime", "creationTime")
        current_file = self.fileGet(file_obj.name)
        if current_file is not None:
            if current_file.modificationTime < file_obj.modificationTime:
                changed = True
                for attr in attrs:
                    current_file.__setattr__(attr, file_obj.__getattr__(attr))
        else:
            if create:
                changed = True
                # add new file inode in the current directory
                self.addSubItem("contents", file_obj)
        if changed:
            self.reSerialize()
            self.save()

    def filesNew(self, nr):
        newlist = self.dbobj.init("files", nr)
        return newlist

    def getTypeId(self):
        pass
        # if S_ISSOCK(value):
        #     self.data[6] = 0
        #
        # elif S_ISLNK(value):
        #     self.data[6] = 1
        #
        # elif S_ISBLK(value):
        #     self.data[6] = 3
        #
        # elif S_ISCHR(value):
        #     self.data[6] = 5
        #
        # elif S_ISFIFO(value):
        #     self.data[6] = 6
        #
        # # keep track of empty directories
        # elif S_ISDIR(value):
        #     self.data[6] = 4

    def setParent(self, parentObj):
        self.dbobj.parent = parentObj.key

    @property
    def dictFiltered(self):
        ddict = self.dbobj.to_dict()
        for item in ddict.get("specials", []):
            if "data" in item:
                item["data"] = binascii.hexlify(item["data"])
        return ddict

    @dictFiltered.setter
    def dictFiltered(self, ddict):
        for item in ddict.get("specials", []):
            if "data" in item:
                item["data"] = binascii.unhexlify(item["data"])
        self.dbobj = self._capnp_schema.new_message(**ddict)
        for item in self.dbobj.specials:
            item.data = b"%s" % item.data

    def _pre_save(self):
        pass
