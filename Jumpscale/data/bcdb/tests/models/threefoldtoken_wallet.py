from Jumpscale import j
#GENERATED CODE CAN CHANGE

SCHEMA="""
@url = threefoldtoken.wallet
@name = wallet
jwt = "" (S)                # JWT Token
addr** = ""                   # Address
addr_key* = ""                   # Address
ipaddr = (ipaddr)           # IP Address
email = "" (S)              # Email address
username = "" (S)           # User name


"""

bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)

Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema,__file__)
MODEL_CLASS = bcdb._BCDBModelClass


class threefoldtoken_wallet(Index_CLASS,MODEL_CLASS):
    def __init__(self,bcdb,schema,reset=False):
        MODEL_CLASS.__init__(self, bcdb=bcdb,schema=schema,reset=reset)
        self.write_once = False
        self._init()