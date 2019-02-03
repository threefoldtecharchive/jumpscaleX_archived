from Jumpscale import j
#GENERATED CODE, can now change


class ACL_index:

    def _init_index(self):
        self.index = None

    
    def index_keys_set(self,obj):
        val = obj.hash
        if val not in ["",None]:
            val=str(val)
            # self._log_debug("key:hash:%s:%s"%(val,obj.id))
            self._index_key_set("hash",val,obj.id)

    def index_keys_delete(self,obj):
        val = obj.hash
        if val not in ["",None]:
            val=str(val)
            self._log_debug("delete key:hash:%s:%s"%(val,obj.id))
            self._index_key_delete("hash",val,obj.id)
    def get_by_hash(self,hash):
        return self.get_from_keys(hash=hash)
