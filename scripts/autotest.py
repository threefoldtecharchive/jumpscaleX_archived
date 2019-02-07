from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4
# import re



# ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
client = j.clients.telegram_bot.get("test")

response = run('python3 /sandbox/code/github/threefoldtech/jumpscaleX/test.py', shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
# response.stderr = ansi_escape.sub('', response.stderr)

if response.stderr not in [None, '']:
    file_name = '{}.log'.format(str(uuid4()).replace('-', '')[:10])
    with open (file_name, 'w+') as f:
        f.write(response.stderr)
        
    # file_link = '{}/{}'.format('serverip', file_name)
    # client.send_message(chatid="@hamadatest", text=file_link)
else:
    client.send_message(chatid="@hamadatest", text='Tests Passed')
