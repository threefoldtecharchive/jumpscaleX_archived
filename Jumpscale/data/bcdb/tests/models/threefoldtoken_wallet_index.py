from Jumpscale import j
#GENERATED CODE, can now change


class threefoldtoken_wallet_index:

    def _init_index(self):
        pass #to make sure works if no index
        self._logger.info("init index:%s"%self.schema.url)

        p = j.clients.peewee

        db = self.bcdb.sqlclient.sqlitedb
        # print(db)

        class BaseModel(p.Model):
            class Meta:
                print("*%s"%db)
                database = db

        class Index_threefoldtoken_wallet(BaseModel):
            id = p.IntegerField(unique=True)
            addr = p.TextField(index=True)

        self.index = Index_threefoldtoken_wallet
        self.index.create_table(safe=True)

    
    def index_set(self,obj):
        idict={}
        idict["addr"] = obj.addr
        idict["id"] = obj.id
        if not self.index.select().where(self.index.id == obj.id).count()==0:
            #need to delete previous record from index
            self.index.delete().where(self.index.id == obj.id).execute()
        self.index.insert(**idict).execute()

    
    def index_keys_set(self,obj):
        val = obj.addr_key
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:addr_key:%s:%s"%(val,obj.id))
            self._set_key("addr_key",val,obj.id)
    def get_by_addr_key(self,addr_key):
        return self.get_from_keys(addr_key=addr_key)