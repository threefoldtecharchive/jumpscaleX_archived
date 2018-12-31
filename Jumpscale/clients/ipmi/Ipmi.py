import threading
import time

from Jumpscale import j

JSConfigBase = j.application.JSBaseConfigClass


class Ipmi(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.ipmi.client
    name* = "" (S)
    bmc = "" (S)
    user = "" (S)
    password_ = "" (S)
    port = 623 (ipport)
    """
    """ Ipmi client

    Before using the ipmi client, make sure to install ipmitool
    """

    def power_on(self):
        """ Power on ipmi host
        """
        j.tools.executorLocal.execute("ipmitool -H {host} -U {user} -P {password} -p {port} chassis power on".format(
            host=self.bmc,
            user=self.user,
            password=self.password_,
            port=self.port,
        ))

    def power_off(self):
        """ Power off ipmi host
        """
        j.tools.executorLocal.execute("ipmitool -H {host} -U {user} -P {password} -p {port} chassis power off".format(
            host=self.bmc,
            user=self.user,
            password=self.password_,
            port=self.port,
        ))

    def power_status(self):
        """ Returns power status of ipmi host

        Returns:
            str -- power status of node ('on' or 'off')
        """
        _, out, _ = j.tools.executorLocal.execute(
            "ipmitool -H {host} -U {user} -P {password} -p {port} chassis power status".format(
                host=self.bmc,
                user=self.user,
                password=self.password_,
                port=self.port,))

        if out.lower().strip() == "chassis power is on":
            return "on"
        elif out.lower().strip() == "chassis power is off":
            return "off"
        else:
            raise RuntimeError("ipmitool returned something unexpected: {}".format(out))

    def power_cycle(self):
        """ Power off host, wait a couple of seconds and turn back on again.
        The power will always be turned on at the end of this call.
        """
        # ipmitool doesn't support booting from off state. So if off, just boot up the node
        if self.power_status() == "off":
            self.power_on()
            return

        j.tools.executorLocal.execute("ipmitool -H {host} -U {user} -P {password} -p {port} chassis power cycle".format(
            host=self.bmc,
            user=self.user,
            password=self.password_,
            port=self.port,
        ))
