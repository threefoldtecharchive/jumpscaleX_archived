from Jumpscale import j
#GENERATED CODE, can now change


class threefoldtoken_order_sell_index:

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

        class Index_threefoldtoken_order_sell(BaseModel):
            id = p.IntegerField(unique=True)
            currency_to_sell = p.TextField(index=True)
            price_min = p.FloatField(index=True)
            amount = p.FloatField(index=True)
            expiration = p.IntegerField(index=True)
            approved = p.BooleanField(index=True)
            wallet_addr = p.TextField(index=True)

        self.index = Index_threefoldtoken_order_sell
        self.index.create_table(safe=True)

    
    def index_set(self,obj):
        idict={}
        idict["currency_to_sell"] = obj.currency_to_sell
        idict["price_min"] = obj.price_min_usd
        idict["amount"] = obj.amount
        idict["expiration"] = obj.expiration
        idict["approved"] = obj.approved
        idict["wallet_addr"] = obj.wallet_addr
        idict["id"] = obj.id
        if not self.index.select().where(self.index.id == obj.id).count()==0:
            #need to delete previous record from index
            self.index.delete().where(self.index.id == obj.id).execute()
        self.index.insert(**idict).execute()

    