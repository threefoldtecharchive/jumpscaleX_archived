
from __future__ import with_statement
import os

from Jumpscale import j
from .BuilderToolsLib import *

# import pygments.lexers
# from pygments.formatters import get_formatter_by_name


class BuilderTools(j.builder.system._BaseClass):

    __jslocation__ = "j.builder.tools"

    def _init(self):

        self._cd = '/tmp'

    def shell_safe(self, path):
        SHELL_ESCAPE = " '\";`|"
        """Makes sure that the given path/string is escaped and safe for shell"""
        path = "".join([("\\" + _) if _ in SHELL_ESCAPE else _ for _ in path])
        return path

    # =============================================================================
    #
    # SYSTEM
    #
    # =============================================================================

    def pprint(self, text, lexer="bash"):
        """
        @format py3, bash
        """
        text = j.core.tools.text_replace(text)
        return j.core.text.print(text, lexer=lexer)

    def system_uuid_alias_add(self):
        """Adds system UUID alias to /etc/hosts.
        Some tools/processes rely/want the hostname as an alias in
        /etc/hosts e.g. `127.0.0.1 localhost <hostname>`.
        """
        old = "127.0.0.1 localhost"
        new = old + " " + self.system_uuid()
        self.file_update(
            '/etc/hosts', lambda x: text_replace_line(x, old, new)[0])

    def system_uuid(self):
        """Gets a machines UUID (Universally Unique Identifier)."""
        return self.run('dmidecode -s system-uuid | tr "[A-Z]" "[a-z]"')

    # =============================================================================
    #
    # LOCALE
    #
    # =============================================================================

    def locale_check(self, locale):
        locale_data = self.run("locale -a | egrep '^%s$' ; true" % (locale,))
        return locale_data == locale

    def locale_ensure(self, locale):
        if not self.locale_check(locale):
            self.run("/usr/share/locales/install-language-pack %s" % (locale))
            self.run("dpkg-reconfigure locales")

    # =============================================================================
    #
    # FILE OPERATIONS
    #
    # =============================================================================

    def copyTree(self, source, dest, keepsymlinks=False, deletefirst=False,
                 overwriteFiles=True, ignoredir=[".egg-info", ".dist-info"], ignorefiles=[".egg-info"],
                 recursive=True, rsyncdelete=False, createdir=False):
        """
        std excludes are done like "__pycache__" no matter what you specify
        Recursively copy an entire directory tree rooted at src.
        The dest directory may already exist; if not,
        it will be created as well as missing parent directories
        @param source: string (source of directory tree to be copied)
        @param dest: string (path directory to be copied to...should not already exist)
        @param keepsymlinks: bool (True keeps symlinks instead of copying the content of the file)
        @param deletefirst: bool (Set to True if you want to erase destination first, be carefull, this can erase directories)
        @param overwriteFiles: if True will overwrite files, otherwise will not overwrite when destination exists
        """
        source = j.core.tools.text_replace(source)
        dest = j.core.tools.text_replace(dest)

        return j.sal.fs.copyDirTree(src=source, dst=dest, keepsymlinks=keepsymlinks, deletefirst=deletefirst,
                                    overwriteFiles=overwriteFiles, ignoredir=ignoredir, ignorefiles=ignorefiles,
                                    recursive=recursive, rsyncdelete=rsyncdelete, createdir=createdir)

    def file_backup(self, location, suffix=".orig", once=False):
        """Backups the file at the given location in the same directory, appending
        the given suffix. If `once` is True, then the backup will be skipped if
        there is already a backup file."""
        location = j.core.tools.text_replace(location)
        backup_location = location + suffix
        if once and self.file_exists(backup_location):
            return False
        else:
            return self.run("cp -a {0} {1}".format(
                location,
                self.shell_safe(backup_location)
            ))[1]

    def file_get_tmp_path(self, basepath=""):
        basepath = j.core.tools.text_replace(basepath)
        if basepath == "":
            x = "{DIR_TEMP}/%s" % j.data.idgenerator.generateXCharID(10)
        else:
            x = "{DIR_TEMP}/%s" % basepath
        x = j.core.tools.text_replace(x)
        return x

    def file_download(
            self,
            url,
            to="",
            overwrite=True,
            retry=3,
            timeout=0,
            login="",
            passwd="",
            minspeed=0,
            multithread=False,
            expand=False,
            minsizekb=40,
            removeTopDir=False,
            deletedest=False):
        """
        download from url
        @return path of downloaded file
        @param to is destination
        @param minspeed is kbytes per sec e.g. 50, if less than 50 kbytes during 10 min it will restart the download (curl only)
        @param when multithread True then will use aria2 download tool to get multiple threads
        @param removeTopDir : if True and there is only 1 dir in the destination then will move files away from the one dir to parent (often in tgz the top dir is not relevant)
        """

        to = j.core.tools.text_replace(to)

        # DO NOT CHANGE minsizekb<40, is to protect us against file not found, if
        # there is a specific need then change the argument only for that 1
        # usecase

        destination = to
        if expand and to != "":
            if overwrite:
                self.dir_remove(destination)

        if to == "" or expand:
            to = self.joinpaths("{DIR_TEMP}", j.sal.fs.getBaseName(url))

        to = j.core.tools.text_replace(to)

        if deletedest:
            self.dir_remove(to)

        if overwrite:
            if self.file_exists(to):
                j.sal.fs.remove(to)
                j.sal.fs.remove("%s.downloadok" % to)

        if not (self.file_exists(to) and self.file_exists("%s.downloadok" % to)):

            j.sal.fs.createDir(j.sal.fs.getDirName(to))

            if multithread is False:
                minspeed = 0
                if minspeed != 0:
                    minsp = "-y %s -Y 600" % (minspeed * 1024)
                else:
                    minsp = ""
                if login:
                    user = "--user %s:%s " % (login, passwd)
                else:
                    user = ""

                cmd = "curl -L '%s' -o '%s' %s %s --connect-timeout 30 --retry %s --retry-max-time %s" % (
                    url, to, user, minsp, retry, timeout)
                if self.file_exists(to):
                    cmd += " -C -"
                self._logger.info(cmd)
                j.sal.fs.remove("%s.downloadok" % to)
                rc, out, err = self.run(cmd, die=False, timeout=timeout)
                if rc == 33:  # resume is not support try again withouth resume
                    j.sal.fs.remove(to)
                    cmd = "curl -L '%s' -o '%s' %s %s --connect-timeout 5 --retry %s --retry-max-time %s" % (
                        url, to, user, minsp, retry, timeout)
                    rc, out, err = self.run(cmd, die=False, timeout=timeout)
                fsize = self.file_size(to)
                if minsizekb != 0 and fsize < minsizekb:
                    raise j.exceptions.RuntimeError(
                        "Could not download:{}.\nFile size too small after download {}kb.\n".format(url, fsize))
                if rc > 0:
                    raise j.exceptions.RuntimeError(
                        "Could not download:{}.\nErrorcode: {}.\n".format(url, rc))
                else:
                    self.touch("%s.downloadok" % to)
            else:
                raise j.exceptions.RuntimeError("not implemented yet")

        if expand:
            return self.file_expand(to, destination, removeTopDir=removeTopDir)

        return to

    def file_expand(self, path, destination="", removeTopDir=False):
        self._logger.info("file_expand:%s" % path)
        path = j.core.tools.text_replace(path)
        base = j.sal.fs.getBaseName(path)
        if base.endswith(".tgz"):
            base = base[:-4]
        elif base.endswith(".tar.gz"):
            base = base[:-7]
        elif base.endswith(".gz"):
            base = base[:-3]
        elif base.endswith(".bz2"):
            base = base[:-4]
        elif base.endswith(".xz"):
            base = base[:-3]
        elif base.endswith(".tar"):
            base = base[:-4]
        elif base.endswith(".zip"):
            base = base[:-4]
        else:
            raise RuntimeError("Cannot file expand, not supported")
        if destination == "":
            destination = self.joinpaths("{DIR_TEMP}", base)
        j.sal.fs.remove(destination)
        j.sal.fs.createDir(destination)
        path = j.core.tools.text_replace(path)
        destination = j.core.tools.text_replace(destination)
        self.dir_ensure(destination)
        if path.endswith(".tar.gz") or path.endswith(".tgz"):
            cmd = "tar -C %s -xzf %s" % (destination, path)
        elif path.endswith(".xz"):
            if self.isMac:
                self.prefab.system.package.install('xz')
            else:
                self.prefab.system.package.install('xz-utils')
            cmd = "tar -C %s -xzf %s" % (destination, path)
        elif path.endswith("tar.bz2"):
            #  cmd = "cd %s;bzip2 -d %s | tar xvf -" % (j.sal.fs.getDirName(path), path)
            cmd = "tar -C %s -jxvf %s" % (destination, path)
            #  tar -jxvf
        elif path.endswith(".bz2"):
            cmd = "cd %s;bzip2 -d %s" % (j.sal.fs.getDirName(path), path)
        elif path.endswith(".zip"):
            cmd = "cd %s;rm -rf %s;mkdir -p %s;cd %s;unzip %s" % (
                j.sal.fs.getDirName(path), base, base, base, path)
        else:
            raise j.exceptions.RuntimeError(
                "file_expand format not supported yet for %s" % path)

        # print(cmd)
        self.run(cmd)

        if removeTopDir:
            res = self.find(destination, recursive=False, type="d")
            if len(res) == 1:
                self.copyTree(res[0], destination)
                self.dir_remove(res[0])

        if self.dir_exists(self.joinpaths(destination, base)):
            return self.joinpaths(destination, base)
        return destination

    def touch(self, path):
        path = j.core.tools.text_replace(path)
        self.file_write(path, "")

    def file_read(self, location, default=None):
        location = j.core.tools.text_replace(location)
        import base64
        """Reads the *remote* file at the given location, if default is not `None`,
        default will be returned if the file does not exist."""
        location = j.core.tools.text_replace(location)
        if default is None:
            assert self.file_exists(
                location), "prefab.file_read: file does not exists {0}".format(location)
        elif not self.file_exists(location):
            return default
        frame = self.file_base64(location)
        return base64.decodebytes(frame.encode(errors='replace')).decode()

    def file_exists(self, location):
        """Tests if there is a file at the given location."""
        location = j.core.tools.text_replace(location)
        if j.sal.fs.exists(location) and j.sal.fs.isFile(location):
            return True
        return False

    def exists(self, location, replace=True):
        """
        check if dir or file or exists
        """
        if replace:
            location = j.core.tools.text_replace(location)
        return j.sal.fs.exists(location)

    def file_is_file(self, location):
        location = j.core.tools.text_replace(location)
        return j.sal.fs.isFile(location)

    def file_is_dir(self, location):
        location = j.core.tools.text_replace(location)
        return j.sal.fs.isDir(location)

    def file_is_link(self, location):
        location = j.core.tools.text_replace(location)
        return j.sal.fs.isLink(location)

    def file_attribs(self, location, mode=None, owner=None, group=None):
        """
        Updates the mode/owner/group for the remote file at the given
        location.

        :param mode: mode of file, sent as Octal, defaults to None
        :type mode: Octal, optional
        :param owner: owner of file, defaults to None
        :type owner: string, optional
        :param group: owning group, defaults to None
        :type group: string, optional
        """
        location = j.core.tools.text_replace(location)
        if mode:
            j.sal.fs.chmod(path, mode)
        if owner or group:
            j.sal.fs.chown(path, owner, group)

    def file_attribs_get(self, location):
        """Return mode, owner, and group for remote path.
        Return mode, owner, and group if remote path exists, 'None'
        otherwise.
        """
        location = j.core.tools.text_replace(location)
        location = location.replace("//", "/")
        if self.file_exists(location):
            if self.isMac:
                fs_check = self.run('stat -f %s %s' %
                                    ('"%a %u %g"', location), showout=False)[1]
            else:
                fs_check = self.run('stat %s %s' % (
                    location, '--format="%a %U %G"'), showout=False)[1]
            (mode, owner, group) = fs_check.split(' ')
            return {'mode': mode, 'owner': owner, 'group': group}
        else:
            return None

    def file_size(self, path):
        """
        return in kb
        """
        path = j.core.tools.text_replace(path)
        return j.sal.fs.fileSize(path)
        # print("du -Lck %s" % path)
        # rc, out, err = self.run("du -Lck %s" % path, showout=False)
        # if rc != 0:
        #     raise j.exceptions.RuntimeError("Failed to define size of path '%s' \nerror: %s" % (path, err))
        # res = out.split("\n")[-1].split("\t")[0].split(" ")[0]
        # print(out)
        # # j.shell()
        # return int(res)

    @property
    def hostname(self):
        j.sal.nettools.getHostname()

    @hostname.setter
    def hostname(self, val):
        if val == self.hostname:
            return
        val = val.strip()
        if self.isMac:
            hostfile = "/private/etc/hostname"
            self.file_write(hostfile, val)
        else:
            hostfile = "/etc/hostname"
            self.file_write(hostfile, val)
        self.run("hostname %s" % val)
        self._hostname = val
        self.ns.hostfile_set(val, '127.0.0.1')

    @property
    def ns(self):
        # TODO:
        return self.prefab.system.ns

    def setIDs(self, name, grid, domain="aydo.com"):
        self.fqn = "%s.%s.%s" % (name, grid, domain)
        self.hostname = name

    @property
    def hostfile(self):
        def get():
            if self.isMac:
                hostfile = "/private/etc/hosts"
            else:
                hostfile = "/etc/hosts"
            return self.file_read(hostfile)
        return self._cache.get("hostfile", get)

    @hostfile.setter
    def hostfile(self, val):
        if self.isMac:
            hostfile = "/private/etc/hosts"
            self.file_write(hostfile)
        else:
            hostfile = "/etc/hosts"
            self.file_write(hostfile, val)
        self._cache.reset()

    def file_write(self, location, content, mode=None, owner=None, group=None, check=False,
                   strip=True, showout=True, append=False, sudo=False):
        """
        :param location: location to write to
        :type location: string
        :param content: content will be written in file
        :type content: string
        :param mode: mode of file, sent as Octal, defaults to None
        :type mode: Octal, optional
        :param owner: owner of file, defaults to None
        :type owner: string, optional
        :param group: owning group, defaults to None
        :type group: string, optional
        :param append: append to file if exists, defaults to False
        :type append: bool, optional
        :param sudo: defaults to False
        :type sudo: bool, optional
        """
        path = j.core.tools.text_replace(location)
        if strip:
            content = j.core.text.strip(content)
        j.sal.fs.writeFile(path, content, append=append)
        self.file_attribs(path, mode, owner, group)

    def file_unlink(self, filename):
        """Remove the file path (only for files, not for symlinks)

        :param filename: file path to be removed
        :type filename: str
        """
        filename = j.core.tools.text_replace(filename)
        if self.file_exists(filename):
            j.sal.fs.unlinkFile(filename)

    def file_ensure(self, location, mode=None, owner=None, group=None):
        """
        Updates the mode/owner/group for the remote file at the given
        location.

        :param location: path to file
        :type location: string
        :param mode: mode of file, sent as Octal, defaults to None
        :type mode: Octal, optional
        :param owner: owner of file, defaults to None
        :type owner: string, optional
        :param group: owning group, defaults to None
        :type group: string, optional
        """
        location = j.core.tools.text_replace(location)
        if self.file_exists(location):
            self.file_attribs(location, mode=mode, owner=owner, group=group)
        else:
            self.file_write(location, "", mode=mode, owner=owner, group=group)

    def file_remove_prefix(self, location, prefix, strip=True):
        # look for each line which starts with prefix & remove
        location = j.core.tools.text_replace(location)
        content = self.file_read(location)
        out = ""
        for l in content.split("\n"):
            if strip:
                l2 = l.strip()
            else:
                l2 = l
            if l2.startswith(prefix):
                continue
            out += "%s\n" % l
        self.file_write(location, out)

    def file_link(self, source, destination, symbolic=True, mode=None, owner=None, group=None):
        """Creates a (symbolic) link between source and destination on the remote host,
        optionally setting its mode / owner / group."""
        source = j.core.tools.text_replace(source)
        destination = j.core.tools.text_replace(destination)
        if self.file_exists(destination) and (not self.file_is_link(destination)):
            raise Exception(
                "Destination already exists and is not a link: %s" % (destination))
        self.file_attribs(destination, mode, owner, group)

    def replace(self, text, args={}):
        text = j.core.tools.text_replace(text, args=args)
        if "$" in text:
            raise RuntimeError("found $ in the text to replace, should use {}")
        return text

    def file_copy(self, source, dest, recursive=False, overwrite=True):
        source = j.core.tools.text_replace(source)
        dest = j.core.tools.text_replace(dest)
        j.sal.fs.copyFile(source, dest, createDirIfNeeded=True, overwriteFile=overwrite)

    def file_move(self, source, dest, recursive=False):
        source = j.core.tools.text_replace(source)
        dest = j.core.tools.text_replace(dest)
        j.sal.fs.moveFile(source, dest)

    def file_base64(self, location):
        """Returns the base64 - encoded content of the file at the given location."""
        content = self.file_read(location)
        return j.data.serializers.base64.dumps(content)

    def file_sha256(self, location):
        """Returns the SHA - 256 sum (as a hex string) for the remote file at the given location."""
        location = j.core.tools.text_replace(location)
        return j.data.hash.sha512(location)

    def file_md5(self, location):
        """Returns the MD5 sum (as a hex string) for the remote file at the given location."""
        location = j.core.tools.text_replace(location)
        return j.data.hash.md5(location)

    def package_install(self, name):
        if "," in name:
            for item in name.split(","):
                self.package_install(item.strip())

        # TODO do same for list
        # check if ubuntu or osx, use right package manager to install
        if self.isUbuntu or self.isLinux:
            j.sal.ubuntu.apt_install(name)

    # =============================================================================
    #
    # Network OPERATIONS
    #
    # =============================================================================

    def getNetworkInfoGenrator(self):
        from Jumpscale.tools.nettools.NetTools import parseBlock, IPBLOCKS, IPMAC, IPIP, IPNAME
        exitcode, output, err = self.run("ip a", showout=False)
        for m in IPBLOCKS.finditer(output):
            block = m.group('block')
            yield parseBlock(block)

    @property
    def networking_info(self):
        from Jumpscale.tools.nettools.NetTools import getNetworkInfo
        if not self._networking_info:
            all_info = list()
            for device in getNetworkInfo():
                all_info.append(device)
        return all_info

    # =============================================================================
    #
    # DIRECTORY OPERATIONS
    #
    # =============================================================================

    def joinpaths(self, *args):
        return j.sal.fs.joinPaths(*args)

    def dir_attribs(self, location, mode=None, owner=None, group=None, recursive=False, showout=False):
        """Updates the mode / owner / group for the given remote directory."""
        location = j.core.tools.text_replace(location)
        if showout:
            # self._logger.info("set dir attributes:%s"%location)
            self._logger.debug('set dir attributes:%s"%location')
        recursive = recursive and "-R " or ""
        if mode:
            self.run('chmod %s %s %s' %
                     (recursive, mode, location), showout=False)
        if owner:
            self.run('chown %s %s %s' %
                     (recursive, owner, location), showout=False)
        if group:
            self.run('chgrp %s %s %s' %
                     (recursive, group, location), showout=False)

    def dir_exists(self, location):
        """
        Tells if there is a remote directory at the given location.

        :param location: location of dir to check
        :type location: string
        """
        location = j.core.tools.text_replace(location)
        return j.sal.fs.exists(location)

    def dir_remove(self, location, recursive=True):
        """ Removes a directory """
        location = j.core.tools.text_replace(location)
        j.sal.fs.remove(location)

    def dir_ensure(self, location, recursive=True, mode=None, owner=None, group=None):
        """Ensures that there is a remote directory at the given location,
        optionally updating its mode / owner / group.

        If we are not updating the owner / group then this can be done as a single
        ssh call, so use that method, otherwise set owner / group after creation."""
        location = j.core.tools.text_replace(location)
        j.sal.fs.createDir(location)
        self.file_attribs(location, mode, owner, group)

    def find(self, path, recursive=True, pattern="", findstatement="", type="", contentsearch="",
             executable=False, extendinfo=False):
        """

        @param findstatement can be used if you want to use your own find arguments
        for help on find see http://www.gnu.org/software/findutils/manual/html_mono/find.html

        @param pattern e.g. * / config / j*
            *   Matches any zero or more characters.
            ?   Matches any one character.
            [string] Matches exactly one character that is a member of the string string.

        @param type
            b    block(buffered) special
            c    character(unbuffered) special
            d    directory
            p    named pipe(FIFO)
            f    regular file
            l    symbolic link


        @param contentsearch
            looks for this content inside the files

        @param executable
            looks for executable files only

        @param extendinfo: this will return [[$path, $sizeinkb, $epochmod]]
        """
        path = j.core.tools.text_replace(path)
        cmd = "cd %s;find ." % path
        if recursive is False:
            cmd += " -maxdepth 1"
        # if contentsearch=="" and extendinfo==False:
        #     cmd+=" -print"
        if pattern != "":
            cmd += " -path '%s'" % pattern
        if contentsearch != "":
            type = "f"

        if type != "":
            cmd += " -type %s" % type

        if executable:
            cmd += " -executable"

        if extendinfo:
            cmd += " -printf '%p||%k||%T@\n'"

        if contentsearch != "":
            cmd += " -print0 | xargs -r -0 grep -l '%s'" % contentsearch

        out = self.run(cmd, showout=False)[1]

        # self._logger.info(cmd)
        self._logger.debug(cmd)

        paths = []
        for item in out.split("\n"):
            if item.startswith("./"):
                item = item[2:]
            if item.strip() == "":
                continue
            item = item.strip()
            if item.startswith("+ find"):
                continue
            paths.append("%s/%s" % (path, item))

        # print cmd

        paths2 = []
        if extendinfo:
            for item in paths:
                if item.find("||") != -1:
                    path, size, mod = item.split("||")
                    if path.strip() == "":
                        continue
                    paths2.append([path, int(size), int(float(mod))])
        else:
            paths2 = [item for item in paths if item.strip() != ""]
            paths2 = [item for item in paths2 if os.path.basename(item) != "."]

        return paths2

    # -----------------------------------------------------------------------------
    # CORE
    # -----------------------------------------------------------------------------

    def run(self, cmd, die=True, debug=None,  showout=True, profile=True, replace=True,
            shell=False, env=None, timeout=600, args={}):
        """
        @param profile, execute the bash profile first
        """
        self._logger.info(cmd)
        if cmd.strip() == "":
            raise RuntimeError("cmd cannot be empty")
        if not env:
            env = {}
        else:
            env = args.update(env)

        rc, out, err = j.sal.process.execute(cmd, cwd=None, timeout=timeout, die=True,
                                             env=env, interactive=False, replace=replace)
        return rc, out, err

    def cd(self, path):
        """cd to the given path"""
        path = j.core.tools.text_replace(path)
        j.sal.fs.changeDir(path)
        self._cd = path

    def pwd(self):
        return self._cd

    def execute_jumpscript(self, script, die=True, profile=True, tmux=False, replace=True, showout=True):
        """
        execute a jumpscript(script as content) in a remote tmux command, the stdout will be returned
        """
        script = j.core.tools.text_replace(script)
        script = j.core.text.strip(script)

        if script.find("from Jumpscale import j") == -1:
            script = "from Jumpscale import j\n\n%s" % script

        # TODO:
        return self.execute_script(script, die=die, profile=profile, interpreter="jspython", tmux=tmux,
                                   replace=replace, showout=showout)

    # =============================================================================
    #
    # SHELL COMMANDS
    #
    # =============================================================================

    def command_check(self, command):
        """Tests if the given command is available on the system."""
        command = j.core.tools.text_replace(command)
        rc, out, err = self.run("which '%s'" % command,
                                die=False, showout=False, profile=True)
        return rc == 0

    def command_location(self, command):
        """
        return location of cmd
        """
        command = j.core.tools.text_replace(command)
        rc, out, err = self.run("which '%s'" % command,
                                die=False, showout=False, profile=True)
        if rc>0:
            raise RuntimeError("command '%s' does not exist, cannot find" % command)
        return out.strip()

    def command_ensure(self, command, package=None):
        """Ensures that the given command is present, if not installs the
        package with the given name, which is the same as the command by
        default."""
        command = j.core.tools.text_replace(command)
        if package is None:
            package = command
        if not self.command_check(command):
            self.prefab.system.package.install(package)
        assert self.command_check(command), \
            "Command was not installed, check for errors: %s" % (command)

    @property
    def isUbuntu(self):
        return str(j.core.platformtype.getParents(j.core.platformtype.myplatform)).find("ubuntu")!=-1

    @property
    def isLinux(self):
        return str(j.core.platformtype.getParents(j.core.platformtype.myplatform)).find("linux")!=-1

    @property
    def isAlpine(self):
        return str(j.core.platformtype.getParents(j.core.platformtype.myplatform)).find("alpine")!=-1

    @property
    def isArch(self):
        return False

    @property
    def isMac(self):
        return str(j.core.platformtype.getParents(j.core.platformtype.myplatform)).find("darwin")!=-1

    @property
    def isCygwin(self):
        return str(j.core.platformtype.getParents(j.core.platformtype.myplatform)).find("cygwin")!=-1
