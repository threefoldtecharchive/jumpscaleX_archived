from Jumpscale import j
#GENERATED CODE, can now change


class jumpscale_bcdb_test_house_index:

    def _init_index(self):
        self.index = None

    
    def index_keys_set(self,obj):
        val = obj.name
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:name:%s:%s"%(val,obj.id))
            self._set_key("name",val,obj.id)
        val = obj.active
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:active:%s:%s"%(val,obj.id))
            self._set_key("active",val,obj.id)
        val = obj.cost
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:cost:%s:%s"%(val,obj.id))
            self._set_key("cost",val,obj.id)

    def index_keys_delete(self,obj):
        val = obj.name
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:name:%s:%s"%(val,obj.id))
            self._delete_key("name",val,obj.id)
        val = obj.active
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:active:%s:%s"%(val,obj.id))
            self._delete_key("active",val,obj.id)
        val = obj.cost
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:cost:%s:%s"%(val,obj.id))
            self._delete_key("cost",val,obj.id)
    def get_by_name(self,name):
        return self.get_from_keys(name=name)
    def get_by_active(self,active):
        return self.get_from_keys(active=active)
    def get_by_cost(self,cost):
        return self.get_from_keys(cost=cost)