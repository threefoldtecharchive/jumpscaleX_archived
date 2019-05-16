from Jumpscale import j

# import html

from data.capnp.ModelBase import ModelBase


class IssueModel(ModelBase):
    """
    Model Class for an Issue object
    """

    def index(self):
        i = self.collection.add2index(**self.to_dict())

    def _pre_save(self):
        # process the labels to our proper structure
        labels = [item for item in self.dbobj.labels]
        if labels != []:
            toremove = []
            for label in labels:
                if label.startswith("type_"):
                    toremove.append(label)
                    label = label[5:]
                    if label not in [
                        "unknown",
                        "alert",
                        "bug",
                        "doc",
                        "feature",
                        "incident",
                        "question",
                        "request",
                        "story",
                        "task",
                    ]:
                        label = "unknown"
                        toremove.pop()
                    self.dbobj.type = label
                elif label.startswith("priority_"):
                    toremove.append(label)
                    label = label[9:]
                    if label not in ["minor", "normal", "major", "critical"]:
                        label = "normal"
                        toremove.pop()
                    self.dbobj.priority = label
                elif label.startswith("state_"):
                    toremove.append(label)
                    label = label[6:]
                    if label not in ["new", "inprogress", "resolved", "wontfix", "question", "closed"]:
                        label = "new"
                        toremove.pop()
                    self.dbobj.state = label
            if self.dbobj.isClosed:
                self.dbobj.state = "closed"
            self.initSubItem("labels")
            for item in toremove:
                self.list_labels.pop(self.list_labels.index(item))
            self.reSerialize()
            content = self.dbobj.content
            content = html.escape(content)

    def gitHostRefSet(self, name, id):
        return j.clients.gogs._gitHostRefSet(self, name, id)

    def gitHostRefExists(self, name):
        return j.clients.gogs._gitHostRefExists(self, name)

    def gitHostRefGet(self, name):
        return j.clients.gogs._gitHostRefGet(self, name)

    def assigneeSet(self, key):
        """
        @param key is the unique key of the member
        """
        if key not in self.dbobj.assignees:
            self.addSubItem("assignees", key)
        self.changed = True

    def commentSet(self, comment, owner="", modTime=None):
        if owner is None:
            owner = ""
        for item in self.dbobj.comments:
            if item.comment != comment:
                item.comment == comment
                self.changed = True
            if item.owner != owner:
                item.owner == owner
                self.changed = True
            if modTime and item.modTime != modTime:
                item.modTime = modTime
                self.changed
            return
        obj = self.collection.list_comments_constructor(comment=comment, owner=owner)
        self.addSubItem("comments", obj)
        self.changed = True
