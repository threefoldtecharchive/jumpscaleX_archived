from flask import Flask, request, send_file, render_template, abort
from autotest import RunTests
from build_image import BuildImage
from utils import Utils
import os
utils = Utils()
app = Flask(__name__)


def test_run(image_name, repo, branch, commit, committer):
    """Run test aginst the new commit and give report on Telegram chat and github commit status.
    
    :param image_name: docker image name.
    :type image_name: str
    :param repo: full repo name
    :type repo: str
    :param branch: branch name.
    :type branch: str
    :param commit: commit hash.
    :type commit: str
    :param committer: name of the committer on github.
    :type committer: str
    """
    test = RunTests()
    file_name = '{}.log'.format(commit[:7])
    status = 'success'
    content = test.github_get_content(repo=repo, ref=commit)
    if content:
        lines = content.splitlines()
        for line in lines:
            if line.startswith('#'):
                continue
            response = test.run_tests(image_name=image_name, run_cmd=line, repo=repo, commit=commit)
            test.write_file(text='---> {}'.format(line), file_name=file_name)
            test.write_file(text=response.stdout, file_name=file_name)
            if response.returncode:
                status = 'failure'
    else:
        test.write_file(text="Didn't find tests", file_name=file_name)

    utils.report(status=status, file_name=file_name, repo=repo, branch=branch, commit=commit, committer=committer)


def build_image(branch, commit, committer):
    """Build a docker image to install application.

    :param branch: branch name.
    :type branch: str
    :param commit: commit hash.
    :type commit: str
    :param committer: name of the committer on github.
    :type committer: str
    """
    build = BuildImage()
    image_name = build.random_string()
    response = build.image_bulid(image_name=image_name, branch=branch, commit=commit)
    if response.returncode:
        file_name = '{}.log'.format(commit[:7])
        build.write_file(text=response.stdout, file_name=file_name)
        build.images_clean()
        utils.report(status='failure', file_name=file_name, repo=utils.repo[0], branch=branch, commit=commit, committer=committer)
        return False
    return image_name

def get_state(name):
    with open('status.log', 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.split(':')
        if line[0] == name:
            return line[1].strip()

@app.route('/jumpscalex', methods=["POST"])
def triggar_jumpscale(**kwargs):
    """Triggar the test when post request is sent from jumpscalex repo.
    """
    if request.json:
        # push case 
        if request.json.get('ref'):
            repo = request.json['repository']['full_name']
            branch = request.json['ref'][request.json['ref'].rfind('/') + 1:]
            commit = request.json['after']
            committer = request.json['pusher']['name']
            if repo == utils.repo[0] and branch == 'development':
                utils.github_status_send(status='pending', link=utils.serverip, repo=repo, commit=commit)
                image_name = '{}/jumpscalex'.format(utils.username)
                test_run(image_name=image_name, repo=repo, branch=branch, commit=commit, committer=committer)
        
        # pull request case
        elif request.json.get('pull_request'):
            repo = request.json['pull_request']['head']['repo']['full_name']
            branch = request.json['pull_request']['head']['ref']
            commit = request.json['pull_request']['head']['sha']
            committer = request.json['sender']['login']
            if repo == utils.repo[0]:
                utils.github_status_send(status='pending', link=utils.serverip, repo=repo, commit=commit)
                image_name = build_image(branch=branch, commit=commit, committer=committer)
                if image_name:
                    test_run(image_name=image_name, repo=repo, branch=branch, commit=commit, committer=committer)
                    build = BuildImage()
                    build.images_clean(image_name=image_name)
    return "Done", 201

@app.route('/digitalmex', methods=["POST"])
def triggar_digitalme(**kwargs):
    """Triggar the test when post request is sent from digitalme repo
    """
    if request.json:
        # push case 
        if request.json.get('ref'):
            repo = request.json['repository']['full_name']
            branch = request.json['ref'][request.json['ref'].rfind('/') + 1:]
            commit = request.json['after']
            committer = request.json['pusher']['name']
            if repo == utils.repo[1]:
                utils.github_status_send(status='pending', link=utils.serverip, repo=repo, commit=commit)
                image_name = '{}/jumpscalex'.format(utils.username)
                test_run(image_name=image_name, repo=repo, branch=branch, commit=commit, committer=committer)
    return "Done", 201


@app.route("/<filename>")
def files(filename):
    abs_path = os.path.join(utils.result_path, filename)
    if not os.path.exists(abs_path):
        return abort(404)

    if os.path.isfile(abs_path):
        return send_file(abs_path, mimetype='text/x-log')


@app.route('/')
def dir_listing():
    path = utils.result_path
    names = os.listdir(path)
    names.sort(key=lambda x: os.path.getctime(os.path.join(path, x)), reverse=True)
    files = list()
    [files.append({'name': name, 'state': get_state(name)}) for name in names]
    return render_template('files.html', files=files)


if __name__ == "__main__":
    port = utils.serverip[utils.serverip.rfind(':') + 1:]
    app.run("0.0.0.0", port)
