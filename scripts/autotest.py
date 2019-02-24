from Jumpscale import j
from subprocess import run, PIPE
from uuid import uuid4
import sys, os , re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


def random_string():
    return str(uuid4()).replace('-', '')[:10]

def send_msg(msg):
    chat_id = os.environ.get('chat_id')
    client = j.clients.telegram_bot.get("test")
    msg = msg + '\n' + os.environ.get('name') + '\n' + os.environ.get('commit')
    client.send_message(chatid=chat_id, text=msg)

def execute_cmd(cmd):
    response = run(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
    return response

def write_file(text):
    text = ansi_escape.sub('', text)
    file_name = '{}.log'.format(os.environ.get('commit')[:7])
    with open (file_name, 'w+') as f:
        f.write(text)
    file_link = '{}/{}'.format(os.environ.get('ServerIp'), file_name)
    return file_link

def build_image():
    image_name = random_string()
    cmd = 'docker build --force-rm -t {} /sandbox/code/github/threefoldtech/jumpscaleX/scripts --build-arg commit={}'\
            .format(image_name, os.environ.get('commit'))
    response = execute_cmd(cmd)
    if response.returncode:
        file_link = write_file(response.stdout)
        send_msg('Failed to install jumpscaleX ' + file_link)
        images_clean()
        sys.exit()
    else:
        return image_name

def run_tests(image_name):
    docker_cmd = "docker run --rm -t {} /bin/bash -c".format(image_name)
    env_cmd = "source /sandbox/env.sh; export NACL_SECRET={};".format(os.environ.get('Nacl'))
    run_cmd = "python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/test.py 1>/dev/null"
    cmd = '{} "{} {}"'.format(docker_cmd, env_cmd, run_cmd)
    response = execute_cmd(cmd)
    if 'Error In' in response.stdout:
        file_link = write_file(response.stdout[response.stdout.find('Error In'):])
        send_msg('Tests had errors ' + file_link)
    else:
        send_msg('Tests Passed')

def images_clean(image_name=None):
    if image_name:
        response = execute_cmd('docker rmi -f {}'.format(image_name))
        
    # for case of failure to build docker images
    response = execute_cmd('docker images | tail -n+2 | awk "{print \$5}"')
    images_time = response.stdout.split()
    response = execute_cmd('docker images | tail -n+2 | awk "{print \$3}"')
    images_id = response.stdout.split()
    if len(images_id) == len(images_time):
        for i in range(0, len(images_id)):
            if images_time[i] not in ['second', 'seconds', 'minutes', 'minute']:
                response = execute_cmd('docker rmi -f {}'.format(images_id[i]))
                
if __name__ == "__main__":
    image_name = build_image()
    run_tests(image_name)
    images_clean(image_name)
