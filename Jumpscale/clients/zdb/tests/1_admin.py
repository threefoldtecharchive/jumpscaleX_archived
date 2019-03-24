from Jumpscale import j

def main(self):
    """
    to run:

    js_shell 'j.clients.zdb.test(name="admin",start=True)'

    """

    c = self.client_admin_get()
    c.reset()

    c.namespaces_list()
    assert c.namespaces_list() == ['default']

    self._log_info("test ok")

    return "OK"
