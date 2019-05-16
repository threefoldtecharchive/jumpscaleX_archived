from Jumpscale import j

from .GiteaPublicKey import GiteaPublicKey


class GiteaUserCurrentPublicKey(GiteaPublicKey):
    def save(self, commit=True):

        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            self._log_debug(err)
            return is_valid

        try:
            resp = self.client.api.user.userCurrentPostKey(self.data)
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
            self.client.api.user.userCurrentDeleteKey(id=str(self.id))
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False
