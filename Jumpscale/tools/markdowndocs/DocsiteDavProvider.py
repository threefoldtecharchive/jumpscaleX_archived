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

        self.obj = self.provider.get_by_path(self.path)

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

        obj = self.provider.get_by_path(path)
        if not obj:
            return None
        if obj.is_dir:
            return DirCollection(path, self.environ)
        else:
            return DocResource(path, self.environ, obj)

    def create_collection(self, name):
        dir = self._model.new()
        dir.is_dir = True
        path = j.sal.fs.joinPaths(self.path, name)
        dir.path = path
        dir.name = name
        dir.save()
        self.obj.children.append(name)
        self.obj.save()
        return True

    def handle_delete(self):
        parent_path = j.sal.fs.getDirName(self.path).rstrip("/")
        parent = self.provider.get_by_path(parent_path)
        parent.children.remove(self.obj.name)
        parent.save()
        for name in self.get_member_names():
            member = self.get_member(name)
            member.delete()
        self.obj.delete()
        return True

    def support_recursive_delete(self):
        return True

    def create_empty_resource(self, name):
        self.obj.children.append(name)
        self.obj.save()
        new_obj = self._model.new()
        new_obj.name = name
        new_obj.path = j.sal.fs.joinPaths(self.path, name)
        new_obj.is_dir = False
        new_obj.save()
        return self.get_member(name)


TMP_DIR = "/tmp/dav_tmp"
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
        parent_path = j.sal.fs.getDirName(self.vfile.path).rstrip("/")
        parent = self.provider.get_by_path(parent_path)
        parent.children.remove(self.vfile.name)
        parent.save()
        return True

    def begin_write(self, content_type=None):
        j.sal.fs.createEmptyFile(TMP_DIR)
        j.sal.fs.writeFile(TMP_DIR, self.vfile.content)
        return open(TMP_DIR, "wb")


    def end_write(self, with_errors):
        if j.sal.fs.exists(TMP_DIR):
            new_content = j.sal.fs.readFile(TMP_DIR)
            self.vfile.content = new_content
            self.vfile.save()
            j.sal.fs.remove(TMP_DIR)

    def copy_move_single(self, dest_path, is_move):
        new_obj = self.provider._model.new()
        new_obj.path = dest_path
        new_obj.name = j.sal.fs.getBaseName(dest_path)
        new_obj.content = self.vfile.content
        new_obj.is_dir = False
        new_obj.save()
        new_parent_path = j.sal.fs.getDirName(dest_path).rstrip("/") or "/"
        parent = self.provider.get_by_path(new_parent_path)
        parent.children.append(new_obj.name)
        if is_move:
            self.delete()
        return True


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

    def get_by_path(self, path):

        res = self._model.find(path=path)
        if len(res) == 1:
            print("> found one object with path: {}".format(path))
            return res[0]
        elif len(res) > 1:
            print("> found more the one object with path: {}".format(path))
            return res
        else:
            print("> can't find objects for {}".format(path))
            return None

