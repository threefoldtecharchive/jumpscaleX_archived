import os
from Jumpscale import j
import base64
from collections import namedtuple
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail, Personalization, Attachment as SendGridAttachment

Attachment = namedtuple("Attachment", ["originalfilename", "binarycontent", "type"])
JSBASE = j.application.JSBaseClass


class SendGridClient(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.clients.sendgrid"
        JSBASE.__init__(self)

    def send(
        self, sender, subject, message, recipients=None, message_type="text/plain", api_key=None, attachments=None
    ):
        """
        @param sender:string (the sender of the email)
        @param recipient:list (list of recipients of the email)
        @param subject:string (subject of the email)
        @param message:string (content of the email)
        @param message_type:string (mime type of the email content)
        @param api_key:string (the api key of sendgrid)
        @param attachments:list (list of Attachment tuple)
        """
        api_key = api_key or os.environ.get("SENDGRID_API_KEY", None)

        if recipients is None or recipients == []:
            return
        if attachments is None:
            attachments = []

        if api_key is None:
            raise j.exceptions.Base("Make sure to export SENDGRID_API_KEY or pass your api key")
        sg = sendgrid.SendGridAPIClient(apikey=api_key)
        from_email = Email(sender)
        to_email = Email(recipients[0])
        content = Content(message_type, message)
        mail = Mail(from_email, subject, to_email, content)

        to = list(set(recipients))  # no duplicates.
        if len(to) > 1:
            for receiver in to[1:]:
                mail.personalizations[0].add_to(Email(receiver))

        for attachment in attachments:
            mail.add_attachment(self.build_attachment(attachment))

        try:
            response = sg.client.mail.send.post(request_body=mail.get())
        except Exception as e:
            self._log_info(e)
            raise e

        self._log_info("Email sent..")
        return response.status_code, response.body

    def test(self):

        SENDER = "test@threefold.tech"
        RECIPENT = "test@threefold.tech"
        SUBJECT = "Sending with SendGrid is Fun"
        MESSAGE_TYPE = "text/plain"
        MESSAGE = "and easy to do anywhere, even with Python"

        attachment = Attachment(
            originalfilename="balance_001.pdf",
            binarycontent=b"TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNlY3RldHVyIGFkaXBpc2NpbmcgZWxpdC4gQ3JhcyBwdW12",
            type="application/pdf",
        )

        statCode, body = self.send(SENDER, SUBJECT, MESSAGE, [RECIPENT], MESSAGE_TYPE, attachments=[attachment])

        self._log_info(statCode)

    def build_attachment(self, attachment):
        """
        Returns a valid sendgrid attachment from typical attachment object.
        e.g
        ```
        attachment = Attachment()
        attachment.content = ("TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNl"
                              "Y3RldHVyIGFkaXBpc2NpbmcgZWxpdC4gQ3JhcyBwdW12")
        attachment.type = "application/pdf"
        attachment.filename = "balance_001.pdf"
        attachment.disposition = "attachment"
        attachment.content_id = "Balance Sheet"
        return attachment
        ```
        """
        sendgridattachment = SendGridAttachment()
        sendgridattachment.content = base64.b64encode(attachment.binarycontent).decode()
        sendgridattachment.type = attachment.type
        sendgridattachment.filename = attachment.originalfilename
        sendgridattachment.disposition = "attachment"
        sendgridattachment.content_id = attachment.originalfilename

        return sendgridattachment
