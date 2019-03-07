import configparser
from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4
import sys
import os
import re
import requests
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


class Utils:
    def __init__(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read('config.ini')
        self.username = config['docker']['username']
        self.password = config['docker']['password']
        self.serverip = config['main']['server_ip']
        self.chat_id = config['main']['chat_id']
        self.access_token = config['github']['access_token']
        self.repo = config['github']['repo']
        self.exports = self.export_var(config)

    def execute_cmd(self, cmd):
        response = run(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
        return response

    def send_msg(self, msg, commit=None, commiter=None):
        client = j.clients.telegram_bot.get("test")
        if commit:
            msg = msg + '\n' + commiter + '\n' + commit
        client.send_message(chatid=self.chat_id, text=msg)

    def write_file(self, text, file_name):
        text = ansi_escape.sub('', text)
        file_path = '/mnt/data/result/' + file_name
        if os.path.exists(file_path):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not

        with open(file_path, append_write) as f:
            f.write(text + '\n\n')

    def github_status_send(self, status, file_link, commit):
        data = {"state": status, "description": "JSX-machine for testing",
                "target_url": file_link, "context": "continuous-integration/JSX"}
        url = 'https://api.github.com/repos/{}/statuses/{}?access_token={}'.format(self.repo, commit, self.access_token)
        requests.post(url, json=data)

    def random_string(self):
        return str(uuid4())[10:]

    def export_var(self, config):
        exports = config['exports']
        exp = ''
        for _ in exports:
            ex = exports.popitem()
            exp = exp + ex[0] + '=' + ex[1] + ' '
        return exp
