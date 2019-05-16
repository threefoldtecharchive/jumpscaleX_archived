import base64
from Jumpscale import j


class FilesystemManager:
    def __init__(self, client):
        self._client = client

    def open(self, file, mode="r", perm=0o0644):
        """
        Opens a file on the node

        :param file: file path to open
        :param mode: open mode
        :param perm: file permission in octet form

        mode:
          'r' read only
          'w' write only (truncate)
          '+' read/write
          'x' create if not exist
          'a' append
        :return: a file descriptor
        """
        args = {"file": file, "mode": mode, "perm": perm}

        return self._client.json("filesystem.open", args)

    def exists(self, path):
        """
        Check if path exists

        :param path: path to file/dir
        :return: boolean
        """
        args = {"path": path}

        return self._client.json("filesystem.exists", args)

    def list(self, path):
        """
        List all entries in directory
        :param path: path to dir
        :return: list of director entries
        """
        args = {"path": path}

        return self._client.json("filesystem.list", args)

    def mkdir(self, path):
        """
        Make a new directory == mkdir -p path
        :param path: path to directory to create
        :return:
        """
        args = {"path": path}

        return self._client.json("filesystem.mkdir", args)

    def remove(self, path):
        """
        Removes a path (recursively)

        :param path: path to remove
        :return:
        """
        args = {"path": path}

        return self._client.json("filesystem.remove", args)

    def move(self, path, destination):
        """
        Move a path to destination

        :param path: source
        :param destination: destination
        :return:
        """
        args = {"path": path, "destination": destination}

        return self._client.json("filesystem.move", args)

    def chmod(self, path, mode, recursive=False):
        """
        Change file/dir permission

        :param path: path of file/dir to change
        :param mode: octet mode
        :param recursive: apply chmod recursively
        :return:
        """
        args = {"path": path, "mode": mode, "recursive": recursive}

        return self._client.json("filesystem.chmod", args)

    def chown(self, path, user, group, recursive=False):
        """
        Change file/dir owner

        :param path: path of file/dir
        :param user: user name
        :param group: group name
        :param recursive: apply chown recursively
        :return:
        """
        args = {"path": path, "user": user, "group": group, "recursive": recursive}

        return self._client.json("filesystem.chown", args)

    def read(self, fd):
        """
        Read a block from the given file descriptor

        :param fd: file descriptor
        :return: bytes
        """
        args = {"fd": fd}

        data = self._client.json("filesystem.read", args)
        return base64.decodebytes(data.encode())

    def write(self, fd, bytes):
        """
        Write a block of bytes to an open file descriptor (that is open with one of the writing modes

        :param fd: file descriptor
        :param bytes: bytes block to write
        :return:

        :note: don't overkill the node with large byte chunks, also for large file upload check the upload method.
        """
        args = {"fd": fd, "block": base64.encodebytes(bytes).decode()}

        return self._client.json("filesystem.write", args)

    def close(self, fd):
        """
        Close file
        :param fd: file descriptor
        :return:
        """
        args = {"fd": fd}

        return self._client.json("filesystem.close", args)

    def upload(self, remote, reader):
        """
        Uploads a file
        :param remote: remote file name
        :param reader: an object that implements the read(size) method (typically a file descriptor)
        :return:
        """

        fd = self.open(remote, "w")
        while True:
            chunk = reader.read(512 * 1024)
            if chunk == b"":
                break
            self.write(fd, chunk)
        self.close(fd)

    def download(self, remote, writer):
        """
        Downloads a file
        :param remote: remote file name
        :param writer: an object the implements the write(bytes) interface (typical a file descriptor)
        :return:
        """

        fd = self.open(remote)
        while True:
            chunk = self.read(fd)
            if chunk == b"":
                break
            writer.write(chunk)
        self.close(fd)

    def upload_file(self, remote, local):
        """
        Uploads a file
        :param remote: remote file name
        :param local: local file name
        :return:
        """
        file = open(local, "rb")
        try:
            self.upload(remote, file)
        finally:
            file.close()

    def download_file(self, remote, local):
        """
        Downloads a file
        :param remote: remote file name
        :param local: local file name
        :return:
        """
        file = open(local, "wb")
        try:
            self.download(remote, file)
        finally:
            file.close()
