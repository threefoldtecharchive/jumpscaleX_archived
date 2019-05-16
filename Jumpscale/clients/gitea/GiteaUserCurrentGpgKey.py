from Jumpscale import j

from .GiteaGpgKey import GiteaGpgKey

JSBASE = j.application.JSBaseClass


class GiteaUserCurrentGpgKey(GiteaGpgKey):
    def save(self, commit=True):
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            self._log_debug(err)
            return is_valid

        try:
            d = self.data
            d["armored_public_key"] = d["public_key"]
            resp = self.user.client.api.user.userCurrentPostGPGKey(d)
            pubkey = resp.json()
            for k, v in pubkey.items():
                setattr(self, k, v)
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False

    def delete(self, commit=True):
        is_valid, err = self._validate(delete=True)

        if not commit or not is_valid:
            self._log_debug(err)
            return is_valid
        try:
            self.user.client.api.user.userCurrentDeleteGPGKey(id=str(self.id))
            self.id = None
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False
