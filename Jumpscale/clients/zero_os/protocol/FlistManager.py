from Jumpscale import j


class FlistManager:
    def __init__(self, client, container_id):
        self._client = client
        self._id = container_id

    def create(self, src, dst, storage="hub.grid.tf:9980", token="", hub=""):
        """
        Create an flist from src

        if token is specified, try to push the generated flist to a hub.
        by default push to hub.grid.tf, but you can change the destination hub using the `hub` argument.

        hub value for threefold hubs:
            default: https://hub.grid.tf/api/flist/me/upload-flist
            playground: https://playground.hub.grid.tf/api/flist/me/upload-flist
        storage value for threefold hubs:
            default: hub.grid.tf:9980
            playgroud: hub.grid.tf:9910


        :param src: Absolute path of the directory with the files that will be uploaded to storage
        :param dst: Flist name (Ex: /tmp/myflist.flist)
        :param storage: Address of zdb were files will be uploaded
        :param token: An optional iyo jwt token to upload data into the backend and flist on the hub
        :param hub: URL of the API endpoint to use to push the generated flist on a hub. If not specified, will push to
                    https://hub.grid.tf/api/flist/me/upload-flist
        """
        args = {"container": self._id, "flist": dst, "src": src, "storage": storage, "token": token, "hub": hub}
        flist_loction = self._client.json("corex.flist.create", args)
        return flist_loction.split("/mnt/containers/%d/" % self._id)[1]
