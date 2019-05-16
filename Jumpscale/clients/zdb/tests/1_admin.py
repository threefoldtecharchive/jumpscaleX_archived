from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.clients.zdb.test(name="admin",start=True)'

    """

    c = self.client_admin_get(port=9901)
    c.reset()

    c.namespaces_list()
    assert c.namespaces_list() == ["default"]

    self._log_info("test ok")

    return "OK"
