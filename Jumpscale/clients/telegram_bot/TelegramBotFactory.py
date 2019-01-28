from Jumpscale import j
from .TelegramBotClient import TelegramBot

JSConfigs = j.application.JSBaseConfigsClass


class TelegramBotFactory(JSConfigs):
    __jslocation__ = "j.clients.telegram_bot"
    _CHILDCLASS = TelegramBot
