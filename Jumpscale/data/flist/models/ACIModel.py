from data.capnp.ModelBase import ModelBase


class ACIModel(ModelBase):
    """
    class for ACL item = Access Control Item
    """

    @property
    def key(self):
        if self._key == "":
            self._key = j.data.hash.md5_string(self.getAsText())
        return self._key

    @property
    def id(self):
        # if self.dbobj.id == 0:
        #     raise j.exceptions.Base("id cannot be 0")
        return self.dbobj.id

    def index(self):
        pass

    def getAsText(self, withUserNames=False):
        out = "user:%s\ngroup:%s\n" % (self.dbobj.uname, self.dbobj.gname)
        out += "mode:%s\n" % oct(self.dbobj.mode)[4:]
        out2 = []
        for right in self.dbobj.rights:
            out2.append("%s|%s" % (right.usergroupid, sorted(right.right)))
        out2.sort()
        out += "\n".join(out2)
        out = out.rstrip() + "\n"
        return out

    @property
    def text(self):
        return self.getAsText()

    @property
    def modeInOctFormat(self):
        return oct(self.dbobj.mode)[4:]
