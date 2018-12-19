from Jumpscale import j
#GENERATED CODE, can now change


class jumpscale_bcdb_test_house_index:

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

        class Index_jumpscale_bcdb_test_house(BaseModel):
            id = p.IntegerField(unique=True)
            name = p.TextField(index=True)
            active = p.BooleanField(index=True)
            cost = p.FloatField(index=True)

        self.index = Index_jumpscale_bcdb_test_house
        self.index.create_table(safe=True)

    
    def index_set(self,obj):
        idict={}
        idict["name"] = obj.name
        idict["active"] = obj.active
        idict["cost"] = obj.cost_usd
        idict["id"] = obj.id
        if not self.index.select().where(self.index.id == obj.id).count()==0:
            #need to delete previous record from index
            self.index.delete().where(self.index.id == obj.id).execute()
        self.index.insert(**idict).execute()

    