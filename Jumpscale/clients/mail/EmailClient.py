from Jumpscale import j
import smtplib
import mimetypes
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

JSConfigFactory = j.application.JSFactoryBaseClass
JSConfigClient = j.application.JSBaseClass
TEMPLATE = """
smtp_server = ""
smtp_port = 0
login = ""
password = ""
from = ""
"""


class EmailClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        config = self.config.data
        self._server = config['smtp_server']
        self._port = config['smtp_port']
        self._ssl = self._port in [465, 587]
        self._username = config.get('login')
        self._password = config.get('password')
        self._sender = config.get('from')

    def __str__(self):
        out = "server=%s\n" % (self._server)
        out += "port=%s\n" % (self._port)
        out += "username=%s\n" % (self._username)
        return out

    __repr__ = __str__

    def send(self, recipients, sender="", subject="", message="", files=None, mimetype=None):
        """
        @param recipients: Recipients of the message
        @type recipients: mixed, string or list
        @param sender: Sender of the email
        @type sender: string
        @param subject: Subject of the email
        @type subject: string
        @param message: Body of the email
        @type message: string
        @param files: List of paths to files to attach
        @type files: list of strings
        @param mimetype: Type of the body plain, html or None for autodetection
        @type mimetype: string
        """
        if not sender:
            sender = self._sender
        if isinstance(recipients, str):
            recipients = [recipients]
        server = smtplib.SMTP(self._server, self._port)
        server.ehlo()
        if self._ssl:
            server.starttls()
        if self._username:
            server.login(self._username, self._password)

        if mimetype is None:
            if '<html>' in message:
                mimetype = 'html'
            else:
                mimetype = 'plain'

        msg = MIMEText(message, mimetype)

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ','.join(recipients)

        if files:
            txtmsg = msg
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ','.join(recipients)
            msg.attach(txtmsg)
            for fl in files:
                # Guess the content type based on the file's extension.  Encoding
                # will be ignored, although we should check for simple things like
                # gzip'd or compressed files.
                filename = j.sal.fs.getBaseName(fl)
                ctype, encoding = mimetypes.guess_type(fl)
                content = j.sal.fs.readFile(fl)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                if maintype == 'text':
                    attachement = MIMEText(content, _subtype=subtype)
                elif maintype == 'image':
                    attachement = MIMEImage(content, _subtype=subtype)
                elif maintype == 'audio':
                    attachement = MIMEAudio(content, _subtype=subtype)
                else:
                    attachement = MIMEBase(maintype, subtype)
                    attachement.set_payload(content)
                    # Encode the payload using Base64
                    encoders.encode_base64(attachement)
                # Set the filename parameter
                attachement.add_header(
                    'Content-Disposition', 'attachment', filename=filename)
                msg.attach(attachement)
        server.sendmail(sender, recipients, msg.as_string())
        server.close()

    # def sendmail(self, ffrom, to, subject, msg, smtpuser, smtppasswd,
    #              smtpserver="smtp.mandrillapp.com", port=587, html=""):
    #     from email.mime.multipart import MIMEMultipart
    #     from email.mime.text import MIMEText
    #
    #     msg = MIMEMultipart('alternative')
    #
    #     msg['Subject'] = subject
    #     msg['From'] = ffrom
    #     msg['To'] = to
    #
    #     if msg != "":
    #         part1 = MIMEText(str(msg), 'plain')
    #         msg.attach(part1)
    #
    #     if html != "":
    #         part2 = MIMEText(html, 'html')
    #         msg.attach(part2)
    #
    #     s = smtplib.SMTP(smtpserver, port)
    #
    #     s.login(smtpuser, smtppasswd)
    #     s.sendmail(msg['From'], msg['To'], msg.as_string())
    #
    #     s.quit()


class EmailClientFactory(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.email"
        JSConfigFactory.__init__(self, EmailClient)
