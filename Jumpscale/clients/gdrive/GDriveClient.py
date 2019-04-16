import Jumpscale
from Jumpscale import j
from dateutil import parser
import os
import httplib2
import io

try:
    from googleapiclient.discovery import build
except BaseException:
    j.sal.process.execute("python3 -m pip install google-api-python-client")
from googleapiclient.discovery import build
from google.oauth2 import service_account

from .GDriveFile import *

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive.appdata',
          'https://www.googleapis.com/auth/drive.scripts',
          'https://www.googleapis.com/auth/drive.metadata']

APPLICATION_NAME = 'Google Drive Exporter'

JSConfigClient = j.application.JSBaseConfigClass


class GDriveClient(JSConfigClient):
    _SCHEMATEXT = """
    @url =  jumpscale.sonic.client
    name* = "" (S)
    credfile = "" (S)
    """

    def _init(self):
        self._credentials = None

    @property
    def credentials(self):
        if not self._credentials:
            self._credentials = service_account.Credentials.from_service_account_file(self.credfile, scopes=SCOPES)
        return self._credentials

    def service_get(self, name="drive", version="v3"):
        return build(name, version, credentials=self.credentials)

    def getFile(self, file_id, service_name="drive", service_version="v3"):
        file = GDriveFile(self.service_get(service_name, service_version), id=file_id)
        return file

    def exportSlides(self, presentation, destpath="/tmp", staticdir=None, size='MEDIUM'):
        from Jumpscale.tools.googleslides.slides2html.downloader import Downloader
        # presentation should be the guid 
        # should extract the presentation if full path
        os.makedirs(destpath, exist_ok=True)
        service = self.service_get("slides", "v1")
        downloader = Downloader(presentation, service, size)
        downloader.download(destpath)
        presentation_dir = j.sal.fs.joinPaths(destpath, presentation)
        slides = [x for x in os.listdir(presentation_dir) if "png" in x and "_" in x and "background_" not in x]
        for image in slides:
            imagepath = j.sal.fs.joinPaths(presentation_dir, image)
            slideimage = image.split("_",maxsplit=1)[1]   # 00_asdsadasda.png remove the leading zeros and _
            newimagepath = j.sal.fs.joinPaths(presentation_dir, slideimage)
            j.sal.fs.moveFile(imagepath, newimagepath)
        if staticdir:
            j.sal.fs.moveDir(presentation_dir, staticdir)