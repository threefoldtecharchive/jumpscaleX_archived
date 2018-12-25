from Jumpscale import j
#GENERATED CODE, can now change


class threefoldtoken_order_buy_index:

    def _init_index(self):
        self.index = None

    
    def index_keys_set(self,obj):
        val = obj.currency_to_buy
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:currency_to_buy:%s:%s"%(val,obj.id))
            self._set_key("currency_to_buy",val,obj.id)
        val = obj.price_max
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:price_max:%s:%s"%(val,obj.id))
            self._set_key("price_max",val,obj.id)
        val = obj.amount
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:amount:%s:%s"%(val,obj.id))
            self._set_key("amount",val,obj.id)
        val = obj.expiration
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:expiration:%s:%s"%(val,obj.id))
            self._set_key("expiration",val,obj.id)
        val = obj.approved
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:approved:%s:%s"%(val,obj.id))
            self._set_key("approved",val,obj.id)
        val = obj.wallet_addr
        if val not in ["",None]:
            val=str(val)
            # self._logger.debug("key:wallet_addr:%s:%s"%(val,obj.id))
            self._set_key("wallet_addr",val,obj.id)

    def index_keys_delete(self,obj):
        val = obj.currency_to_buy
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:currency_to_buy:%s:%s"%(val,obj.id))
            self._delete_key("currency_to_buy",val,obj.id)
        val = obj.price_max
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:price_max:%s:%s"%(val,obj.id))
            self._delete_key("price_max",val,obj.id)
        val = obj.amount
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:amount:%s:%s"%(val,obj.id))
            self._delete_key("amount",val,obj.id)
        val = obj.expiration
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:expiration:%s:%s"%(val,obj.id))
            self._delete_key("expiration",val,obj.id)
        val = obj.approved
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:approved:%s:%s"%(val,obj.id))
            self._delete_key("approved",val,obj.id)
        val = obj.wallet_addr
        if val not in ["",None]:
            val=str(val)
            self._logger.debug("delete key:wallet_addr:%s:%s"%(val,obj.id))
            self._delete_key("wallet_addr",val,obj.id)
    def get_by_currency_to_buy(self,currency_to_buy):
        return self.get_from_keys(currency_to_buy=currency_to_buy)
    def get_by_price_max(self,price_max):
        return self.get_from_keys(price_max=price_max)
    def get_by_amount(self,amount):
        return self.get_from_keys(amount=amount)
    def get_by_expiration(self,expiration):
        return self.get_from_keys(expiration=expiration)
    def get_by_approved(self,approved):
        return self.get_from_keys(approved=approved)
    def get_by_wallet_addr(self,wallet_addr):
        return self.get_from_keys(wallet_addr=wallet_addr)