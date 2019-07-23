from Jumpscale import j


class FILE(j.data.bcdb._BCDBModelClass):
    def _schema_get(self):
        return j.data.schema.get_from_url_latest("jumpscale.bcdb.fs.file.2")

    def _index_pre_text(self):
        """

        :return: [(object,text)]


        text e.g. : color__red ftype__doc importance__1

        """
        out = ""
        for tag in self.tags:
            if ":" in tag:
                splitted = tag.split(":")
                assert splitted == 2
                pre, post = splitted
            else:
                pre = "-"
                post = tag

            pre = pre.strip().lower()
            post = post.strip().lower()
            out += "'%s:%s" % (pre, post)
        post = str(self.type).lower()
        out += "typef__%s" % (post)
        ext = str(self.ext).lower()
        out += "extf__%s" % (ext)
        return ("file_meta", out)

    def search(
        self,
        dir_path=None,
        type=None,
        tags=None,
        from_epoch=None,
        to_epoch=None,
        content=None,
        description=None,
        extension=None,
    ):
        if not tags:
            tags = []
