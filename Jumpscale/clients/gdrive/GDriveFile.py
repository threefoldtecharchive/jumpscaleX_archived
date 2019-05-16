from Jumpscale import j
from dateutil import parser
import copy
from apiclient.http import *
from apiclient.http import MediaIoBaseDownload

GOOGLEMIME = [
    "application/vnd.google-apps.audio",
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.drawing",
    "application/vnd.google-apps.file",
    "application/vnd.google-apps.folder",
    "application/vnd.google-apps.form",
    "application/vnd.google-apps.fusiontable",
    "application/vnd.google-apps.map",
    "application/vnd.google-apps.photo",
    "application/vnd.google-apps.presentation",
    "application/vnd.google-apps.script",
    "application/vnd.google-apps.sites",
    "application/vnd.google-apps.spreadsheet",
    "application/vnd.google-apps.unknown",
    "application/vnd.google-apps.video",
    "application/vnd.google-apps.drive-sdk",
]


class GDriveFile:
    def __init__(self, service, id="", json=""):
        self.service = service
        self._mime_type = None
        self._gmd = None

        if id.startswith("http"):
            id = id.replace("/edit", "")
            id = id.rstrip("/")
            id = id.split("/")[-1]

        self.id = id

        self._init(json=json)

    def _init(self, json):

        # BASIC INIT

        self.name = ""
        self.sid = ""
        self.company = ""
        self.customer = ""
        self.project = ""
        self.description = ""
        self.remarks = []
        self.modTime = 0
        self.downloadDate = 0
        self.version = 0
        self.extension = ""
        self.binary = True
        self.changed = False
        self.fileChanged = False

        if json == "" and "description" in self.gmd:
            json = self.gmd["description"]

        try:
            self.__dict__.update(j.data.serializers.json.loads(json))

        except BaseException:
            self.changed = True
            self.description = json  # the old description

        self.changed = True

        name = self.gmd.get("name")
        if (
            name == "Untitled document"
            or name == "Untitled spreadsheet"
            or name == "Untitled presentation"
            or name == ""
        ):
            # name = j.data.time.getLocalTimeHR().replace(' ', '-').replace('/', '_')
            raise j.exceptions.Input(message="Cannot process doc:%s" % self)

        if "<" in name and ">" in name:
            self.sid = name.split("<", 1)[1].split(">", 1)[0]
        else:
            self.sid = j.data.idgenerator.generateXCharID(4)
        self.name = name.split("<", 1)[0].strip()

        if self.sid.replace(".", "").strip() == "":
            self.sid = j.data.idgenerator.generateXCharID(4)

        modtime = self.gmd.get("modifiedTime")
        if modtime is not None:
            modtime = parser.parse(modtime)
            self.modTime = int(j.data.time.any2epoch(modtime))

        self.version = self.gmd.get("version")

        self._getMimeType()

    @property
    def gmd(self):
        if self._gmd is None:
            self._gmd = self.service.files().get(fileId=self.id).execute()
        return self._gmd

    @property
    def mimetype(self):
        if self._mime_type is None:
            self._getMimeType()
        return self._mime_type

    def _getMimeType(self):

        mime_type = self.gmd.get("mimeType")

        if mime_type in GOOGLEMIME:
            self.binary = False

        if mime_type == "application/vnd.google-apps.document":
            self._mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            self.extension = "docx"
        elif mime_type == "application/vnd.google-apps.spreadsheet":
            self._mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            self.extension = "xlsx"
        elif mime_type == "application/vnd.google-apps.presentation":
            self._mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            self.extension = "pptx"
        elif mime_type == "":
            self._mime_type = "text/plain"
            self.extension = "txt"

    @property
    def json(self):
        data = copy.copy(self.__dict__)
        data.pop("_gmd")
        data.pop("_mime_type")
        data.pop("fileChanged")
        data.pop("changed")
        return j.data.serializers.json.dumps(data, True, True)

    def saveMetadata(self):
        if self.changed:
            name2 = "%s <%s>" % (self.name, self.sid)
            self.service.files().update(fileId=self.id, body={"description": self.json, "name": name2}).execute()
            self.changed = False

    def exportPDF(self, path=""):
        self.export(path, pdf=True)

    def export(self, path="", pdf=False):

        if self.extension == "" or pdf:
            new_type = "application/pdf"
            extension = "pdf"
        else:
            extension = self.extension

        if path == "":
            path = "/tmp/gdrive/%s__%s.%s" % (self.sid, self.name, extension)

        if not self.binary:
            # Not suitable for large files. MediaIoBaseDownload has a bug. See:
            # https://github.com/google/google-api-python-client/issues/15

            if self.extension == "" or pdf:
                new_type = "application/pdf"
            else:
                new_type = self.mimetype

            request = self.service.files().export_media(fileId=self.id, mimeType=new_type)
            response = request.execute()
            with open(path, "wb") as wer:
                wer.write(response)
            return

        else:
            request = self.service.files().get_media(fileId=self.id)
            with open(path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

    def save(self):
        if self.changed:
            self.saveMetadata()

    def __str__(self):
        return "gdoc: %s:%s" % (self.name, self.sid)

    __repr__ = __str__
