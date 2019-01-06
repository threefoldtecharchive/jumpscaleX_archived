from http.client import HTTPSConnection
from urllib.parse import urlencode
from Jumpscale import j


JSConfigClient = j.application.JSBaseConfigClass


class TelegramBot(JSConfigClient):
    _SCHEMATEXT = """
    @url = jumpscale.telegramBot.client
    name* = "" (S)
    bot_token_ = "" (S)
    """

    def _init(self):
        self._conn = HTTPSConnection("api.telegram.org")

    def config_check(self):
        """
        check the configuration if not what you want the class will barf & show you where it went wrong
        """
        if not self.bot_token_:
            return "bot_token_ is not properly configured, cannot be empty"

    def send_message(self, chatid, text, parse_mode=None):
        """
        send_message sends text to chat id
        :param chatid: Unique identifier for the target chat or username of the target channel
        :param text: Text of the message to be sent
        :param parse_mode: See https://core.telegram.org/bots/api#sendmessage
        :return: result of sendMessage api
        """
        params = dict(chat_id=chatid, text=text)
        if parse_mode is not None:
            params["parse_mode"] = parse_mode
        url = "/bot{}/sendMessage?{}".format(self.bot_token_, urlencode(params))
        self._conn.request("GET", url)
        return self._conn.getresponse().read()
