from Jumpscale import j
from wsgidav import compat, util
from wsgidav.dav_provider import DAVCollection, DAVNonCollection, DAVProvider

class DirCollection(DAVCollection):
    """Root collection, lists all bcdbs"""

    def __init__(self, path, environ):
        DAVCollection.__init__(self, path, environ)
        self.vfs = self.provider.vfs

    def get_member_names(self):
        # import ipdb; ipdb.set_trace()
        return [name.get() for name in self.vfs.list(self.path)]

    def get_member(self, name):
        path = j.sal.fs.joinPaths(self.path, name)
        if self.vfs.is_dir(path):
            return DirCollection(path, self.environ)
        else:
            return DocResource(path, self.environ, self.vfs.get(path))

class DocResource(DAVNonCollection):

    def __init__(self, path, environ, doc):
        DAVNonCollection.__init__(self, path, environ)
        self.doc = doc

    def get_content(self):
        html = "<pre>" + self.doc.get() + "</pre>"
        return compat.StringIO(html.encode("utf8"))

    def get_content_length(self):
        return len(self.get_content().read())

    def get_content_type(self):
        return "text/html"

    def get_display_name(self):
        return compat.to_native(self.doc.key)

    def get_display_info(self):
        return {"type": "BCDB Model"}


class BCDBResourceProvider(DAVProvider):

    def __init__(self):
        DAVProvider.__init__(self)
        # self.vfs = j.data.bcdb.vfs_get()
        self.vfs = FakeVFS()
    def get_resource_inst(self, path, environ):
        """Return DAVResource object for path.

        """
        root = DirCollection("/", environ)
        return root.resolve("/", path)