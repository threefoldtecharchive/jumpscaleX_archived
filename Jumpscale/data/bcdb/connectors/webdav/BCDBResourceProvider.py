from Jumpscale import j
from wsgidav import compat, util
from wsgidav.dav_provider import DAVCollection, DAVNonCollection, DAVProvider


class DirCollection(DAVCollection):
    """
    Handles all kinds of directory-like resources
    """

    def __init__(self, path, environ):
        DAVCollection.__init__(self, path, environ)
        self.vfs = self.provider.vfs

    def get_member_names(self):
        """
        get member names to be listed from the path
        :return: list of member names
        """
        return [name for name in self.vfs.list(self.path)]

    def get_member(self, name):
        """
        get member by name
        :param name: member name
        :return: DirCollection if the member is a dir-like or DocResource if the member is a doc
        """
        path = j.sal.fs.joinPaths(self.path, name)

        # This to avoid returning 500 response if there was an error in bcdb returned data
        try:
            vfile = self.vfs.get(path)
        except Exception as e:
            return CorruptedResource(path, self.environ, str(e))

        if vfile.is_dir():
            return DirCollection(path, self.environ)
        else:
            return DocResource(path, self.environ, vfile)


class CorruptedResource(DAVNonCollection):
    """
    Represents a corrupted resource which could happen because of bcdb failure
    """
    def __init__(self, path, environ, error):
        DAVNonCollection.__init__(self, path, environ)
        self.path = path
        self.error = error

    def get_content(self):
        html = "<pre>" + self.error + "</pre>"
        return compat.BytesIO(html.encode("utf-8"))

    def get_content_length(self):
        return len(self.get_content().read())

    def get_content_type(self):
        return "text/html"

    def get_display_name(self):
        return compat.to_native(self.path + " --corrupted")

    def get_display_info(self):
        return {"type": "Corrupted resource"}


class DocResource(DAVNonCollection):
    """
    Handles docs. a doc is bcdb data object treated like a documentation
    """

    def __init__(self, path, environ, vfile):
        DAVNonCollection.__init__(self, path, environ)
        self.doc = vfile.get()

    def get_content(self):
        html = self.doc
        return compat.BytesIO(html.encode("utf-8"))

    def get_content_length(self):
        return len(self.get_content().read())

    def get_content_type(self):
        try:
            j.data.serializers.json.loads(self.doc)
            return "application/json"
        except:
            return "text/html"

    def get_display_name(self):
        return compat.to_native(self.doc)

    def get_display_info(self):
        return {"type": "resource"}


class BCDBResourceProvider(DAVProvider):
    def __init__(self):
        DAVProvider.__init__(self)
        self.vfs = j.data.bcdb._get_vfs()

    def get_resource_inst(self, path, environ):
        """
        Return DAVResource object for path.
        """
        root = DirCollection("/", environ)
        return root.resolve("/", path)
