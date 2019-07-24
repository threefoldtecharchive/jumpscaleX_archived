from Jumpscale import j


class FILE(j.data.bcdb._BCDBModelClass):
    def _schema_get(self):
        return j.data.schema.get_from_url_latest("jumpscale.bcdb.fs.file.2")

    def _text_index_content_pre_(self, property_name, val, obj_id, nid=1):
        """

        :return: text


        text e.g. : color__red ftype__doc importance__1

        """
        obj = self.get(obj_id)
        out = ""
        if property_name == "tags":
            for tag in obj.tags:
                out += tag.replace(":", "__") + " "
        # Add more meta data as tags
        type = str(obj.type).lower()
        if type:
            out += "type__%s " % type
        ext = str(obj.extension).lower()
        if ext:
            out += "ext__%s " % ext
        return property_name, out, obj_id, nid

    def files_search(
        self,
        type=None,
        tags=None,
        content=None,
        description=None,
        extension=None,
    ):
        # import ipdb;ipdb.set_trace()
        return list(
            self.do_search(**dict(type=type, tags=tags, extension=extension, content=content, description=description))
        )

    def do_search(self, **kwargs):
        if not kwargs:
            return None

        key, value = kwargs.popitem()
        if not value:
            return self.do_search(**kwargs)

        if key == "tags":
            value = value.replace(":", "__")
        if key == "type":
            key = "tags"
            value = "type__%s" % value.lower()

        if key == "extension":
            key = "tags"
            value = "ext__%s" % value.lower()

        res = self.search(value, property_name=key)
        next = self.do_search(**kwargs)
        if next is not None and res:
            return set(res).intersection(next)
        else:
            return set(res)


