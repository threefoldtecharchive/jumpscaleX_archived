from Jumpscale import j

import digitalocean
import time

JSConfigBase = j.application.JSBaseConfigClass


class DigitalOceanVM(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.digitalocean.vm
    name* = "" (S)
    project_name = "" (S)
    do_id = "" (S)
    """
