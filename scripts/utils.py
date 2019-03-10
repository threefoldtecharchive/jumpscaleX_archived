from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4
import configparser
import requests
import base64
import sys
import os
import re
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
        self.result_path = config['main']['result_path']
        self.exports = self.export_var(config)

    def execute_cmd(self, cmd):
        response = run(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
        return response

    def random_string(self):
        return str(uuid4())[:10]

    def send_msg(self, msg, commit=None, committer=None):
        """Send Telegram message using Telegram bot.

        :param msg: message to be sent.
        :type msg: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github.
        :type committer: str
        """
        client = j.clients.telegram_bot.get("test")
        if commit:
            msg = msg + '\n' + committer + '\n' + commit
        client.send_message(chatid=self.chat_id, text=msg)

    def write_file(self, text, file_name):
        """Write result file.

        :param text: text will be written to result file.
        :type text: str
        :param file_name: result file name.
        :type file_name: str
        """
        text = ansi_escape.sub('', text)
        file_path = os.path.join(self.result_path, file_name)
        if os.path.exists(file_path):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not

        with open(file_path, append_write) as f:
            f.write(text + '\n\n')

    def github_status_send(self, status, file_link, commit):
        """Change github commit status.
        
        :param status: should be one of [error, failure, pending, success].
        :type status: str
        :param file_link: the result file link to be accessed through the server.
        :type file_link: str
        :param commit: commit hash required to change its status on github.
        :type commit: str
        """
        data = {"state": status, "description": "JSX-machine for testing",
                "target_url": file_link, "context": "continuous-integration/0-Test"}
        url = 'https://api.github.com/repos/{}/statuses/{}?access_token={}'.format(self.repo, commit, self.access_token)
        requests.post(url, json=data)

    def github_get_content(self, commit):
        """Get file content from github with specific commit.

        :param commit: commit hash.
        :type commit: str
        """
        url = 'https://api.github.com/repos/{}/contents/0-Test.sh'.format(self.repo)
        req = requests.get(url, {'ref': commit})
        if req.status_code == requests.codes.ok:
            req = req.json()
            content = base64.b64decode(req['content'])
            content = content.decode()
            return content
        return None

    def export_var(self, config):
        """Prepare environment variables from config file.

        :param config: secret stored in config.ini file.
        """
        exports = config['exports']
        exps = ''
        for _ in exports:
            exp = exports.popitem()
            exps = exps + exp[0] + '=' + exp[1] + ' '
        return exps
