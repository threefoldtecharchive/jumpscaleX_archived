from Jumpscale import j
from wsgidav import compat, util
from wsgidav.dav_provider import DAVCollection, DAVNonCollection, DAVProvider


class DirCollection(DAVCollection):
    """
    Handles all kinds of directory-like resources
    """

    def __init__(self, path, environ):
        DAVCollection.__init__(self, path, environ)
        self._model = self.provider._model
        self.obj = self._model.find(path=self.path)[0]
    def get_member_names(self):
        """
        get member names to be listed from the path
        :return: list of member names
        """
        children_paths = [child for child in self.obj.children]
        names = [child.split("/")[-1] for child in children_paths]
        return names

    def get_member(self, name):
        """
        get member by name
        :param name: member name
        :return: DirCollection if the member is a dir-like or DocResource if the member is a doc
        """

        path = j.sal.fs.joinPaths(self.path, name)
        obj = self._model.find(path=path)[0]
        if obj.is_dir:
            return DirCollection(path, self.environ)
        else:
            return DocResource(path, self.environ, obj)

    def create_collection(self, name):
        dir = self.model.new()
        dir.is_dir = True
        path = j.sal.fs.joinPaths(self.path, name)
        dir.path = path
        dir.name = name
        dir.save()
        self.obj.children.append(path)
        return True

    def create_empty_resource(self, name):
        pass



class DocResource(DAVNonCollection):
    """
    Handles docs. a doc is bcdb data object treated like a documentation
    """

    def __init__(self, path, environ, vfile):
        DAVNonCollection.__init__(self, path, environ)
        self.vfile = vfile
        self.content = vfile.content
        self._title = vfile.name

    @property
    def title(self):
        return self._title

    def get_content(self):
        html = self.content
        return compat.BytesIO(html.encode("utf-8"))

    def get_content_length(self):
        return len(self.get_content().read())

    def get_content_type(self):
        return self.vfile.content_type

    def get_display_name(self):
        return compat.to_native(self.title)

    def get_display_info(self):
        return {"type": self.vfile.content_type}

    def handle_delete(self):
        self.vfile.delete()

    def handle_copy(self, dest_path, depth_infinity):
       pass

    def begin_write(self, content_type=None):
        pass

    def end_write(self, with_errors):
        pass

    def handle_move(self, dest_path):
        pass



RESOURCE_MODEL_URL = "threebot.docsites.resource"

class DocsteDavProvider(DAVProvider):
    def __init__(self, bcdb_name):
        DAVProvider.__init__(self)
        self._bcdb = j.data.bcdb.get(bcdb_name)
        self._model = self._bcdb.model_get_from_url(RESOURCE_MODEL_URL)

    def get_resource_inst(self, path, environ):
        """
        Return DAVResource object for path.
        """
        root = DirCollection("/", environ)
        return root.resolve("/", path)
