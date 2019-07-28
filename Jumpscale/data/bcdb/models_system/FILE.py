from Jumpscale import j
from wsgidav import compat
import mimetypes


class FILE(j.data.bcdb._BCDBModelClass):
    def _schema_get(self):
        return j.data.schema.get_from_url_latest("jumpscale.bcdb.fs.file.2")

    _dir_model_ = None

    @property
    def _dir_model(self):
        if not self._dir_model_:
            self._dir_model_ = self.bcdb.model_get_from_url("jumpscale.bcdb.fs.dir.2")
        return self._dir_model_

    _block_model_ = None

    @property
    def _block_model(self):
        if not self._block_model_:
            self._block_model_ = self.bcdb.model_get_from_url("jumpscale.bcdb.fs.block.2")
        return self._block_model_

    def _text_index_content_pre_(self, property_name, val, obj_id, nid=1):
        """

        :return: text


        text e.g. : color__red ftype__doc importance__1

        """
        if property_name == "tags":
            obj = self.get(obj_id)
            out = ""
            for tag in obj.tags:
                out += tag.replace(":", "__") + " "
            # Add more meta data as tags
            type = str(obj.type).lower()
            if type:
                out += "type__%s " % type
            ext = str(obj.extension).lower()
            if ext:
                out += "ext__%s " % ext
            val = out
        return property_name, val, obj_id, nid

    def files_search(self, type=None, tags=None, content=None, description=None, extension=None):
        return list(
            self._do_search(**dict(type=type, tags=tags, extension=extension, content=content, description=description))
        )

    def _do_search(self, **kwargs):
        if not kwargs:
            return None

        key, value = kwargs.popitem()
        if not value:
            return self._do_search(**kwargs)

        if key == "tags":
            value = value.replace(":", "__")
        if key == "type":
            key = "tags"
            value = "type__%s" % value.lower()

        if key == "extension":
            key = "tags"
            value = "ext__%s" % value.lower()

        res = self.search(value, property_name=key)
        next = self._do_search(**kwargs)
        if next is not None and res:
            return set(res).intersection(next)
        else:
            return set(res)

    def filestream_get(self, vfile, model):
        return FileStream(vfile, model)

    def file_create_empty(self, name):
        """
        create new file inside a directory
        :param name: file name
        :return: file object
        """
        new_file = self.new()
        new_file.name = name
        new_file.save()
        dir = self._dir_model.find(name=j.sal.fs.getParent(name))[0]
        dir.files.append(new_file.id)
        dir.save()
        return new_file

    def file_write(self, path, content, append=True, create=True):
        """
        writes a file to bcdb
        :param path: the path to store the file
        :param content: content of the file to be written
        :param append: if True will append if the file already exists
        :param create: create new if true and the file doesn't exist
        :return: file object
        """
        try:
            file = self.find(name=path)[0]
        except:
            if not create:
                raise RuntimeError(
                    "file with path {} doesn't exist, if you want to create it pass create = True".format(path)
                )
            file = self.file_create_empty(path)
        fs = FileStream(file, self._block_model)
        fs.writelines(content, append=append)
        return file

    def file_delete(self, path):
        file = self.find(name=path)[0]
        file.delete()
        parent = self._dir_model.find(name=j.sal.fs.getDirName(path))[0]
        parent.files.delete(file.id)
        parent.save()


class FileStream:
    # plain types are the the file types that will be stored as plain text in content
    # other types will be saved in blocks
    PLAIN_TYPES = ["md", "txt", "json", "toml"]

    def __init__(self, vfile, model):
        self._vfile = vfile
        self._block_model = model

    def writelines(self, stream, append=True):
        ext = self._vfile.extension or self._vfile.name.split(".")[-1]
        if ext in self.PLAIN_TYPES:
            self._save_plain(stream, append=append)
        else:
            self._save_blocks(stream, append=append)

        if not self._vfile.extension and ext:
            self._vfile.extension = ext
            self._vfile.save()

    def _save_blocks(self, stream, append=True):
        if not append:
            self._vfile.blocks = []
            self._vfile.save()
        for block in stream:
            hash = j.data.hash.md5_string(block)
            exists = self._block_model.find(md5=hash)
            if exists:
                b = exists[0]
            else:
                b = self._block_model.new()
                b.md5 = hash
                b.content = block
                b.size = len(block)
                b.epoch = j.data.time.epoch
                b.save()
            self._vfile.size_bytes += b.size
            self._vfile.blocks.append(b.id)

    def _save_plain(self, stream, append=True):
        if append:
            content = self._vfile.content
        else:
            content = ""
        self._vfile.content = content + "\n".join([line for line in stream])
        self._vfile.size_bytes = len(self._vfile.content.encode())

    def read_stream_get(self):
        if self._vfile.content:
            ret = compat.BytesIO()
            ret.write(self._vfile.content.encode())
            ret.seek(0)
            return ret
        elif self._vfile.blocks:
            ret = compat.BytesIO()
            for block_id in self._vfile.blocks:
                ret.write(self._block_model.get(block_id).content)
            ret.seek(0)
            return ret
        else:
            return compat.BytesIO()

    def close(self):
        self._vfile.epoch = j.data.time.epoch
        self._vfile.content_type = mimetypes.guess_type(self._vfile.name)[0] or "text/plain"
        self._vfile.save()
