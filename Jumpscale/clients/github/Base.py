from Jumpscale import j

replacelabels = {
    "bug": "type_bug",
    "duplicate": "process_duplicate",
    "enhancement": "type_feature",
    "help wanted": "state_question",
    "invalid": "state_question",
    "question": "state_question",
    "wontfix": "process_wontfix",
    "completed": "state_verification",
    "in progress": "state_inprogress",
    "ready": "state_verification",
    "story": "type_story",
    "urgent": "priority_urgent",
    "type_bug": "type_unknown",
    "type_story": "type_unknown",
}

JSBASE = j.application.JSBaseClass


class Base(j.application.JSBaseClass):
    def __init__(self):
        JSBASE.__init__(self)

    @property
    def bodyWithoutTags(self):
        # remove the tag lines from the body
        out = ""
        if self.body is None:
            return ""
        for line in self.body.split("\n"):
            if line.startswith("##") and not line.startswith("###"):
                continue
            out += "%s\n" % line

        out = out.rstrip() + "\n"
        return out

    @property
    def tags(self):
        if "_tags" not in self.__dict__:
            lineAll = ""
            if self.body is None:
                self._tags = j.data.tags.getObject("")
                return self._tags
            for line in self.body.split("\n"):
                # look for multiple lines, append and then transform to tags
                if line.startswith(".. ") and not line.startswith("..."):
                    line0 = line[2:].strip()
                    lineAll += "%s " % line0
            self._tags = j.data.tags.getObject(lineAll)
        return self._tags

    @tags.setter
    def tags(self, ddict):
        if j.data.types.dict(ddict) is False:
            raise j.exceptions.Input("Tags need to be dict as input for setter, now:%s" % ddict)

        keys = sorted(ddict.keys())

        out = self.bodyWithoutTags + "\n"
        for key, val in ddict.items():
            out += ".. %s:%s\n" % (key, val)

        self.body = out
        return self.tags

    def __str__(self):
        return str(self._ddict)

    __repr__ = __str__
