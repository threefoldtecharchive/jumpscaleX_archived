from autotest import RunTests
from build_image import BuildImage
from utils import Utils
import os
from datetime import datetime


utils = Utils()
test = RunTests()
image_name = '{}/jumpscalex'.format(utils.username)
repo = utils.repo[0]
file_name = '{}_builders.log'.format(str(datetime.now())[:10])
line = "python3.6 -m pytest -v /sandbox/code/github/threefoldtech/jumpscaleX/Jumpscale/builder/"
response = test.run_tests(image_name=image_name, run_cmd=line, repo=repo, commit='')
test.write_file(text='---> {}'.format(line), file_name=file_name)
test.write_file(text=response.stdout, file_name=file_name)
file_link = '{}/{}'.format(utils.serverip, file_name)
if response.returncode:
    utils.send_msg('Builders tests failed {}'.format(file_link))
else:
    utils.send_msg('Builders tests passed {}'.format(file_link))
