from Jumpscale import j
import re

percentrec = re.compile("^\s+\((?P<per>\d+\.\d+)/100%\).*$")
inforec = re.compile("^(?P<key>\w+(\s+\w+)?):\s+(?P<value>.*)$", re.MULTILINE)
sizerec = re.compile("^(?P<size>[\d\.]+)(?P<unit>[A-Z])")
virtualsizerec = re.compile("\((?P<size>[\d\.]+)\sbytes\)")

JSBASE = j.application.JSBaseClass


class QemuImg(j.application.JSBaseClass):

    def __init__(self):
        self.__jslocation__ = "j.sal.qemu_img"
        JSBASE.__init__(self)

    def create(self, fileName, diskImageFormat, size, baseImage=None, encryptTargetImage=False,
               useCompatibilityLevel6=False, isTargetImageTypeSCSI=False):
        """
        Create a new disk image <fileName> of size <size> and format <diskImageFormat>.
        If base_image is specified, then the image will record only the differences from base_image. No size needs to be specified in this case. base_image will never be modified unless you use the "commit" monitor command.
        @param fileName: a disk image filename
        @param diskImageFormat: disk image format
        @param size: the disk image size in kilobytes. Optional suffixes 'M' (megabyte) and 'G' (gigabyte) are supported
        @param baseImage: the read-only disk image which is used as base for a copy on write image; the copy on write image only stores the modified data
        @param encryptTargetImage: indicates that the target image must be encrypted (qcow format only)
        @param useCompatibilityLevel6: indicates that the target image must use compatibility level 6 (vmdk format only)
        @param isTargetImageTypeSCSI: indicates that the target image must be of type SCSI (vmdk format only)
        """
        command = '%s create' % self._getBinary()

        if encryptTargetImage:
            if not diskImageFormat.upper() == 'QCOW':
                raise ValueError('encryptTargetImage property is only supported for qcow diskImageFormat')

            command = '%s -e' % command

        if useCompatibilityLevel6:
            if not diskImageFormat.upper() == 'VMDK':
                raise ValueError('useCompatibilityLevel6 property is only supported for vmdk diskImageFormat')
            command = '%s -6' % command

        if isTargetImageTypeSCSI:
            if not diskImageFormat.upper() == 'VMDK':
                raise ValueError('isTargetImageTypeSCSI property is only supported for vmdk diskImageFormat')

            command = '%s -s' % command

        if baseImage:
            command = '%s -b %s' % (command, baseImage)

        command = '%(command)s -f %(diskImageFormat)s %(fileName)s' % {
            'command': command, 'diskImageFormat': diskImageFormat, 'fileName': fileName}

        if size is not None:
            command = '%(command)s %(size)sK' % {'command': command, 'size': size}

        if size is None and not baseImage:
            raise ValueError('Size can only be None if baseImage is specified')

        exitCode, output = self._local.execute(command, die=False)

        if not exitCode == 0:
            raise j.exceptions.RuntimeError('Command %s exited with code %s, output %s' % (command, exitCode, output))

    def commit(self, fileName, diskImageFormat):
        """
        Commit the changes recorded in <fileName> in its base image.
        @param fileName: a disk image filename
        @param diskImageFormat: disk image format
        """
        if not j.tools.path.get(fileName).exists():
            raise IOError('Disk Image %s does not exist' % fileName)

        command = '%s commit -f %s %s' % (self._getBinary(), diskImageFormat, fileName)
        exitCode, output = self._local.execute(command, die=False)

        if not exitCode == 0:
            raise j.exceptions.RuntimeError('Command %s exited with code %s, output %s' % (command, exitCode, output))

    def convert(self, fileName, diskImageFormat, outputFileName, outputFormat, compressTargetImage=False,
                encryptTargetImage=False, useCompatibilityLevel6=False, isTargetImageTypeSCSI=False, logger=None):
        """
        Convert the disk image <fileName> to disk image <outputFileName> using format <outputFormat>.
        It can be optionally encrypted ("-e" option) or compressed ("-c" option).
        Only the format "qcow" supports encryption or compression. The compression is read-only.
        It means that if a compressed sector is rewritten, then it is rewritten as uncompressed data.

        @param fileName: a disk image filename
        @param diskImageFormat: disk image format
        @param outputFileName: is the destination disk image filename
        @param outputFormat: is the destination format
        @param compressTargetImage: indicates that target image must be compressed (qcow format only)
        @param encryptTargetImage: indicates that the target image must be encrypted (qcow format only)
        @param useCompatibilityLevel6: indicates that the target image must use compatibility level 6 (vmdk format only)
        @param isTargetImageTypeSCSI: indicates that the target image must be of type SCSI (vmdk format only)
        @param logger: Callback method to report progress
        @type logger: function
        """
        if not j.tools.path.get(fileName).exists():
            raise IOError('Disk Image %s does not exist' % fileName)

        command = self._getBinary()
        args = ['convert']

        if compressTargetImage:
            if not diskImageFormat.upper() == 'QCOW':
                raise ValueError('compressTargetImage property is only supported for qcow diskImageFormat')
            args.append('-c')

        if encryptTargetImage:
            if not diskImageFormat.upper() == 'QCOW':
                raise ValueError('encryptTargetImage property is only supported for qcow diskImageFormat')
            args.append('-e')

        if useCompatibilityLevel6:
            if not diskImageFormat.upper() == 'VMDK':
                raise ValueError('useCompatibilityLevel6 property is only supported for vmdk diskImageFormat')
            args.append('-6')

        if isTargetImageTypeSCSI:
            if not diskImageFormat.upper() == 'VMDK':
                raise ValueError('isTargetImageTypeSCSI property is only supported for vmdk diskImageFormat')
            args.append('-s')

        args.extend(['-f', str(diskImageFormat)])
        args.extend(['-O', str(outputFormat)])
        if logger:
            args.append('-p')
        args.append(fileName)
        args.append(outputFileName)

        if not logger:
            command += ' ' + ' '.join(args)
            exitCode, output = self._local.execute(command, die=False)
        else:
            rc, prc = self._local.execute(command, args, async=True)
            output = ''
            line = ""
            lastper = 0
            while not prc.stdout.closed:
                char = prc.stdout.read(1)
                output += char
                if char == '\r':
                    m = percentrec.match(line)
                    if m:
                        per = int(float(m.group('per')))
                        if per != lastper:
                            logger(per)
                            lastper = per
                    line = ''
                elif char == '\n':
                    break
                line += char
            output += prc.stdout.read()
            prc.communicate()
            exitCode = prc.returncode

        if not exitCode == 0:
            raise j.exceptions.RuntimeError('Command %s exited with code %s, output %s' % (command, exitCode, output))

    def info(self, fileName, diskImageFormat=None, chain=False, unit='K'):
        """
        Give information about the disk image <fileName>. Use it in particular to know the size reserved on
        disk which can be different from the displayed size. If VM snapshots are stored in the disk image,
        they are displayed too.

        @param fileName: a disk image filename
        @param diskImageFormat: disk image format
        @result: dict with info in KB
        """

        if not j.tools.path.get(fileName).exists():
            raise IOError('Disk Image %s does not exist' % fileName)

        command = '%s info' % (self._getBinary())

        if diskImageFormat:
            command = '%s -f %s' % (command, diskImageFormat)
        if chain:
            command += " --backing-chain "

        command = '%s "%s"' % (command, fileName)

        exitCode, output = self._local.execute(command, die=False)

        if not exitCode == 0:
            raise j.exceptions.RuntimeError('Command %s exited with code %s, output %s' % (command, exitCode, output))

        def getresult(output):
            result = dict()
            for match in inforec.finditer(output):
                value = match.group('value')
                key = match.group('key')
                if key == 'virtual size':
                    value = virtualsizerec.search(value).group('size')
                    value = j.data_units.bytes.toSize(int(value), '', unit)
                else:
                    sizematch = sizerec.match(value)
                    if sizematch:
                        value = j.data_units.bytes.toSize(float(sizematch.group('size')), sizematch.group('unit'), unit)
                result[match.group('key')] = value
            return result

        if chain:
            result = list()
            for img in output.split('\n\n'):
                result.append(getresult(img))
            return result
        else:
            return getresult(output)

    def _getBinary(self):
        return 'qemu-img'
