
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