from Jumpscale import j

# GENERATED CODE, can now change


class GROUP_index:
    def _init_index(self):
        self.index = None

    def index_keys_set(self, obj):
        val = obj.name
        if val not in ["", None]:
            val = str(val)
            # self._log_debug("key:name:%s:%s"%(val,obj.id))
            self._index_key_set("name", val, obj.id)
        val = obj.dm_id
        if val not in ["", None]:
            val = str(val)
            # self._log_debug("key:dm_id:%s:%s"%(val,obj.id))
            self._index_key_set("dm_id", val, obj.id)
        val = obj.email
        if val not in ["", None]:
            val = str(val)
            # self._log_debug("key:email:%s:%s"%(val,obj.id))
            self._index_key_set("email", val, obj.id)

    def index_keys_delete(self, obj):
        val = obj.name
        if val not in ["", None]:
            val = str(val)
            self._log_debug("delete key:name:%s:%s" % (val, obj.id))
            self._index_key_delete("name", val, obj.id)
        val = obj.dm_id
        if val not in ["", None]:
            val = str(val)
            self._log_debug("delete key:dm_id:%s:%s" % (val, obj.id))
            self._index_key_delete("dm_id", val, obj.id)
        val = obj.email
        if val not in ["", None]:
            val = str(val)
            self._log_debug("delete key:email:%s:%s" % (val, obj.id))
            self._index_key_delete("email", val, obj.id)

    def get_by_name(self, name):
        return self.get_from_keys(name=name)

    def get_by_dm_id(self, dm_id):
        return self.get_from_keys(dm_id=dm_id)

    def get_by_email(self, email):
        return self.get_from_keys(email=email)
