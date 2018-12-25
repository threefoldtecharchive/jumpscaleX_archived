from Jumpscale import j
#GENERATED CODE, can now change


class threefoldtoken_wallet_index:

    def _init_index(self):
        self.index = None

    
    def index_keys_set(self,obj):
        val = obj.addr
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:addr:%s:%s"%(val,obj.id))
            self._set_key("addr",val,obj.id)

    def index_keys_delete(self,obj):
        val = obj.addr
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:addr:%s:%s"%(val,obj.id))
            self._delete_key("addr",val,obj.id)
    def get_by_addr(self,addr):
        return self.get_from_keys(addr=addr)