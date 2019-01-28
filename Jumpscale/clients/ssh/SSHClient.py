import io
import functools
from Jumpscale import j
from .SSHClientBase import SSHClientBase


class SSHClient(SSHClientBase):




    def _init(self):
        SSHClientBase._init(self)
        self._logger = j.logger.get("ssh client: %s:%s(%s)" % (self.addr_variable, self.port, self.login))

    @property
    def _client(self):
        if self._client_ is None:
            pkey = self.sshkey_obj.path if (self.sshkey_obj and self.sshkey_obj.path) else None
            passwd = self.passwd
            if pkey:
                passwd = self.sshkey_obj.passphrase

            from pssh.ssh2_client import SSHClient as PSSHClient
            PSSHClient = functools.partial(PSSHClient, retry_delay=1)

            self._client_ = PSSHClient(self.addr_variable,
                                      user=self.login,
                                      password=passwd,
                                      port=self.port,
                                      pkey=pkey,
                                      num_retries=self.timeout / 6,
                                      allow_agent=self.allow_agent,
                                      timeout=5)

        return self._client_

    def execute(self, cmd, showout=True, die=True, timeout=None):
        # print ("execute", cmd, showout, die, timeout)
        channel, _, stdout, stderr, _ = self._client.run_command(cmd, timeout=timeout)
        # self._client.wait_finished(channel)

        def _consume_stream(stream, printer, buf=None):
            buffer = buf or io.StringIO()
            for line in stream:
                buffer.write(line + '\n')
                if showout:
                    printer(line)
            return buffer

        out = _consume_stream(stdout, self._logger.debug)
        err = _consume_stream(stderr, self._logger.error)
        self._client.wait_finished(channel)
        _consume_stream(stdout, self._logger.debug, out)
        _consume_stream(stderr, self._logger.error, err)

        rc = channel.get_exit_status()
        output = out.getvalue()
        out.close()
        error = err.getvalue()
        err.close()
        channel.close()

        if rc and die:
            raise j.exceptions.RuntimeError("Cannot execute (ssh):\n%s\noutput:\n%serrors:\n%s" % (cmd, output, error))

        return rc, output, error


    # def connectViaProxy(self, host, username, port, identityfile, proxycommand=None):
    #     # TODO: Fix this
    #     self.usesproxy = True
    #     client = paramiko.SSHClient()
    #     client._policy = paramiko.WarningPolicy()
    #     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     import os.path
    #     self.host = host
    #     cfg = {'hostname': host, 'username': username, "port": port}
    #     self.addr = host
    #     self.user = username

    #     if identityfile is not None:
    #         cfg['key_filename'] = identityfile
    #         self.key_filename = cfg['key_filename']

    #     if proxycommand is not None:
    #         cfg['sock'] = paramiko.ProxyCommand(proxycommand)
    #     cfg['timeout'] = 5
    #     cfg['allow_agent'] = True
    #     cfg['banner_timeout'] = 5
    #     self.cfg = cfg
    #     self._forward_agent = True
    #     self._client = client
    #     self._client.connect(**cfg)

    #     return self._client

    def _reset(self):
        with self._lock:
            if self._client is not None:
                self._client = None

    @property
    def sftp(self):
        if self._ftp is None:
            self._ftp = self._client._make_sftp()
        return self._ftp

    def _close(self):
        # TODO: make sure we don't need to clean anything
        pass

    # def copy_file(self, local_file, remote_file, recurse=False):
    #     #DOES THIS WORK?
    #     return self._client.copy_file(local_file, remote_file, recurse=recurse, sftp=self.sftp)



