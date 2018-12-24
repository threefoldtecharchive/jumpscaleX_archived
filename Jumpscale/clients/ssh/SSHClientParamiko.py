import io
from io import StringIO
import paramiko
import functools
import threading
import queue
import socket
import time
import os
from Jumpscale import j
from paramiko.ssh_exception import (AuthenticationException,
                                    BadHostKeyException, SSHException, BadAuthenticationType)
from .SSHClientBase import SSHClientBase
from .StreamReader import StreamReader


class SSHClientParamiko(SSHClientBase):

    def _init(self):
        SSHClientBase._init(self)
        # key_filename = self.sshkey.path if (self.sshkey and self.sshkey.path) else None
        self._lock = threading.Lock()
        if self.passwd:
            self.forward_agent = False
            self.look_for_keys = False
            # self.key_filename = None
            self.passphrase = None
        else:
            self.look_for_keys = True

        self._transport = None
        self._client = None
        self._logger_enable()

    def _test_local_agent(self):
        """
        try to connect to the local ssh-agent
        return True if local agent is running, False if not
        """
        agent = paramiko.Agent()
        if len(agent.get_keys()) == 0:
            return False
        else:
            return True

    @property
    def client(self):
        if self._client is None:
            self._connect()
        return self._client

    def connect(self):
        return self._connect()

    def reset(self):
        with self._lock:
            if self._client is not None:
                self._client = None

    @property
    def sftp(self):
        return self.client.open_sftp()

    def _make_sftp(self):
        """Make SFTP client from open transport"""
        transport = self.transport
        transport.open_session()
        return paramiko.SFTPClient.from_transport(transport)

    def _mkdir(self, sftp, directory):
        """Make directory via SFTP channel

        :param sftp: SFTP client object
        :type sftp: :py:class:`paramiko.sftp_client.SFTPClient`
        :param directory: Remote directory to create
        :type directory: str

        Catches and logs at error level remote IOErrors on creating directory.
        """
        try:
            sftp.mkdir(directory)
        except IOError as error:
            msg = "Error occured creating directory %s on %s - %s"
            self._logger.error(msg, directory, self.host, error)
            raise IOError(msg, directory, self.host, error)
        self._logger.debug("Creating remote directory %s", directory)
        return True

    def mkdir(self, sftp, directory):
        """Make directory via SFTP channel.

        Parent paths in the directory are created if they do not exist.

        :param sftp: SFTP client object
        :type sftp: :py:class:`paramiko.sftp_client.SFTPClient`
        :param directory: Remote directory to create
        :type directory: str

        Catches and logs at error level remote IOErrors on creating directory.
        """
        try:
            parent_path, sub_dirs = directory.split(os.path.sep, 1)
        except ValueError:
            parent_path = directory.split(os.path.sep, 1)[0]
            sub_dirs = None
        if not parent_path and directory.startswith(os.path.sep):
            try:
                parent_path, sub_dirs = sub_dirs.split(os.path.sep, 1)
            except ValueError:
                return True
        try:
            sftp.stat(parent_path)
        except IOError:
            self._mkdir(sftp, parent_path)
        sftp.chdir(parent_path)
        if sub_dirs:
            return self.mkdir(sftp, sub_dirs)
        return True

    def _parent_paths_split(self, file_path, sep=None):
        sep = os.path.sep if sep is None else sep
        try:
            destination = sep.join(
                [_dir for _dir in file_path.split(os.path.sep)
                 if _dir][:-1])
        except IndexError:
            destination = ''
        if file_path.startswith(sep) or not destination:
            destination = sep + destination
        return destination

    def _copy_dir(self, local_dir, remote_dir, sftp):
        """Call copy_file on every file in the specified directory, copying
        them to the specified remote directory."""
        file_list = os.listdir(local_dir)
        for file_name in file_list:
            local_path = os.path.join(local_dir, file_name)
            remote_path = '/'.join([remote_dir, file_name])
            self.copy_file(local_path, remote_path, recurse=True,
                           sftp=sftp)

    def copy_file(self, local_file, remote_file, recurse=False,
                  sftp=None):
        """Copy local file to host via SFTP/SCP

        Copy is done natively using SFTP/SCP version 2 protocol, no scp command
        is used or required.

        :param local_file: Local filepath to copy to remote host
        :type local_file: str
        :param remote_file: Remote filepath on remote host to copy file to
        :type remote_file: str
        :param recurse: Whether or not to descend into directories recursively.
        :type recurse: bool

        :raises: :py:class:`ValueError` when a directory is supplied to
          ``local_file`` and ``recurse`` is not set
        :raises: :py:class:`IOError` on I/O errors writing files
        :raises: :py:class:`OSError` on OS errors like permission denied
        """
        if os.path.isdir(local_file) and recurse:
            return self._copy_dir(local_file, remote_file, sftp)
        elif os.path.isdir(local_file) and not recurse:
            raise ValueError("Recurse must be true if local_file is a "
                             "directory.")
        sftp = self._make_sftp() if not sftp else sftp
        destination = self._parent_paths_split(remote_file, sep='/')
        try:
            sftp.stat(destination)
        except IOError:
            self.mkdir(sftp, destination)
        sftp.chdir()
        try:
            sftp.put(local_file, remote_file)
        except Exception as error:
            self._logger.error("Error occured copying file %s to remote destination "
                              "%s:%s - %s",
                              local_file, self.host, remote_file, error)
            raise error
        self._logger.debug("Copied local file %s to remote destination %s",
                         local_file, remote_file)

    @property
    def transport(self):
        if self.client is None:
            raise j.exceptions.RuntimeError("Could not connect to %s:%s" % (self.addr, self.port))
        r = self.client.get_transport()
        if r is None:
            raise RuntimeError("transport cannot be None")
        return r

    def _connect(self):
        if self.addr == "" or self.port == 0:
            raise RuntimeError("addr or port cannot be empty.")
        with self._lock:
            self._logger.debug("Test sync ssh connection to %s:%s:%s" % (self.addr, self.port, self.login))

        if j.sal.nettools.waitConnectionTest(self.addr, self.port, self.timeout) is False:
            self._logger.error("Cannot connect to ssh server %s:%s with login:%s and using sshkey:%s" %
                              (self.addr, self.port, self.login, self.key_filename))
            raise RuntimeError("Could not connect to addr:'%s' port:'%s'"%(self.addr,self.port))

        # self.pkey = None
        # if self.key_filename is not None and self.key_filename != '':
        #     self.pkey = paramiko.RSAKey.from_private_key_file(
        #         self.sshkey.path, password=self.sshkey.passphrase)

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # if self.key_filename:
        #     self.allow_agent = True
        #     self.look_for_keys = True
        #     # if j.clients.ssh.SSHKeyGetPathFromAgent(self.key_filename, die=False) is not None and not self.passphrase:
        #     #     j.clients.ssh.ssh_keys_load(self.key_filename)

        start = j.data.time.getTimeEpoch()

        while start + self.timeout > j.data.time.getTimeEpoch():
            try:
                self._logger.info("connect to:%s" % self.addr)
                self._logger.debug("connect with port :%s" % self.port)
                self._logger.debug("connect with username :%s" % self.login)
                self._logger.debug("connect with password :%s" % self.passwd)
                # self._logger.debug("connect with pkey :%s" % self.pkey)
                self._logger.debug("connect with allow_agent :%s" %self.allow_agent)
                self._logger.debug("connect with look_for_keys :%s" % self.look_for_keys)
                self._logger.debug("Timeout is : %s " % self.timeout)
                self._client.connect(
                    self.addr,
                    int(self.port),
                    username=self.login,
                    password=self.passwd,
                    # pkey=self.pkey,
                    allow_agent=self.allow_agent,
                    look_for_keys=self.look_for_keys,
                    timeout=2.0,
                    banner_timeout=3.0)
                self._logger.info("connection ok")
                return self._client
            except BadAuthenticationType as e:
                raise e
            except (BadHostKeyException, AuthenticationException) as e:
                self._logger.error(
                    "Authentification error. Aborting connection : %s" % str(e))
                self._logger.error(str(e))
                raise j.exceptions.RuntimeError(str(e))

            except (SSHException, socket.error) as e:
                self._logger.error("Unexpected error in socket connection for ssh. Aborting connection and try again.")
                self._logger.error(e)
                self._client.close()
                # self.reset()
                time.sleep(0.1)
                continue

            except Exception as e:
                # j.clients.ssh.removeFromCache(self)
                msg = "Could not connect to ssh on %s@%s:%s. Error was: %s" % (self.login, self.addr, self.port, e)
                raise j.exceptions.RuntimeError(msg)


        raise j.exceptions.RuntimeError(
                'Impossible to create SSH connection to %s:%s' % (self.addr, self.port))

    def execute(self, cmd, showout=True, die=True, timeout=None):
        """
        run cmd & return
        return: (retcode,out_err)
        """
        ch = None
        # with self._lock:
        ch = self.transport.open_session()

        if self.forward_agent:
            paramiko.agent.AgentRequestHandler(ch)

        # execute the command on the remote server
        ch.exec_command(cmd)
        # indicate that we're not going to write to that channel anymore
        ch.shutdown_write()
        # create file like object for stdout and stderr to read output of
        # command
        stdout = ch.makefile('r')
        stderr = ch.makefile_stderr('r')

        # Start stream reader thread that will read strout and strerr
        inp = queue.Queue()
        outReader = StreamReader(stdout, ch, inp, 'O')
        errReader = StreamReader(stderr, ch, inp, 'E')
        outReader.start()
        errReader.start()

        err = io.StringIO()  # error buffer
        out = io.StringIO()  # stdout buffer
        out_eof = False
        err_eof = False

        while out_eof is False or err_eof is False:
            try:
                chan, line = inp.get(block=True, timeout=1.0)
                if chan == 'T':
                    if line == 'O':
                        out_eof = True
                    elif line == 'E':
                        err_eof = True
                    continue
                line = j.core.text.toAscii(line)
                if chan == 'O':
                    if showout:
                        with self._lock:
                            self._logger.debug(line.rstrip())
                    out.write(line)
                elif chan == 'E':
                    if showout:
                        with self._lock:
                            self._logger.error(line.rstrip())
                    err.write(line)
            except queue.Empty:
                pass

        # stop the StreamReader and wait for the thread to finish
        outReader._stopped = True
        errReader._stopped = True
        outReader.join()
        errReader.join()

        # indicate that we're not going to read from this channel anymore
        ch.shutdown_read()
        # close the channel
        ch.close()

        # close all the pseudofiles
        stdout.close()
        stderr.close()

        rc = ch.recv_exit_status()

        if rc and die:
            raise j.exceptions.RuntimeError(
                "Cannot execute (ssh):\n%s\noutput:\n%serrors:\n%s" % (cmd, out.getvalue(), err.getvalue()))

        return rc, out.getvalue(), err.getvalue()

    def close(self):
        # TODO: make sure we don't need to clean anything
        pass

    def rsync_up(self, source, dest, recursive=True):
        if dest[0] != "/":
            raise j.exceptions.RuntimeError("dest path should be absolute")

        dest = "%s@%s:%s" % (
            self.config.data['login'], self.addr_variable, dest)
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=True,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=[
                ".egg-info",
                ".dist-info",
                "__pycache__"],
            ignorefiles=[".egg-info"],
            rsync=True,
            ssh=True,
            sshport=self.port_variable,
            recursive=recursive)

    def rsync_down(self, source, dest, source_prefix="", recursive=True):
        if source[0] != "/":
            raise j.exceptions.RuntimeError("source path should be absolute")
        source = "%s@%s:%s" % (
            self.config.data['login'], self.addr_variable, source)
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=True,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=[
                ".egg-info",
                ".dist-info"],
            ignorefiles=[".egg-info"],
            rsync=True,
            ssh=True,
            sshport=self.port_variable,
            recursive=recursive)



    def portforwardToLocal(self, remoteport, localport):
        self.portforwardKill(localport)
        C = "ssh -L %s:localhost:%s root@%s -p %s" % (
            remoteport, localport, self.addr, self.port)
        print(C)
        pm = j.core.builder.system.processmanager.get()
        pm.ensure(cmd=C, name="ssh_%s" % localport, wait=0.5)
        print("Test tcp port to:%s" % localport)
        if not j.sal.nettools.waitConnectionTest("127.0.0.1", localport, 10):
            raise RuntimeError("Cannot open ssh forward:%s_%s_%s" %
                               (self, remoteport, localport))
        print("Connection ok")

    def portforwardKill(self, localport):
        print("kill portforward %s" % localport)
        pm = j.core.builder.system.processmanager.get()
        pm.processmanager.stop('ssh_%s' % localport)

    # def SSHAuthorizeKey(
    #         self,
    #         keyname=None, keydata=None):
    #     """
    #     @keyname name of the key as loaded in ssh-agent if set keydata will be ignored(this requires ssh-agent to be loaded)
    #     @keydata actual data of private key if set keyname will be ignored
    #     """
    #     if keydata:
    #         key_des = StringIO(keydata)
    #         p = paramiko.RSAKey.from_private_key(key_des)
    #         key = '%s ' % p.get_name() + p.get_base64()
    #     elif not keyname:
    #         raise j.exceptions.Input("keyname and keydata can't be both empty")
    #     else:
    #         key = j.clients.ssh.SSHKeyGetFromAgentPub(keyname)

    #     rc, _, _ = self.execute(
    #         "echo '%s' | sudo -S bash -c 'test -e /root/.ssh'" % self.passwd, die=False)
    #     mkdir_cmd = ''
    #     if rc > 0:
    #         mkdir_cmd = 'mkdir -p /root/.ssh;'

    #     cmd = '''echo '%s' | sudo -S bash -c "%s echo '\n%s' >> /root/.ssh/authorized_keys; chmod 644 /root/.ssh/authorized_keys;chown root:root /root/.ssh/authorized_keys"''' % (
    #         self.passwd, mkdir_cmd, key)
    #     self.execute(cmd, showout=False)

    #     j.clients.ssh.remove_item_from_known_hosts(self.addr)
