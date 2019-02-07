from Jumpscale import j
from subprocess import run, PIPE
import re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
client = j.clients.telegram_bot.get("test")

response = run('python3 /sandbox/code/github/threefoldtech/jumpscaleX/test.py', shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
response.stderr = ansi_escape.sub('', response.stderr)

lines = response.stderr.splitlines() 
lines_send = []
lines_to_send = ''
for line in lines:
    if line.startswith('Traceback'):
        if lines_to_send != '':
            lines_send.append(lines_to_send)
        lines_to_send = line + '\n'
    else:
        lines_to_send = lines_to_send + line + '\n'
lines_send.append(lines_to_send)

for line in lines_send:
    line = "``` \n {} ``` \n".format(line)
    client.send_message(chatid="@hamadatest", text=line, parse_mode='markdown')
