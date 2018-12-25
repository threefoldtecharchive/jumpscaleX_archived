from Jumpscale import j
#GENERATED CODE, can now change


class ACL_index:

    def _init_index(self):
        self.index = None

    
    def index_keys_set(self,obj):
        val = obj.hash
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:hash:%s:%s"%(val,obj.id))
            self._set_key("hash",val,obj.id)

    def index_keys_delete(self,obj):
        val = obj.hash
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:hash:%s:%s"%(val,obj.id))
            self._delete_key("hash",val,obj.id)
    def get_by_hash(self,hash):
        return self.get_from_keys(hash=hash)