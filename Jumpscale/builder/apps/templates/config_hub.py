import os

#
# You should adapt this part to your usage
#
config = {
    "backend-internal-host": "{}".format(os.environ["IP_PORT"]),
    "backend-internal-port": 9900,
    "backend-internal-pass": "",
    "backend-public-host": "{}".format(os.environ["IP_PORT"]),
    "backend-public-port": 9900,
    "public-website": "http://{}".format(os.environ["IP_PORT"]),
    "ignored-files": [".", "..", ".keep"],
    "official-repositories": ["official-apps", "dockers"],
    # 'userdata-root-path': '/opt/0-hub/public',
    # 'workdir-root-path': '/opt/0-hub/workdir',
    # enable debug or production mode
    "debug": True,
}
