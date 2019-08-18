from Jumpscale import j
from .SQLAlchemy import Base, SQLAlchemy

JSConfigs = j.application.JSBaseConfigsClass


class SQLAlchemyFactory(JSConfigs):
    __jslocation__ = "j.clients.sqlalchemy"
    _CHILDCLASS = SQLAlchemy

    def _init(self, **kwargs):
        self.__imports__ = "sqlalchemy"

    def getBaseClass(self):
        """
        complete example how to use sqlalchemy:
        https://github.com/Jumpscale/jumpscaleX/wiki/SQLAlchemy
        """
        return Base

    def validate_lower_strip(self, target, value, oldvalue, initiator):
        value = value.lower().strip()
        return value

    def validate_tel(self, target, value, oldvalue, initiator):
        value = value.lower().strip()
        value = value.replace(".", "")
        value = value.replace(",", "")
        value = value.replace("+", "")
        return value

    def validate_email(self, target, value, oldvalue, initiator):
        value = value.lower().strip()
        if value.find("@") == -1:
            raise j.exceptions.Input(
                "Property error, email not formatted well, needs @.Val:%s\nObj:\n%s" % (value, target)
            )
        return value
