from Jumpscale import j
from .TelegramBotClient import TelegramBot

JSConfigFactory = j.application.JSFactoryBaseClass


class TelegramBotFactory(JSConfigFactory):
    __jslocation__ = "j.clients.telegram_bot"
    _CHILDCLASS = TelegramBot
