from flask import Flask, request
from subprocess import run
from autotest import RunTests
from build_image import BuildImage
from utils import Utils
import os
app = Flask(__name__)


def test_run(image_name, commit, commiter):
    test = RunTests()
    file_name = '{}.log'.format(commit[:7])
    status = True
    if os.path.exists('script.sh'):
        with open('script.sh', 'r') as f:
            lines = f.readlines()
        for line in lines:
            response = test.run_tests(image_name=image_name, run_cmd=line, commit=commit)
            test.write_file(text='---> {}'.format(line), file_name=file_name)
            test.write_file(text=response.stdout, file_name=file_name)
            if response.returncode:
                status = False
    file_link = '{}/{}'.format(test.serverip, file_name)
    test.report(status, file_link, commit=commit, commiter=commiter)


def build_image(branch, commit):
    build = BuildImage()
    build.github_status_send('pending', build.serverip)
    image_name = build.random_string()
    response = build.image_bulid(image_name=image_name, branch=branch, commit=commit)
    if response.returncode:
        file_name = '{}.log'.format(commit[:7])
        build.write_file(text=response.stdout, file_name=file_name)
        build.images_clean()
        file_link = '{}/{}'.format(build.serverip, file_name)
        build.github_status_send('failure', file_link, commit)
        return False, image_name
    return True, image_name


@app.route('/', methods=["POST"])
def triggar(**kwargs):
    if request.json:
        if request.json.get('ref'):
            branch = request.json['ref'][request.json['ref'].rfind('/') + 1:]
            commit = request.json['after']
            commiter = request.json['pusher']['name']

            if branch == 'development':
                utils = Utils()
                utils.github_status_send('pending', utils.serverip, commit=commit)
                image_name = '{}/jumpscalex'.format(utils.username)
                test_run(image_name=image_name, commit=commit, commiter=commiter)

        elif request.json.get('pull_request'):
            branch = request.json['pull_request']['head']['ref']
            commit = request.json['pull_request']['head']['sha']
            commiter = request.json['pull_request']['head']['user']['login']
            state, image_name = build_image(branch, commit)
            if state:
                test_run(image_name=image_name, commit=commit, commiter=commiter)

    return "Done", 201


@app.route('/', methods=["GET"])
def ping():
    return 'pong'


if __name__ == "__main__":
    app.run("0.0.0.0", 6010)
