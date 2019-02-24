from Jumpscale import j
from subprocess import run, PIPE
from datetime import datetime
from uuid import uuid4
import sys
import os 

def random_string():
    return str(uuid4()).replace('-', '')[:10]

def send_msg(msg):
    chat_id = os.environ.get('chat_id')
    client = j.clients.telegram_bot.get("test")
    msg = msg + '\n' + os.environ.get('name') + '\n' + os.environ.get('commit')
    client.send_message(chatid=chat_id, text=msg)

def execute_cmd(cmd):
    rc, stdout, stderr = j.builder.tools.run(cmd)
    return rc, stdout, stderr

def build_image():
    image_name = random_string()
    cmd = 'docker build --rm -t {} /sandbox/code/github/threefoldtech/jumpscaleX/scripts --build-arg commit={}'\
            .format(image_name, os.environ.get('commit'))
    rc, _, _ = execute_cmd(cmd)
    if rc:
        send_msg('Failed to install jumpscaleX')
        images_clean(image_name)
        sys.exit()
    else:
        return image_name

def run_tests(image_name):
    docker_cmd = "docker run --rm -t {} /bin/bash -c".format(image_name)
    env_cmd = "source /sandbox/env.sh; export NACL_SECRET={};".format(os.environ.get('Nacl'))
    run_cmd = "python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/test.py 1>/dev/null"
    cmd = '{} "{} {}"'.format(docker_cmd, env_cmd, run_cmd)
    _, stdout, _ = execute_cmd(cmd)
    if 'Error In' in stdout:
        file_name = '{}.log'.format(str(datetime.now())[:13].replace(' ', '_'))
        with open (file_name, 'w+') as f:
            f.write(stdout[stdout.find('Error In'):])

        file_link = '{}/{}'.format(os.environ.get('ServerIp'), file_name)
        send_msg('Tests had errors ' + file_link)
    else:
        send_msg('Tests Passed')

# def containers_remove():
#     response = execute_cmd('docker ps -a | tail -n+2 | awk "{print\$1}"')
#     containers = response.stdout.split()
#     for container in containers:
#         response = execute_cmd('docker rm -f {}'.format(container))
#         if response.returncode:
#             send_msg('Failed to remove docker container')

def images_clean(image_name):
    rc, _, _ = execute_cmd('docker rmi -f {}'.format(image_name))
    if rc:
        send_msg('Failed to remove docker image')

if __name__ == "__main__":
    image_name = build_image()
    run_tests(image_name)
    # containers_remove()
    images_clean(image_name)
