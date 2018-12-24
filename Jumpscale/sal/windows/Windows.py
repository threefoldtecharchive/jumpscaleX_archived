
import sys
import os
import threading
import time
import os.path
import ctypes
from Jumpscale import j

if j.core.platformtype.myplatform.isWindows:
    # raise j.exceptions.RuntimeError("WindowsSystem module only supported on Windows operating system")
    import win32pdh
    import win32api
    import win32process
    import win32file
    import win32security
    import win32netcon
    import win32net
    import win32service
    import win32serviceutil

    from win32com.client import GetObject
    #import ntsecuritycon as con
    try:
        from io import StringIO
    except ImportError:
        from io import StringIO

    # from win32shell import shell
    from win32com.shell import shellcon
    import winreg as reg
    from core.enumerators.WinRegHiveType import WinRegHiveType
    from core.enumerators.WinRegValueType import WinRegValueType

    from Jumpscale import j
    # from core.inifile.IniFile import IniFile
    import shutil

JSBASE = j.application.JSBaseClass


class WindowsSystem(j.application.JSBaseClass):

    try:
        mythreads = []
        _userEveryone = None

        # Singleton pattern
        __shared_state = {}

        _wmi = GetObject('winmgmts:')
    except:
        pass

    __jslocation__ = "j.sal.windows"

    def __init__(self):
        JSBASE.__init__(self)
        self.__dict__ = self.__shared_state

    def checkFileToIgnore(self, path):
        if j.core.platformtype.myplatform.isWindows:
            ignore = False
            filename = j.sal.fs.getBaseName(path)
            if filename[0:2] == "~$":
                ignore = True
            return ignore
        else:
            return False

    def createStartMenuShortcut(self, description, executable, workingDir, startMenuSubdir="",
                                iconLocation=None, createDesktopShortcut=False, putInStartup=False):
        '''Create a shortcut in the Start menu

        @type description: string
        @param description: The description of the shortcut.
        @type executable: string
        @param executable: The path in which the executable of the application is located.
        @type workingDir: string
        @param workingDir: The working folder of the application
        @type startMenuSubdir:  string
        @param startMenuSubdir: The name of the folder in the Start menu.
        @type iconLocation: string
        @param iconLocation: The folder in which the application icon is located.
        @type createDesktopShortcut: boolean
        @param createDesktopShortcut: Indicates if a shortcut must be put on the desktop.
        @type putInStartup: boolean
        @param putInStartup: Indicates if an application must be started with Windows.
        '''
        import pythoncom
        from win32com.shell import shell
        import os

        # Add shortcut to startmenu
        startmenu = self.getStartMenuProgramsPath()
        if not j.sal.fs.exists("%s\\%s" % (startmenu, startMenuSubdir)):
            j.sal.fs.createDir("%s\\%s" % (startmenu, startMenuSubdir))

        shortcut_startmenu = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
        shortcut_startmenu.SetPath(executable)
        shortcut_startmenu.SetDescription(description)
        if iconLocation is not None:
            shortcut_startmenu.SetIconLocation(iconLocation, 0)
        shortcut_startmenu.SetWorkingDirectory(workingDir)
        shortcut_startmenu.QueryInterface(pythoncom.IID_IPersistFile).Save(
            "%s\\%s\\%s.lnk" % (startmenu, startMenuSubdir, description), 0)

        if putInStartup:
            startupfolder = self.getStartupPath()
            if not j.sal.fs.exists(startupfolder):
                j.sal.fs.createDir(startupfolder)
            shortcut_startup = pythoncom.CoCreateInstance(
                shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
            shortcut_startup.SetPath(executable)
            shortcut_startup.SetDescription(description)
            if iconLocation is not None:
                shortcut_startup.SetIconLocation(iconLocation, 0)
            shortcut_startup.SetWorkingDirectory(workingDir)
            shortcut_startup.QueryInterface(pythoncom.IID_IPersistFile).Save(
                "%s\\%s.lnk" % (startupfolder, description), 0)

        if createDesktopShortcut:
            desktopfolder = self.getDesktopPath()
            shortcut_desktop = pythoncom.CoCreateInstance(
                shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
            shortcut_desktop.SetPath(executable)
            shortcut_desktop.SetDescription(description)
            if iconLocation is not None:
                shortcut_desktop.SetIconLocation(iconLocation, 0)
            shortcut_desktop.SetWorkingDirectory(workingDir)
            shortcut_desktop.QueryInterface(pythoncom.IID_IPersistFile).Save(
                "%s\\%s.lnk" % (desktopfolder, description), 0)

        j.tools.console.echo('Shortcuts created')

    def isNTFSVolume(self, driveletter):
        """Boolean indicating whether a volume is NTFS

        @param driveletter: The letter of the drive to check
        @type driveletter: string
        """

        # Strip away : / \
        while driveletter.endswith(":") or driveletter.endswith("\\") or driveletter.endswith("/"):
            driveletter = driveletter[:-1]
        if not len(driveletter) == 1:
            raise ValueError(
                "Wrong parameter for WindowsSystem.isNTFSVolume: [%s] is not a valid drive letter." % driveletter)
        fTest = '%s:\\' % driveletter
        volumeInformation = win32api.GetVolumeInformation(fTest)
        fileSystem = volumeInformation[4]
        result = fileSystem == 'NTFS'
        return result

    def grantEveryoneFilePermission(self, dirpath, filepath=""):
        """Grant full control to the group I{Everyone} in this folder and all sub-folders

        This function grants full control to the Windows group I{Everyone} for files in the
        C{dirpath} its sub-folders.
        If a C{filepath} is specified, only the permissions of a specific file are updated.

        @type dirpath: string
        @param dirpath: The full path of the folder for which these permissions are set
        @type filepath: string
        @param filepath: The full path to a specific file.
        """

        # Execute command only on NTFS filesystem. Otherwise pass silently
        fullpath = os.path.abspath(dirpath)
        driveLetter = os.path.splitdrive(fullpath)[0]
        if not self.isNTFSVolume(driveLetter):
            self._logger.warning("Skipped file permissions update - filesystem for [%s] is not NTFS" % dirpath)
            return

        def _grantFile(fileName, securityDescriptor):
            '''Set security on a file'''
            self._logger.info("granting all access to everyone on %s" % fileName)
            win32security.SetFileSecurity(fileName, win32security.DACL_SECURITY_INFORMATION, securityDescriptor)

        def _grantDir(dirpath, securityDescriptor):
            '''Set security on a folder'''
            for dir in j.sal.fs.listDirsInDir(dirpath):
                _grantDir(dir, securityDescriptor)
            for file in j.sal.fs.listFilesInDir(dirpath):
                _grantFile(file, securityDescriptor)
            win32security.SetFileSecurity(dirpath, win32security.DACL_SECURITY_INFORMATION, securityDescriptor)

        # create the security descriptor
        sd = win32security.SECURITY_DESCRIPTOR()
        # fill it:
        everyone = win32security.ConvertStringSidToSid('S-1-1-0')
        acl = win32security.ACL(128)
        acl.AddAccessAllowedAce(win32file.FILE_ALL_ACCESS, everyone)
        sd.SetSecurityDescriptorDacl(1, acl, 0)

        if filepath == "":  # it's a dir
            _grantDir(dirpath, sd)
        else:
            _grantFile(os.path.join(dirpath, filepath), sd)

    _isVistaUACEnabled = None

    def isVistaUACEnabled(self):
        """
        Return boolean indicating whether this is a Windows Vista system with
        User Account Control enabled.

        Warning: If modifies the UAC setting but has not yet rebooted,
        this method will return the wrong result.
        """

        if self._isVistaUACEnabled is not None:
            return self._isVistaUACEnabled

        if self.window_getsVersion() != self.VERSION_VISTA:
            return False
        hkey = reg.HKEY_LOCAL_MACHINE
        key = 'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System'
        value = 'EnableLUA'
        if not self.registryHasValue(hkey, key, value):
            self._isVistaUACEnabled = False
        elif self.getValueFromRegKey(hkey, key, value) == 0:
            self._isVistaUACEnabled = False
        else:
            self._isVistaUACEnabled = True
        return self._isVistaUACEnabled

    _userIsAdministrator = None

    def userIsAdministrator(self):
        '''Verifies if the logged on user has administrative rights'''
        if self._userIsAdministrator is not None:
            return self._userIsAdministrator
        import win32net
        import win32netcon
        username = win32api.GetUserName()
        privileges = win32net.NetUserGetInfo(None, username, 1)
        if privileges['priv'] == win32netcon.USER_PRIV_ADMIN:
            self._userIsAdministrator = True
        else:
            self._userIsAdministrator = False
        return self._userIsAdministrator

    def getAppDataPath(self):
        """ Returns the windows "APPDATA" folder in Unicode format. """
        # We retrieve the APPDATA path using the WinAPI in Unicode format.
        # We could read the environment variable "APPDATA" instead, but this
        # variable is encoded in a DOS-style characterset (called "CodePage")
        # depending on the system locale. It's difficult to handle this encoding
        # correctly in Python.
        # See http://msdn2.microsoft.com/en-us/library/bb762181(VS.85).aspx for information about this function.
        return shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0) + os.sep

    def getUsersHomeDir(self):
        return os.path.expanduser("~")

    def getTmpPath(self):
        """ Returns the windows "TMP" folder."""
        import tempfile
        return tempfile.gettempdir()

    def getLocalAppDataPath(self):
        """ Returns the windows "APPDATA" folder in Unicode format. """
        # We retrieve the APPDATA path using the WinAPI in Unicode format.
        # We could read the environment variable "APPDATA" instead, but this
        # variable is encoded in a DOS-style characterset (called "CodePage")
        # depending on the system locale. It's difficult to handle this encoding
        # correctly in Python.
        # See http://msdn2.microsoft.com/en-us/library/bb762181(VS.85).aspx for information about this function.
        return shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, 0, 0) + os.sep

    def getStartMenuProgramsPath(self):
        """ Returns the windows "START MENU/PROGRAMS" folder in Unicode format. """
        return shell.SHGetFolderPath(
            0,
            shellcon.CSIDL_PROGRAMS,
            0,
            0) + os.sep  # See http://msdn2.microsoft.com/en-us/library/bb762181(VS.85).aspx for information about this function.

    def getStartupPath(self):
        """ Returns the windows "START MENU/STARTUP" folder in Unicode format. """
        return shell.SHGetFolderPath(
            0,
            shellcon.CSIDL_STARTUP,
            0,
            0) + os.sep  # See http://msdn2.microsoft.com/en-us/library/bb762181(VS.85).aspx for information about this function.

    def getDesktopPath(self):
        """ Returns the windows "DESKTOP" folder in Unicode format. """
        return j.sal.fs.joinPaths(self.getUsersHomeDir(), "Desktop")
        # return shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, 0, 0) + os.sep #
        # See http://msdn2.microsoft.com/en-us/library/bb762181(VS.85).aspx for
        # information about this function.

    def _getHiveAndKey(self, fullKey):
        '''Split a windows registry key in two parts: the hive (hkey) and the registry key
        Eg: "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion" will return: (_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\Microsoft\Windows\CurrentVersion")
        '''
        str_hkey, str_key = fullKey.split('\\', 1)
        hiveType = WinRegHiveType.getByName(str_hkey.lower())
        return hiveType.hive, str_key

    def _addValuesRecursively(self, regfile, fullKey):
        '''Recursively add all values and subkeys of a given registry key to an IniFile object
        '''
        regfile.addSection(fullKey)
        values = self.enumRegKeyValues(fullKey)
        for value in values:  # Add all values from current key
            paramName = "\"%s\"" % (value[0])
            paramType = value[2]
            if paramType.exportPrefix:
                paramValue = "%s:%s" % (paramType.exportPrefix, value[1])
            else:
                paramValue = "\"%s\"" % (value[1])
            regfile.addParam(fullKey, paramName, paramValue)
        subkeys = self.enumRegKeySubkeys(fullKey)
        for subkey in subkeys:  # Recursively go through all subkeys
            self._addValuesRecursively(regfile, "%s\\%s" % (fullKey, subkey))
        regfile.write()

    def importRegKeysFromString(self, string):
        """Imports windows registry keys from a string

        @param string: The string that holds the registry information (Should be in format returned by exportRegKeysToString())
        @type string: string
        """
        strBuffer = StringIO()
        strBuffer.write(string)
        strBuffer.seek(0)
        regfile = IniFile(strBuffer)
        sections = regfile.getSections()
        for section in sections:
            params = regfile.getParams(section)
            for param in params:
                value = regfile.getValue(section, param, True)
                param = param[1:-1]  # Remove leading and trailing quote
                valueType = None
                if not value.startswith('"'):
                    prefix, value = value.split(':', 1)
                    valueType = WinRegValueType.findByExportPrefix(prefix)
                    if valueType == WinRegValueType.MULTI_STRING:
                        # convert string representation of an array to a real array
                        value = [eval(item) for item in value[1:-1].split(',')]
                    elif valueType == WinRegValueType.DWORD:
                        value = int(value)
                else:
                    valueType = WinRegValueType.STRING
                    value = value[1:-1]  # Remove leading and trailing quote

                # Write the value to the registry
                self._logger.info("Adding '%s' to registry in key '%s' with value '%s' and type '%s'" %
                                 (param, section, value, valueType))
                self.setValueFromRegKey(section, param, value, valueType)

    def importRegKeysFromFile(self, path):
        """Imports windows registry keys from a file

        @param path: The path of the file to import
        @type path: string
        """

        fileContent = j.sal.fs.readFile(path)
        self.importRegKeysFromString(fileContent)

    def exportRegKeysToString(self, key):
        """Exports Windows registry key to a string

        This function exports a Windows registry key to a string (ini-file format).

        @param key: The registry key to export. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string
        """
        strBuffer = StringIO()
        regfile = IniFile(strBuffer)
        self._addValuesRecursively(regfile, key)
        return regfile.getContent()

    def exportRegKeysToFile(self, key, path):
        """Exports Windows registry key to a file

        This function exports a Windows registry key to an ini-file.

        @param key: The registry key to export. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string

        @param path: The path of the file to export to
        @type path: string
        """
        j.sal.fs.writeFile(path, self.exportRegKeysToString(key))

    def registryHasKey(self, key):
        """Check if the windows registry has the specified key

        @param key: The registry key to check. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string
        """
        try:
            hkey, key = self._getHiveAndKey(key)
            aReg = reg.ConnectRegistry(None, hkey)
            aKey = reg.OpenKey(aReg, key)
            return True
        except EnvironmentError:
            return False

    def registryHasValue(self, key, valueName):
        """Check if a certain key in the windows registry has a specified value

        @param key: The registry key to check. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string
        @param valueName: The name of the value to check for
        @type valueName: string

        """
        try:
            hkey, key = self._getHiveAndKey(key)
            self.getValueFromKey(hkey, key, valueName)
            return True
        except EnvironmentError:
            return False

    def enumRegKeyValues(self, key):
        """List all values of a specified key in the windows registry

        @param key: The registry key to check. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string

        @return: An array of tupples containing the name of each value, the data of the value and it's type
        @rtype: tupple(string, WinRegValueType)
        """
        hkey, key = self._getHiveAndKey(key)
        aReg = reg.ConnectRegistry(None, hkey)
        aKey = reg.OpenKey(aReg, key)
        result = []
        index = 0

        # The function EnumValue() retrieves the name of one subkey each time it is called.
        # It is typically called repeatedly, until an EnvironmentError exception
        # is raised, indicating no more values.
        while True:
            try:
                valueName, valueData, valueType = reg.EnumValue(aKey, index)
                result.append((valueName, valueData, WinRegValueType.findByIntegerValue(valueType)))
                index += 1
            except EnvironmentError:
                return result

    def enumRegKeySubkeys(self, key):
        """List all sub-keys of a specified key in the windows registry

        @param key: The registry key to check. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string
        """
        hkey, key = self._getHiveAndKey(key)
        aReg = reg.ConnectRegistry(None, hkey)
        aKey = reg.OpenKey(aReg, key)
        result = []
        index = 0

        # The function EnumKey() retrieves the name of one subkey each time it is called.
        # It is typically called repeatedly, until an EnvironmentError exception
        # is raised, indicating no more values.
        while True:
            try:
                subkey = reg.EnumKey(aKey, index)
                result.append(subkey)
                index += 1
            except EnvironmentError:
                return result

    def getValueFromRegKey(self, key, valueName):
        """Retrieves a value for a key

        @param key: The registry key that holds the value to get. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string
        @param valueName: The name of the value to retrieve
        @type valueName: string
        @return: A tupple containing the data of the value with the specified name and it's type
        @rtype: tupple(string, WinRegValueType)
        """
        hkey, key = self._getHiveAndKey(key)
        aReg = reg.ConnectRegistry(None, hkey)
        aKey = reg.OpenKey(aReg, key)
        value, int_type = reg.QueryValueEx(aKey, valueName)
        return value, WinRegValueType.findByIntegerValue(int_type)

    def deleteRegKey(self, key):
        """Deletes a key from the Windows Registry

        @param key: The registry key that should be deleted. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string
        """
        hkey, key = self._getHiveAndKey(key)
        aReg = reg.ConnectRegistry(None, hkey)
        reg.DeleteKey(aReg, key)

    def setValueFromRegKey(self, key, valueName, valueData, valueType):
        """Sets a value in a key

        @param key: The registry key that holds the value to set. If the key does not exist, it will be created. The key should include the section. Eg. "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
        @type key: string
        @param valueName: The name of the value to set
        @type valueName: string
        @param valueData: The data to assign to the value
        @type valueData: string
        @param valueType: The type of the value
        @type valueType: WinRegValueType
        """
        hkey, key = self._getHiveAndKey(key)
        aReg = reg.ConnectRegistry(None, hkey)
        aKey = reg.CreateKey(aReg, key)
        reg.SetValueEx(aKey, valueName, 0, valueType.type, valueData)

    def addSystemUser(self, userName, password=None):
        """
        Add a system user
        @param userName: name of the user to add
        @param passwd(optional): password of the user
        raise an exception if user already exists
        """
        self._logger.info('Adding system user %s' % userName)

        if self.isSystemUser(userName):
            raise ValueError('User %s Already Exist' % userName)

        userDict = {}
        userDict['name'] = userName

        if password is not None:
            userDict['password'] = password

        userDict['priv'] = win32netcon.USER_PRIV_USER

        win32net.NetUserAdd(None, 1, userDict)

        if self.isSystemUser(userName):

            self._logger.info('User %s Added successfully' % userN)

    def isSystemUser(self, userName):
        """
        Check if user is valid system User
        @param userName: name of the user
        """
        self._logger.info('Checking if user %s exists' % userName)

        if userName in self.listSystemUsers():
            self._logger.info('User %s exists' % userName)

            return True

        self._logger.info('User %s doesnt exist' % userName)

        return False

    def listSystemUsers(self):
        """
        List system users
        @return: list of system user names
        """
        self._logger.info('Listing System Users')

        users = [entry['name'] for entry in win32net.NetUserEnum(None, 0)[0]]

        return users

    def deleteSystemUser(self, userName):
        """
        Delete a system user
        @param userName: name of the user to delete
        """
        self._logger.info('Deleting User %s' % userName)

        if self.isSystemUser(userName):
            win32net.NetUserDel(None, userName)

            if not self.isSystemUser(userName):
                self._logger.info('User %s deleted successfully' % userName)

                return True

            self._logger.info('Failed to delete user %s' % userName)

        else:
            raise j.exceptions.RuntimeError("User %s is not a system user" % userName)

    def getSystemUserSid(self, userName):
        """
        Get user security identifier
        @param userName: name of the system user
        @return: security identifier of the user
        @rtype: string
        """
        self._logger.info('Getting User %s\'s SID' % userName)

        if self.isSystemUser(userName) or userName == 'everyone':

            info = win32security.LookupAccountName(None, userName)
            pySid = info[0]
            sid = win32security.ConvertSidToStringSid(pySid)

            self._logger.info('User\'s SID is %s' % str(sid))

            return sid

        else:
            raise j.exceptions.RuntimeError('Failed to Get User %s\'s SID' % userName)

    def createService(self, serviceName, displayName, binPath, args=None):
        """
        Create a service
        @param serviceName: name of the service
        @param displayName: display name of the service
        @param binPath: path to the executable file of the service (has to be an existing file)
        @param args(optional): arguments to the executable file
        e.g creating a service for postgresql
        serviceName = 'pgsql-8.3'
        displayName = serviceName
        binDir = j.sal.fs.joinPaths(j.dirs.JSBASEDIR, 'apps','postgresql8', 'bin')
        pgDataDir = j.sal.fs.joinPaths(j.dirs.BASEDIR, 'apps','postgresql8', 'Data')
        j.system.windows.createService(serviceName, displayName , '%s\\pg_ctl.exe','runservice -W -N %s -D %s'%(serviceName, pgDataDir))
        """
        self._logger.info('Creating Service %s' % serviceName)

        if not j.sal.fs.isFile(binPath):
            raise ValueError('binPath %s is not a valid file' % binPath)

        executableString = binPath

        if args is not None:
            executableString = "%s %s" % (executableString, args)

        """
        Open an sc handle to use for creating a service
        @param machineName: The name of the computer, or None
        @param dbName: The name of the service database, or None
        @param desiredAccess: The access desired
        @return: a handle to the service control manager
        """
        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)

        try:
            """
            Create Service
            @param scHandle: handle to service control manager database
            @param name: Name of service
            @param displayName: Display name
            @param desiredAccess: type of access to service
            @param serviceType: type of service
            @param startType: When/how to start service
            @param errorControl: severity if service fails to start
            @param binaryFile: name of binary file
            @param loadOrderGroup: name of load ordering group , or None
            @param bFetchTag: Should the tag be fetched and returned? If TRUE, the result is a tuple of (handle, tag), otherwise just handle.
            @param serviceDeps: sequence of dependency names
            @param acctName: account name of service, or None
            @param password: password for service account , or None
            """
            hs = win32service.CreateService(hscm, serviceName, displayName, win32service.SERVICE_ALL_ACCESS,
                                            win32service.SERVICE_WIN32_OWN_PROCESS, win32service.SERVICE_DEMAND_START,
                                            win32service.SERVICE_ERROR_NORMAL, executableString, None,
                                            0, None, None, None)

            win32service.CloseServiceHandle(hs)

        finally:
            win32service.CloseServiceHandle(hscm)

        if self.isServiceInstalled(serviceName):
            self._logger.info('Service %s Created Successfully' % serviceName)
            return True

    def removeService(self, serviceName):
        """
        Remove Service
        Stops the service then starts to remove it
        @param serviceName: name of the service to remove
        """
        if self.isServiceRunning(serviceName):
            self.stopService(serviceName)

        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)

        serviceHandler = win32service.OpenService(hscm, serviceName, win32service.SERVICE_ALL_ACCESS)

        win32service.DeleteService(serviceHandler)

        win32service.CloseServiceHandle(serviceHandler)

        if not self.isServiceInstalled(serviceName):
            self._logger.info('Service %s removed Successfully' % serviceName)

            return True

    def isServiceRunning(self, serviceName):
        """
        Check if service is running

        @return: True if service is running
        @rtype: boolean
        """
        isRunning = win32serviceutil.QueryServiceStatus(serviceName)[1] == win32service.SERVICE_RUNNING
        self._logger.info('Service %s isRunning = %s' % (serviceName, isRunning))

        return isRunning

    def isServiceInstalled(self, serviceName):
        """
        Check if service is installed
        @rtype: boolean
        """
        self._logger.info('Checking if service %s is installed' % serviceName)

        if serviceName in self.listServices():

            self._logger.info('Service %s is installed' % serviceName)

            return True

        self._logger.info('Service %s is not installed' % serviceName)

        return False

    def listServices(self):
        """
        List all services installed
        @return: list of service names installed
        """
        self._logger.info('Listing services installed')

        services = self._wmi.InstancesOf('Win32_Service')
        serviceNames = [service.Properties_('Name').Value for service in services]

        return serviceNames

    def startService(self, serviceName):
        """
        Start a service.

        @param serviceName: name of the service to start
        @return: True if service started successfully
        @rtype: boolean
        """
        if not self.isServiceRunning(serviceName):
            win32serviceutil.StartService(serviceName)

            time.sleep(1)

            if self.isServiceRunning(serviceName):
                return True

            self._logger.info('Failed to start service %s ' % serviceName)

        else:
            self._logger.info('Service %s is already running' % serviceName)

        return False

    def stopService(self, serviceName):
        """
        Stop a service.

        @param serviceName: name of the service to stop
        @return: True if service stopped successfully
        @rtype: boolean
        Checks if service is running then tries to the service.
        """
        if self.isServiceRunning(serviceName):
            win32serviceutil.StopService(serviceName)

            if not self.isServiceRunning(serviceName):

                return True

            self._logger.info('Failed to stop service %s' % serviceName)

        else:
            self._logger.info('Service %s is not running' % serviceName)

    def listRunningProcessesIds(self):
        """
        List Running Processes Ids
        @return: list of running processes ids
        """
        self._logger.info('Listing Running Processes ids')

        runningProcesses = win32process.EnumProcesses()

        return runningProcesses

    def listRunningProcesses(self):
        """
        List Running Processes names
        @return: list of running processes names,cmdlines & ids
        """
        self._logger.info('Listing Running processes names')

        # j.sal.process.execute()
        processes = self._wmi.InstancesOf('Win32_Process')
        result = [[process.Properties_('Name').Value, process.Properties_(
            "processid").Value, process.Properties_("Commandline").Value] for process in processes]

        return result

    def killProcessesFromCommandLines(self, tokill=[]):
        """
        @param tokill is list of list or list of str (when list of list each item of list will be checked)

        """
        for name, id, cmdline in self.listRunningProcesses():
            if cmdline is None:
                cmdline = ""
            cmdline = cmdline.lower().replace("  ", "").replace("  ", "")
            for item in tokill:
                if j.data.types.string.check(item):
                    itemlist = [item]
                elif j.data.types.list.check(item):
                    itemlist = item
                else:
                    raise j.exceptions.RuntimeError("Can only process string or list")
                found = True
                for item2 in itemlist:
                    if cmdline.find(item2) == -1:
                        found = False
                if found:
                    j.sal.process.kill(id)

    def checkProcessesExist(self, tocheck=[]):
        """
        @param tokill is list of list or list of str (when list of list each item of list will be checked)

        """
        for name, id, cmdline in self.listRunningProcesses():
            if cmdline is None:
                cmdline = ""
            cmdline = cmdline.lower().replace("  ", "").replace("  ", "")
            foundmaster = False
            for item in tocheck:
                if j.data.types.string.check(item):
                    itemlist = [item]
                elif j.data.types.list.check(item):
                    itemlist = item
                else:
                    raise j.exceptions.RuntimeError("Can only process string or list")
                found = True
                for item2 in itemlist:
                    if cmdline.find(item2) == -1:
                        found = False
                if found:
                    foundmaster = True
            if foundmaster is False:
                return False
        return True

    def isPidAlive(self, pid):
        """
        Checking if Pid is Still Alive
        @param pid: process id to check
        @type: int
        @rtype: boolean
        """
        self._logger.info('Checking if pid %s is alive' % pid)

        if pid in self.listRunningProcessesIds():
            self._logger.info('Pid %s is alive' % pid)

            return True

        self._logger.info('Pid %s is not alive' % pid)

        return False

    def getPidOfProcess(self, process):
        """
        Retreive the pid of a process
        @param pid: process name
        @type: string
        @return: the pid (or None if Failed)
        @rtype: int
        """
        self._logger.info('Retreiving the pid of process %s' % process)

        processInfo = self._wmi.ExecQuery('select * from Win32_Process where Name="%s"' % process)

        if len(processInfo) > 0:
            pid = processInfo[0].Properties_('ProcessId').Value
            self._logger.info('Process %s\'s id is %d' % (process, pid))

            return pid

        self._logger.info('Failed to retreive the pid of process %s' % process)

        return None

    def checkProcess(self, process, min=1):
        """
        Check if a certain process is running on the system.
        you can specify minimal running processes needed.

        @param process: String with the name of the process we are trying to check
        @param min: (int) minimal threads that should run.
        @return status: (int) when ok, 1 when not ok.
        """
        processInfo = self._wmi.ExecQuery('select * from Win32_Process where Name="%s"' % process)

        if len(processInfo) >= min:
            self._logger.info('Process %s is running with %d threads' % (process, min))
            return 0

        elif len(processInfo) == 0:
            self._logger.info('Process %s is not running' % (process))

        else:
            self._logger.info('Process %s is running with %d thread(s)' % (process, len(processInfo)))

        return 1

    def checkProcessForPid(self, process, pid):
        """
        Check whether a given pid actually does belong to a given process name.
        @param pid: (int) the pid to check
        @param process: (str) the process that should have the pid
        @return status: (int) 0 when ok, 1 when not ok.
        """
        self._logger.info('Check if process %s\'s Id is %d' % (process, pid))

        processInfo = self._wmi.ExecQuery('select * from Win32_Process where Name="%s"' % process)

        if len(processInfo) > 0:
            processesIds = [process.Properties_('ProcessId').Value for process in processInfo]

            for processId in processesIds:

                if processId == pid:
                    return 0

        self._logger.info('Process %s\'s Id is %d and not %d' % (process, processId, pid))

        return 1

    def getFileACL(self, filePath):
        """
        Get Access Control List of a file/directory
        @return: PyACL object
        """
        info = win32security.DACL_SECURITY_INFORMATION
        sd = win32security.GetFileSecurity(filePath, info)
        acl = sd.GetSecurityDescriptorDacl()

        return acl

    def grantAccessToDirTree(self, dirPath, userName='everyone'):
        """
        Allow Permission to userName on a directory tree
        Adds permission to parentDir the walks through all subdirectories and add permissions

        @param dir: path of the dir
        @param userName: name of the user to add to the acl of the dir tree
        """
        self._logger.info('Granting access to Dir Tree %s' % dirPath)

        if j.sal.fs.isDir(dirPath):
            self.grantAccessToFile(dirPath, userName)

            for subDir in j.sal.fswalker.walkExtended(dirPath, recurse=1):
                self.grantAccessToFile(subDir, userName)
        else:
            self._logger.info('%s is not a valid directory' % dirPath)
            raise IOError('Directory %s does not exist' % dirPath)

    def grantAccessToFile(self, filePath, userName='everyone'):
        """
        Allow Permission to userName on a file/directory
        @param file: path of the file/dir
        @param userName: name of the user to add to the acl of the file/dir
        """
        self._logger.info('Granting access to file %s' % filePath)
        import ntsecuritycon as con
        if j.sal.fs.isFile(filePath) or j.sal.fs.isDir(filePath):

            info = win32security.DACL_SECURITY_INFORMATION
            sd = win32security.GetFileSecurity(filePath, info)
            acl = self.getFileACL(filePath)
            user, domain, acType = win32security.LookupAccountName("", userName)

            acl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE |
                                    con.FILE_DELETE_CHILD | con.DELETE | win32file.FILE_SHARE_DELETE, user)
            sd.SetSecurityDescriptorDacl(1, acl, 0)
            win32security.SetFileSecurity(filePath, win32security.DACL_SECURITY_INFORMATION, sd)

        else:
            self._logger.info('File/Directory %s is not valid' % filePath)

            raise IOError('FilePath %s does not exist' % filePath)

    def pm_removeDirTree(self, dirPath, force=False, errorHandler=None):
        """
        Recusrively removes files and folders from a given path
        @param dirPath: path of the dir
        @param force: boolean parameter indicating that folders containing hidden files will also be deleted
        """
        if(j.sal.fs.exists(dirPath)):
            if j.sal.fs.isDir(dirPath):
                if force:
                    fileMode = win32file.GetFileAttributesW(dirPath)
                    for file in j.sal.fswalk.walk(dirPath, recurse=1):
                        self._logger.info('Changing attributes on %s' % fileMode)
                        win32file.SetFileAttributesW(file, fileMode & ~win32file.FILE_ATTRIBUTE_HIDDEN)
                if errorHandler is not None:
                    shutil.rmtree(dirPath, onerror=errorHandler)
                else:
                    shutil.rmtree(dirPath)
            else:
                raise ValueError("Specified path: %s is not a Directory in System.removeDirTree" % dirPath)

    def checkProgramExists(self, programName):
        """
        this is a not too well implemented check to see if a program is installed, it just checks if it can be executed without an error message
        @return when 0 then ok, when 1 not found, when 2 an error but don't know what
        """
        try:
            returncode, output, _ = j.sal.process.execute(programName)
        except Exception as inst:
            if inst.args[1].lower().find("cannot find the file specified") != -1:
                return 1
            else:
                return 2
        return 0

    def clipboardSet(self, text):
        self.initKernel()
        CF_UNICODETEXT = 13
        GHND = 66
        if text is None:
            return

        if isinstance(text, type('')):
            text = str(text, 'mbcs')
        bufferSize = (len(text) + 1) * 2
        hGlobalMem = ctypes.windll.kernel32.GlobalAlloc(ctypes.c_int(GHND), ctypes.c_int(bufferSize))
        ctypes.windll.kernel32.GlobalLock.restype = ctypes.c_void_p
        lpGlobalMem = ctypes.windll.kernel32.GlobalLock(ctypes.c_int(hGlobalMem))
        ctypes.cdll.msvcrt.memcpy(lpGlobalMem, ctypes.c_wchar_p(text), ctypes.c_int(bufferSize))
        ctypes.windll.kernel32.GlobalUnlock(ctypes.c_int(hGlobalMem))
        if ctypes.windll.user32.OpenClipboard(0):
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.SetClipboardData(ctypes.c_int(CF_UNICODETEXT), ctypes.c_int(hGlobalMem))
            ctypes.windll.user32.CloseClipboard()

    def clipboardGet(self):
        self.initKernel()
        # Get required functions, strcpy..
        strcpy = ctypes.cdll.msvcrt.strcpy
        ocb = ctypes.windll.user32.OpenClipboard  # Basic Clipboard functions
        ecb = ctypes.windll.user32.EmptyClipboard
        gcd = ctypes.windll.user32.GetClipboardData
        scd = ctypes.windll.user32.SetClipboardData
        ccb = ctypes.windll.user32.CloseClipboard
        ga = ctypes.windll.kernel32.GlobalAlloc    # Global Memory allocation
        gl = ctypes.windll.kernel32.GlobalLock     # Global Memory Locking
        gul = ctypes.windll.kernel32.GlobalUnlock
        GMEM_DDESHARE = 0x2000

        ocb(0)  # Open Clip, Default task
        pcontents = gcd(1)  # 1 means CF_TEXT.. too lazy to get the token thingy ...
        data = ctypes.c_char_p(pcontents).value
        # gul(pcontents) ?
        ccb()
        return data

    def addActionToShell(self, name, descr, cmd):
        """
        add action in windows explorer on top of file & dir
        """
        if descr == "":
            descr = name
        import winreg as winreg
        for item in ["*", "Directory"]:
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'%s\shell\%s' % (item, name))
            key2 = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r'%s\shell\%s\Command' % (item, name))
            winreg.SetValueEx(key, "", None, winreg.REG_SZ, "%s " % descr)
            winreg.SetValueEx(key, "Icon", None, winreg.REG_SZ, "")
            winreg.SetValueEx(key, "Position", None, winreg.REG_SZ, "Top")
            winreg.SetValueEx(key, "", None, winreg.REG_SZ, "%s " % descr)
            #winreg.SetValueEx(key2,"",None,winreg.REG_SZ,r'cmd.exe /s /k pushd "%V"')
            winreg.SetValueEx(key2, "", None, winreg.REG_SZ, cmd)
            winreg.CloseKey(key)
