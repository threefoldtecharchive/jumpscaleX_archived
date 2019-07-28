from Jumpscale import j


class DIR(j.data.bcdb._BCDBModelClass):
    def _schema_get(self):
        return j.data.schema.get_from_url_latest("jumpscale.bcdb.fs.dir.2")

    _file_model_ = None
    @property
    def _file_model(self):
        if not self._file_model_:
            self._file_model_ = self.bcdb.model_get_from_url("jumpscale.bcdb.fs.file.2")
        return self._file_model_

    def create_empty_dir(self, name):
        new_dir = self.new()
        new_dir.name = j.sal.fs.joinPaths(new_dir.name, name)
        new_dir.save()
        new_dir.dirs.append(new_dir.id)
        new_dir.save()
        return new_dir

    def delete_recursive(self, name):
        dir = self.find(name=name)[0]
        for file_id in dir.files:
            self._file_model.get(file_id).delete()

        for dir_id in dir.dirs:
            self.get(dir_id).delete_recursive()

        dir.delete()
