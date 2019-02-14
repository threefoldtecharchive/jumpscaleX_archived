from Jumpscale import j
from subprocess import run, PIPE
from datetime import datetime
import sys


chat_id = '@hamadatest'

def send_msg(msg):
    client = j.clients.telegram_bot.get("test")
    client.send_message(chatid=chat_id, text=msg)

def execute_cmd(cmd):
    response = run(cmd, shell=True, universal_newlines=True, stdout=PIPE, stderr=PIPE)
    return response

def build_image():
    response = execute_cmd('docker build --rm -t jumpscale /sandbox/code/github/threefoldtech/jumpscaleX')
    if response.returncode:
        send_msg('Failed to bulid docker image')
        containers_remove()
        images_clean()
        sys.exit()

def run_tests():
    docker_cmd = "docker run --rm -t jumpscale /bin/bash -c"
    env_cmd = "source /sandbox/env.sh; export NACL_SECRET=test;"
    run_cmd = "python3 /sandbox/code/github/threefoldtech/jumpscaleX/test.py"
    cmd = '{} "{} {}"'.format(docker_cmd, env_cmd, run_cmd)
    response = execute_cmd(cmd)
    if response.stderr not in [None, '']:
        file_name = '{}.log'.format(str(datetime.now())[:16])
        with open (file_name, 'w+') as f:
            f.write(response.stderr)

        file_link = '{}/{}'.format('serverip', file_name)
        send_msg('test has errors ' + file_link)
    else:
        send_msg('Tests Passed')

def containers_remove():
    response = execute_cmd('docker ps -a | tail -n+2 | awk "{print\$1}"')
    containers = response.stdout.split()
    for container in containers:
        response = execute_cmd('docker rm -f {}'.format(container))
        if response.returncode:
            send_msg('Failed to remove docker container')

def images_clean():
    response = execute_cmd('docker images | tail -n+2 | awk "{print \$1}"')
    images = response.stdout.split()
    response = execute_cmd('docker images | tail -n+2 | awk "{print \$3}"')
    images_id = response.stdout.split()
    for i in range(0, len(images)):
        if images[i] == 'ubuntu':
            continue
        else:
            response = execute_cmd('docker rmi -f {}'.format(images_id[i]))
            if response.returncode:
                send_msg('Failed to remove docker image')

if __name__ == "__main__":
    build_image()
    run_tests()
    containers_remove()
    images_clean()


