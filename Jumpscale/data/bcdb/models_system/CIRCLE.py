

# Copyright (C) 2019 :  TF TECH NV in Belgium see https://www.threefold.tech/
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.


from Jumpscale import j


class CIRCLE(j.data.bcdb._BCDBModelClass):
    def _schema_get(self):
        return j.data.schema.get_from_url_latest("jumpscale.bcdb.circle.2")

    def userids_get(self):
        """
        will recursive get all users ids which are in circle & return as list of id's of users
        :param id:
        :return:
        """
        if not id in self._circles:
            users = []
            gr = self.model_circle.get(id)
            if gr:
                for userid in gr.users:
                    if userid not in users:
                        users.append(userid)
                for gid in gr.circles:
                    gr2 = self.model_circle.get(id)
                    if gr2:
                        for userid2 in gr2.users:
                            if userid2 not in users:
                                users.append(userid2)
            self._circles[id] = users
        return self._circles[id]
