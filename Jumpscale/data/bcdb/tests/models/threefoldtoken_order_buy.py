from Jumpscale import j
#GENERATED CODE CAN CHANGE

SCHEMA="""
@url = threefoldtoken.order.buy
@name = orderbuy
comment = ""
currency_to_buy** = "" (S)    # currency types BTC/ETH/XRP/TFT
currency_mine = (LS)        # which of my currencies I am selling (can be more than 1)
price_max** =  (N)           # can be defined in any currency
amount** = (F)                # amount
expiration** =  (D)           # can be defined as e.g. +1h
buy_from = (LS)             # list of wallet addresses which I want to buy from
secret = "" (S)             # the optional secret to use when doing a buy order, only relevant when buy_from used
approved** = (B)              # if True, object will be scheduled for matching, further updates/deletes are no more possible
owner_email_addr = (S)      # email addr used through IYO when order was created
wallet_addr** = (S)           # Wallet address


"""

bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)

Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema,__file__)
MODEL_CLASS = bcdb._BCDBModelClass


class threefoldtoken_order_buy(Index_CLASS,MODEL_CLASS):
    def __init__(self,bcdb,schema,reset=False):
        MODEL_CLASS.__init__(self, bcdb=bcdb,schema=schema,reset=reset)
        self.write_once = False
        self._init()