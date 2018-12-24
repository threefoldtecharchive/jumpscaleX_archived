from Jumpscale import j
#GENERATED CODE CAN CHANGE

SCHEMA="""
@url = threefoldtoken.order.sell
@name = ordersell
comment = ""
currency_to_sell* = "" (S)   # currency types BTC/ETH/XRP/TFT
currency_accept = (LS)      # can accept more than one currency
price_min* = 0 (N)           # can be defined in any currency
amount* = (F)                # amount
expiration* =  (D)           # can be defined as e.g. +1h
sell_to = (LS)              # list of wallet addresses which are allowed to buy from me
secret = (LS)               # if used the buyers need to have one of the secrets
approved* = (B)              # if True, object will be scheduled for matching, further updates/deletes are no more possible
owner_email_addr = (S)      # email addr used through IYO when order was created
wallet_addr* = (S)           # Wallet address


"""

bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)

Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema,__file__)
MODEL_CLASS = bcdb._BCDBModelClass


class threefoldtoken_order_sell(Index_CLASS,MODEL_CLASS):
    def __init__(self,bcdb,schema,reset=False):
        MODEL_CLASS.__init__(self, bcdb=bcdb,schema=schema,reset=reset)
        self.write_once = False
        self._init()
