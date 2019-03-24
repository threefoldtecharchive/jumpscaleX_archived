from .GiteaOrg import GiteaOrg


class GiteaOrgForMember(GiteaOrg):
    def save(self, commit=True):
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            self._log_debug(err)
            return is_valid
        try:
            resp = self.user.client.api.admin.adminCreateOrg(data=self.data, username=self.user.username)
            org = resp.json()
            for k, v in org.items():
                setattr(self, k, v)
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False

    def update(self, commit=True):
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            self._log_debug(err)
            return is_valid
        try:
            resp = self.user.client.api.orgs.orgEdit(data=self.data, org=self.username)
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False

    # def delete(self, commit=True):
    #     is_valid, err = self._validate(delete=True)
    #
    #     if not commit or not is_valid:
    #         self._log_debug(err)
    #         return is_valid
    #     try:
    #         resp = self.user.client.api.admin.adminDeleteUser(username=self.username)
    #         return True
    #     except Exception as e:
    #         self._log_debug(e.response.content)
    #         return False
