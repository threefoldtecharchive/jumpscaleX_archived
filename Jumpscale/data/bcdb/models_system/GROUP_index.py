from Jumpscale import j
#GENERATED CODE, can now change


class GROUP_index:

    def _init_index(self):
        pass #to make sure works if no index

    
    def index_keys_set(self,obj):
        val = obj.name
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:name:%s:%s"%(val,obj.id))
            self._set_key("name",val,obj.id)
        val = obj.dm_id
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:dm_id:%s:%s"%(val,obj.id))
            self._set_key("dm_id",val,obj.id)
        val = obj.email
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:email:%s:%s"%(val,obj.id))
            self._set_key("email",val,obj.id)
    def get_by_name(self,name):
        return self.get_from_keys(name=name)
    def get_by_dm_id(self,dm_id):
        return self.get_from_keys(dm_id=dm_id)
    def get_by_email(self,email):
        return self.get_from_keys(email=email)