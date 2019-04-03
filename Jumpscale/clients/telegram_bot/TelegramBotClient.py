from telegram.ext import Updater, CommandHandler
from Jumpscale import j


JSConfigClient = j.application.JSBaseConfigClass


class TelegramBot(JSConfigClient):
    """
    You can use this client to run your telegram bots and use Jumpscale config manager
    it exposes updater, bot and and dispatcher to be used by your bot
    """
    _SCHEMATEXT = """
    @url = jumpscale.telegramBot.client
    name* = "" (S)
    bot_token_ = "" (S)
    """

    def _init(self):

        self._conn = HTTPSConnection("api.telegram.org")

        self._updater = None
        self._bot = None
        self._dispatcher = None
        self._command_handler = None


    def config_check(self):
        '''check the configuration if not what you want the class will barf & show you where it went wrong

        :return: Error message regarding issue with the configuration
        :rtype: str
        '''

        if not self.bot_token_:
            return "bot_token_ is not properly configured, cannot be empty"

    def send_message(self, chatid, text, parse_mode=None):
        '''sends text to chat id

        :param chatid:  Unique identifier for the target chat or username of the target channel
        :type chatid: [type]
        :param text: Text of the message to be sent
        :type text: str
        :param parse_mode: See https://core.telegram.org/bots/api#sendmessage, defaults to None
        :type parse_mode: stra, optional
        :return: result of sendMessage api
        :rtype: [type]
        '''
        params = dict(chat_id=chatid, text=text)
        if parse_mode is not None:
            params["parse_mode"] = parse_mode
        url = "/bot{}/sendMessage?{}".format(self.bot_token_, urlencode(params))
        self._conn.request("GET", url)
        return self._conn.getresponse().read()


    @property
    def updater(self):
        if not self._updater:
            self._updater = Updater(token=self.bot_token, use_context=True)

        return self._updater

    @property
    def bot(self):
        if not self._bot:
            self._bot = self.updater.bot

        return self._bot

    @property
    def dispatcher(self):
        if not self._dispatcher:
            self._dispatcher = self.updater.dispatcher

        return self._dispatcher

    def command_register(self, name, command):
        self.dispatcher.add_handler(CommandHandler(name, command))

    def start_polling(self):
        self.updater.start_polling()

