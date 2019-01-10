from intercom.client import Client
from Jumpscale import j
from intercom.errors import HttpError
import intercom
intercom.HttpError = HttpError
intercom.__version__ = '3.1.0'


JSConfigClient = j.application.JSBaseConfigClass


class IntercomClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.intercom.client
        name* = "" (S)
        token_ = "dG9rOmNjNTRlZDFiX2E3OTZfNGFiM185Mjk5X2YzMGQyN2NjODM4ZToxOjA=" (S)
        """

    def _init(self):
        self.token = self.token_
        self.api = Client(personal_access_token=self.token)

    def send_in_app_message(self, body, admin_id, user_id):
        """
        sending an in-app message from an admin to user

        :param body: (String) body of the email
        :param admin_id: (String) id of sender admin
        :param user_id: (String) id of user who will receive the message
        """
        self.api.messages.create(**{
            "message_type": "inapp",
            "body": body,
            "from": {
                "type": "admin",
                "id": admin_id
            },
            "to": {
                "type": "user",
                "id": user_id
            }
        })

    def send_mail_message(self, subject, body, template, admin_id, user_id):
        """
        sending a mail message from an admin to user

        :param subject:(String)  subject of the email
        :param body: (String) body of the email
        :param template: (String) has one of the 2 values "plain", or "personal"
        :param admin_id: (String) id of sender admin
        :param user_id: (String) id of user who will receive the message
        """
        self.api.messages.create(**{
            "message_type": "email",
            "subject": subject,
            "body": body,
            "template": template,
            "from": {
                "type": "admin",
                "id": admin_id
            },
            "to": {
                "type": "user",
                "id": user_id
            }
        })

    def get_user(self, email):
        user = self.api.users.find(email=email)
        return user

    def get_all_users(self):
        users = self.api.users.all()
        return users

    def delete_user(self, email):
        user = self.get_user(email=email)
        self.api.users.delete(user)

    def get_all_admins(self):
        admins = self.api.admins.all()
        return admins

    def get_admin(self, name):
        admins = self.api.admins.all()
        for admin in admins:
            if admin.name == name:
                return admin
        return None
