import requests
import json
from . import errors

from Jumpscale import j

JSConfigBase = j.application.JSBaseConfigClass



def to_bool_or_false(x):
    try:
        return bool(x)
    except:
        return False

def to_int_or_0(x):
    try:
        return int(x)
    except:
        return 0


validators = {
    'num': lambda x:  int(x) and x.isdigit(),
    'valid_userid': lambda x: x.isdigit() and int(x)>0,
    "bool": lambda x: bool(int(x)),
    "int": lambda x: 0 if not x else int(x)
}

validation_rules = {
    "VersionInfo.Rel": validators['num'],
    "sessionid":  validators['num'],
    "VersionInfo.Rel": validators['num'],
    "VersionInfo.Ver": validators['num'],
    "VersionInfo.Patch": validators['num'],
    "VersionInfo.ForceUpdate": validators['num'],
    "VersionInfo.UpdateType": validators['num'],
    "IsReadOnly": validators["bool"],
    "DemoClient": validators["bool"],
    "EnableNews": validators["bool"],

}

conversion_rules = {
    "VersionInfo.Rel": to_int_or_0,
    "VersionInfo.Ver": to_int_or_0,
    "VersionInfo.Patch": to_int_or_0,
    "VersionInfo.ForceUpdate": to_int_or_0,
    "VersionInfo.UpdateType": to_int_or_0,
    "DepId": to_int_or_0,
    "CommCalcType": to_int_or_0,
    "ClientType": to_int_or_0,
    "DemoClient": to_int_or_0,
    "IsReadOnly": to_int_or_0,
    "Sms": to_int_or_0,
    "EnableNews":to_int_or_0,
}


def get_error_string(errval):
    for m in dir(errors):
        res = getattr(errors, m)
        # print(m,  res, errval)
        if res == errval:
            return m
    return ""

def raise_if_error(data):
    if isinstance(data, int):
        errorstring = get_error_string(data)
        if errorstring:
            raise ValueError("raised error with value: {} original is {}".format(data, errorstring))
        else:
            raise ValueError("raised error with value: {} and couldn't find it in errors.".format(data))

    if not (isinstance(data, dict) or isinstance(data, list)):
        raise ValueError("data {} should be dict not {}".format(data, type(data)))

    return data


def clean_data(data):
    if isinstance(data, dict):
        cleaned_data_dict = {}
        for k, v in data.items():
            if k in conversion_rules:
                f = conversion_rules[k]
                cleaned_data_dict[k] = f(v)
            else:
                cleaned_data_dict[k] = v
        return cleaned_data_dict
    elif isinstance(data, list):
        cleaned_data_list = []
        for el in data:
            cleaned_data_list.append(clean_data(el))
        return cleaned_data_list
    else:
        return data

def raise_if_invalid_user_id(user_id):
    raise_if_error(user_id)

def is_valid_user_id(user_id):
    try:
        raise_if_error(user_id)
        return True
    except:
        return False


class NBHClient(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.nbh.client
    name* = "main"
    username = "" (S)
    password_ = "" (S)
    service_url = "" (S)
    nbh_sig_ = (S)
    nbh_wallet_ = (S)
    """


    def _init(self, **kwargs):
        if not self.username or not self.password_:
            raise j.exceptions.Input("Need to specify both username and passwd to use the client")

        if not self.service_url:
            raise j.exceptions.Input("Need to url to use the client")

        self._session = requests.session()
        self.login()

    def _request(self, endpoint, params):
        url = "{}/{}".format(self.service_url, endpoint)
        resp = self._session.get(url, params=params)

        resp.raise_for_status()

        resp_json = resp.json()
        data = json.loads(resp_json['d'])

        return clean_data(data)

    def login(self):
        params = {"username":self.username, "password":self.password_}
        return self._request("BackofficeLogin", params)


    def new_position(self, account_id, buy_or_sell, amount, symbol_id, price, note="", user_defined_date=""):
        """The NewPosition operation is used to open a new position on specific a symbol for the given account number.

        :param account_id: valid account identifier to open position for
        :type account_id: int
        :param buy_or_sell: the open position type, 1 for buy and -1 for sell
        :type buy_or_sell: int
        :param amount: position lots value
        :type amount: int
        :param symbol_id: trade symbol identifier
        :type symbol_id: int
        :param price: open trade price value
        :type price: int
        :param note: string used to mark the open position, defaults to ""
        :type note: str, optional
        :param user_defined_date: trade open time, defaults to "" which means now
        :type user_defined_date: str in format DD/MM/yyyy HH:mm:ss, optional
        :return: the new position ticket number
        :rtype: [type]
        """
        params = {"AccountID": account_id, "BuySell": buy_or_sell, "Amount":amount, "SymbolID": symbol_id, "Price":price, "note":note, "UserDefinedData":user_defined_date}
        return self._request("NewPosition", params)


    def close_position(self, account_id, ticket_id, amount, price, ref_price, commission, user_defined_date=""):
        """The ClosePosition operation is used to close the position that belongs to the given account number

        :param account_id: valid account identifier to open position for
        :type account_id: int
        :param ticket_id: the position number to be closed
        :type ticket_id: int
        :param amount: position amount to be closed
        :type amount: int
        :param price: at price value to close position on it
        :type price: int
        :param ref_price: reference symbol price value
        :type ref_price: int
        :param commission: the commision value to be used when closing the position
        :type commission: int
        :param user_defined_date: trade open time, defaults to "" which means now
        :type user_defined_date: str in format DD/MM/yyyy HH:mm:ss, optional
        :return: closed ticket number
        :rtype: int
        """
        params = {"AccountID": account_id, "TicketID": ticket_id, "Amount":amount, "Price":price, "RefPrice": ref_price, "Comm": commission, "UserDefinedData":user_defined_date}
        return self._request("ClosePosition", params)


    def detailed_openpositions_report(self, client_id, account_type, symbol_id=0, position_type=0, is_paging=False):
        """The DetailedOpenPositionsReport operation is used to get detailed open positions report that shows the open position details for all accounts
under the given client number.

        :param client_id: valid client identifier to get report for
        :type client_id: int
        :param account_type: type of account to get account status report for. 1 for Normal Account, 2 for Coverage Account.
        :type account_type: int
        :param symbol_id: The report will show the open position detailed  for this symbol ID. Defaults to 0 means for all Symbol.
        :type symbol_id: int
        :param position_type: The report will shows the net open position details for this type. 0 for all, 1 for buy type, -1 for sell type. Defaults to 0.
        :type position_type: int
        :param is_paging: indicates that you're calling to get the remaining records. First call must be false, next must be true.
        :type is_paging: bool, optional
        :return: list of open positions
        :rtype: list
        """
        params = {"ClientID": client_id, "AccountType": account_type, "SymbolID": symbol_id, "PositionType": position_type, "isPaging": is_paging}
        return self._request("DetailedOpenPositionsReport", params)


    def get_accounts_ids(self, client_id):
        """The GetAccountsIDs operation is used to get the list of account/s Id/s  which are related to a given client number.

        :param client_id: valid client identifier
        :type client_id: int
        :return: list of account ids
        :rtype: list
        """
        params = {"ClientID": client_id}
        return self._request("GetAccountsIDs", params)
