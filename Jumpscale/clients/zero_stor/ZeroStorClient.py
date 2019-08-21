from Jumpscale import j
import grpc

from . import file
from . import data
from . import metadata


JSConfigBase = j.application.JSBaseConfigClass


class ZeroStorClient(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.zstor.client
    name* = "" (S)
    ip = "127.0.0.1" (ipaddress)
    port = 8000 (ipport)
    """

    def _init(self, **kwargs):
        channel = grpc.insecure_channel("%s:%s" % (self.ip, self.port))

        # initialize stubs
        self._file = file.File(channel)
        self._zstor_data = data.Data(channel)
        self._metadata = metadata.Metadata(channel)

    def write(self, data, *kwargs):
        """
        Write date to 0-store
        :param data: data (bytes)
        :return: chunks
        """
        return self._zstor_data.write(data)

    def read(self, chunks):
        """
        Read data from 0-stor
        :param chunk: chunks as returned by a write() call
        :return: data 
        :rtype: bytes
        """
        return self._zstor_data.read(chunks)

    def write_file(self, path, *kwargs):
        """
        upload file to 0-stor
        :param path: path to local file to upload
        :return: file chunks
        """
        return self._zstor_data.write_file(path)

    def read_file(self, chunks, file_path, sync_io=False, **kwargs):
        """
        read file from 0-stor
        :param chunks: file chunks as returned from write_file
        :param file_path: local file path to download to
        :param sync_io: use the O_SYNC on the file, forcing all write operation to be writen to the
                        underlying hardware before returning.
        :param mode: 0 = truncate, 1 = append, 2 = exclusive
        """
        return self._zstor_data.read_file(chunks=chunks, file_path=file_path, sync_io=sync_io, **kwargs)

    def write_stream(self, input, block_size=4096):
        """
        Upload data from a file like object (input)
        :param input: file like object (implements a read function which return 'bytes')
        :param block_size: block size used to call input.read(block_size)
        :note: if input is an open file, make sure it's open in binary mode
        :return: metadata object
        """
        return self._zstor_data.write_stream(input=input, block_size=block_size)

    def read_stream(self, chunks, output, chunk_size=4096):
        """
        Download data to a file like object (output)
        :param chunks: chunks as returned by write_stream
        :param chunk_size: read chunk size in bytes
        :param output: file like object (implements a write function which takey 'bytes')
        """
        return self._zstor_data.read_stream(chunks=chunks, output=output, chunk_size=chunk_size)

    def delete(self, chunks):
        """
        Delete a data with chunks
        :param chunks: chunks as returned by write
        """
        return self._zstor_data.delete(chunks=chunks)

    def check(self, chunks, fast=True):
        """
        Checks data state with key
        :param chunks: chunks as returned by write
        """
        return self._zstor_data.check(chunks=chunks, fast=fast)

    def repair(self, chunks):
        """
        Repairs a file
        :param chunks: chunks as returned by write
        """
        return self._zstor_data.repair(chunks=chunks)

    def startClient(self):
        """
        """
        # use prefab to start the client so we can connect to it using grpc
        raise j.exceptions.NotImplemented()
