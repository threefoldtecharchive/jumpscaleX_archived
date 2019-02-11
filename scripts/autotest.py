from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4


client = j.clients.telegram_bot.get("test")
response = run('docker build --rm -t jumpscale ../', shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
if response.returncode:
    client.send_message(chatid="@hamadatest", text='Failed to bulid docker image')

response = run('docker run --rm -t jumpscale /bin/bash -c "source /sandbox/env.sh; python3 /sandbox/code/github/threefoldtech/jumpscaleX/test.py"', shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
if response.stderr not in [None, '']:
    file_name = '{}.log'.format(str(uuid4()).replace('-', '')[:10])
    with open (file_name, 'w+') as f:
        f.write(response.stderr)

    file_link = '{}/{}'.format('serverip', file_name)
    client.send_message(chatid="@hamadatest", text='test has errors ' + file_link)
else:
    client.send_message(chatid="@hamadatest", text='Tests Passed')

response = run('docker rmi jumpscale', shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
if response.returncode:
    client.send_message(chatid="@hamadatest", text='Failed to remove the built docker image')
