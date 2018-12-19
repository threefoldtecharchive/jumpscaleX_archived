import io
import functools
from Jumpscale import j
from .SSHClientBase import SSHClientBase


class SSHClient(SSHClientBase):


    def _init(self):
        SSHClientBase._init(self)
        self._logger = j.logger.get("ssh client: %s:%s(%s)" % (self.addr_variable, self.port, self.login))
        self._client = None


    @property
    def client(self):
        pkey = self.sshkey.path if (self.sshkey and self.sshkey.path) else None
        passwd = self.passwd
        if pkey:
            passwd = self.sshkey.passphrase

        from pssh.ssh2_client import SSHClient as PSSHClient
        PSSHClient = functools.partial(PSSHClient, retry_delay=1)

        self._client = PSSHClient(self.addr_variable,
                                  user=self.login,
                                  password=passwd,
                                  port=self.port,
                                  pkey=pkey,
                                  num_retries=self.timeout / 6,
                                  allow_agent=self.allow_agent,
                                  timeout=5)

        return self._client

    def execute(self, cmd, showout=True, die=True, timeout=None):
        print ("execute", cmd, showout, die, timeout)
        channel, _, stdout, stderr, _ = self.client.run_command(cmd, timeout=timeout)
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

    def connect(self):
        self.client

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
    #     self.forward_agent = True
    #     self._client = client
    #     self._client.connect(**cfg)

    #     return self._client

    def reset(self):
        with self._lock:
            if self._client is not None:
                self._client = None

    @property
    def sftp(self):
        return self.client._make_sftp()

    def close(self):
        # TODO: make sure we don't need to clean anything
        pass

    def copy_file(self, local_file, remote_file, recurse=False, sftp=None):
        return self.client.copy_file(local_file, remote_file, recurse=recurse, sftp=sftp)

    def rsync_up(self, source, dest, recursive=True):
        if dest[0] != "/":
            raise j.exceptions.RuntimeError("dest path should be absolute")

        dest = "%s@%s:%s" % (self.login, self.addr_variable, dest)
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
        source = "%s@%s:%s" % (self.login, self.addr_variable, source)
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

