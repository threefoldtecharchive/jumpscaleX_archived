from . import typchk


class PowerManager:
    _image_chk = typchk.Checker({"image": str})

    def __init__(self, client):
        self._client = client

    def reboot(self):
        """
        full reboot of the node
        """
        self._client.raw("core.reboot", {}, stream=True).stream()

    def poweroff(self):
        """
        full power off of the node
        """
        self._client.raw("core.poweroff", {}, stream=True).stream()

    def update(self, image):
        """
        update the node with given image, and fast reboot into this image
        No hardware reboot will ahppend

        :param image: efi image name, the image will be downloaded from https://bootstrap.grid.tf/kernel
                      example: "zero-os-development.efi"
        """

        args = {"image": image}

        self._image_chk.check(args)
        self._client.raw("core.update", args, stream=True).stream()
