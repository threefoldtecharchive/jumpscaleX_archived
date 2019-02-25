from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4
import sys
import os
import re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


class Utils:

    def execute_cmd(self, cmd):
        response = run(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
        return response

    def send_msg(self, msg, push=True):
        chat_id = os.environ.get('chat_id')
        client = j.clients.telegram_bot.get("test")
        if push:
            msg = msg + '\n' + os.environ.get('name') + '\n' + os.environ.get('commit')
        client.send_message(chatid=chat_id, text=msg)

    def write_file(self, text, file_name):
        text = ansi_escape.sub('', text)
        with open(file_name, 'w+') as f:
            f.write(text)
        file_link = '{}/{}'.format(os.environ.get('ServerIp'), file_name)
        return file_link
