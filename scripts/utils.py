from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4
import configparser
import base64
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
        self.github_cl = j.clients.github('test', token=self.access_token)
        self.repo = self.github_cl.api.get_repo(self.repo)

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
            msg = '\n'.join([msg, committer, commit])
        client.send_message(chatid=self.chat_id, text=msg)

    def write_file(self, text, file_name, file_path=''):
        """Write result file.

        :param text: text will be written to result file.
        :type text: str
        :param file_name: result file name.
        :type file_name: str
        """
        text = ansi_escape.sub('', text)
        if file_path == '':
            file_path = self.result_path
        file_path = os.path.join(file_path, file_name)
        if os.path.exists(file_path):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not

        with open(file_path, append_write) as f:
            f.write(text + '\n')

    def github_status_send(self, status, file_link, commit):
        """Change github commit status.
        
        :param status: should be one of [error, failure, pending, success].
        :type status: str
        :param file_link: the result file link to be accessed through the server.
        :type file_link: str
        :param commit: commit hash required to change its status on github.
        :type commit: str
        """
        commit = self.repo.get_commit(commit)
        commit.create_status(state=status, target_url=file_link, description='JSX-machine for testing',
                             context='continuous-integration/0-Test')

    def github_get_content(self, ref, file_path='0-Test.sh'):
        """Get file content from github with specific commit.

        :param commit: commit hash.
        :type commit: str
        """
        try:
            content_b64 = self.repo.get_contents(file_path, ref=ref)
        except Exception:
            return None
        content = base64.b64decode(content_b64.content)
        content = content.decode()
        return content
    
    def report(self, status, file_name, branch, commit, committer=''):
        """Report the result to github commit status and Telegram chat.

        :param status: test status. 
        :type status: str
        :param file_link: result file link. 
        :type file_link: str
        :param branch: branch name. 
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github. 
        :type committer: str
        """
        file_link = '{}/{}'.format(self.serverip, file_name)
        text = '{}:{}'.format(file_name, status)
        self.write_file(text=text, file_name='status.log', file_path='.')
        self.github_status_send(status, file_link, commit=commit)
        if status == 'success' and branch == 'development':
            self.send_msg('Tests Passed ' + file_link, commit=commit, committer=committer)
        elif status == 'failure' and branch == 'development':
            self.send_msg('Tests had errors ' + file_link, commit=commit, committer=committer)
        
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
