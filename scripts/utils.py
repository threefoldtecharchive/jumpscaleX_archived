from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4
import sys
import os
import re
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


class Utils:
    def __init__(self):
        self.username = os.environ.get('username')
        self.password = os.environ.get('password')
        self.serverip = os.environ.get('ServerIp')
        self.chat_id = os.environ.get('chat_id')
        self.commit = os.environ.get('commit')
        self.commiter = os.environ.get('commiter')
        self.nacl = os.environ.get('Nacl')
        self.access_token = os.environ.get('access_token')

    def execute_cmd(self, cmd):
        response = run(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
        return response

    def send_msg(self, msg, push=False):
        client = j.clients.telegram_bot.get("test")
        if push:
            msg = msg + '\n' + self.commiter + '\n' + self.commit
        client.send_message(chatid=self.chat_id, text=msg)

    def write_file(self, text, file_name):
        text = ansi_escape.sub('', text)
        with open(file_name, 'w+') as f:
            f.write(text)
        file_link = '{}/{}'.format(self.serverip, file_name)
        return file_link
