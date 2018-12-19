from Jumpscale import j
#GENERATED CODE, can now change


class ACL_index:

    def _init_index(self):
        pass #to make sure works if no index

    
    def index_keys_set(self,obj):
        val = obj.hash
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:hash:%s:%s"%(val,obj.id))
            self._set_key("hash",val,obj.id)
    def get_by_hash(self,hash):
        return self.get_from_keys(hash=hash)