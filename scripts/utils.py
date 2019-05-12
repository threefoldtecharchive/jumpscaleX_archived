from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4
import configparser
import time
import os
import re
import codecs
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
        self.repo = config['github']['repo'].split(',')
        self.result_path = config['main']['result_path']
        self.exports = self.export_var(config)
        self.github_cl = j.clients.github.get('test', token=self.access_token)
        self.telegram_cl = j.clients.telegram_bot.get("test")

    def execute_cmd(self, cmd):
        response = run(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE, encoding='utf-8')
        return response

    def random_string(self):
        return str(uuid4())[:10]

    def send_msg(self, msg, repo=None, branch=None, commit=None, committer=None):
        """Send Telegram message using Telegram bot.

        :param msg: message to be sent.
        :type msg: str
        :param repo: full repo name
        :type repo: str
        :param branch: branch name
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github.
        :type committer: str
        """
        if commit:
            repo = repo.strip('threefoldtech/')
            msg = '\n'.join([msg, repo, branch, committer, commit])
        for _ in range(0, 5):
            try:    
                self.telegram_cl.bot.sendMessage(chat_id=self.chat_id, text=msg)
                break
            except Exception:
                time.sleep(1)
                self.telegram_cl = j.clients.telegram_bot.get("test")

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

        with codecs.open(file_path, append_write, 'utf-8') as f:
            f.write(text + '\n')

    def github_status_send(self, status, link,  repo, commit):
        """Change github commit status.
        
        :param status: should be one of [error, failure, pending, success].
        :type status: str
        :param link: the result file link to be accessed through the server.
        :type link: str
        :param repo: full repo name
        :type repo: str
        :param commit: commit hash required to change its status on github.
        :type commit: str
        """
        for _ in range(0, 5):
            try: 
                repo = self.github_cl.api.get_repo(repo)
                commit = repo.get_commit(commit)
                commit.create_status(state=status, target_url=link, description='JSX-machine for testing',
                                    context='continuous-integration/0-Test')
                break
            except Exception:
                time.sleep(1)
                self.github_cl = j.clients.github.get('test', token=self.access_token)

    def github_get_content(self, repo, ref, file_path='0-Test.sh'):
        """Get file content from github with specific ref.

        :param repo: full repo name
        :type repo: str
        :param ref: name of the commit/branch/tag.
        :type ref: str
        :param file_path: file path in the repo
        :type file_path: str
        """
        for _ in range(0, 5):
            try:
                repo = self.github_cl.api.get_repo(repo)
                content_b64 = repo.get_contents(file_path, ref=ref)
                break
            except Exception:
                time.sleep(1)
                self.github_cl = j.clients.github.get('test', token=self.access_token)
        else:
            return None
        content = j.data.serializers.base64.decode(content_b64.content)
        content = content.decode()
        return content
    
    def report(self, status, file_name, repo, branch, commit, committer=''):
        """Report the result to github commit status and Telegram chat.

        :param status: test status. 
        :type status: str
        :param file_name: result file name. 
        :type file_name: str
        :param repo: full repo name
        :type repo: str
        :param branch: branch name. 
        :type branch: str
        :param commit: commit hash.
        :type commit: str
        :param committer: committer name on github. 
        :type committer: str
        """
        file_link = '{}/{}'.format(self.serverip, file_name)
        text = '{}:{}'.format(file_name, status)
        self.write_file(text=text, file_name='status.log')
        self.github_status_send(status=status, repo=repo, link=file_link, commit=commit)
        if status == 'success':
            self.send_msg('Tests passed ' + file_link, repo=repo, branch=branch, commit=commit, committer=committer)
        elif status == 'failure':
            self.send_msg('Tests failed ' + file_link, repo=repo, branch=branch, commit=commit, committer=committer)
        
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
