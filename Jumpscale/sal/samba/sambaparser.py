import configparser
import re
from Jumpscale import j

JSBASE = j.application.JSBaseClass
DEFAULTSECT = "DEFAULT"

"""
Override from https://github.com/enthought/Python-2.7.3/blob/master/Lib/ConfigParser.py
"""


class SambaConfigParser(configparser.ConfigParser, JSBASE):
    OPTCRE_SMB = re.compile(
        r'(?P<option>[^=\s][^=]*)'          # very permissive!
        r'\s*(?P<vi>[=])\s*'                 # any number of space/tab,
        # followed by separator
        # (either =), followed
        # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
    )

    def __init__(self):
        JSBASE.__init__(self)
        configparser.ConfigParser.__init__(self)

    def _read(self, fp, fpname):
        # override optcre to allow colon on key
        self._optcre = self.OPTCRE_SMB

        """Parse a sectioned setup file.
        The sections in setup file contains a title line at the top,
        indicated by a name in square brackets (`[]'), plus key/value
        options lines, indicated by `name: value' format lines.
        Continuations are represented by an embedded newline then
        leading whitespace.  Blank lines, lines beginning with a '#',
        and just about everything else are ignored.
        """
        cursect = None                        # None, or a dictionary
        optname = None
        lineno = 0
        e = None                              # None, or an exception
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                # no leading whitespace
                continue
            # continuation line?
            if line[0].isspace() and cursect is not None and optname:
                value = line.strip()
                if value:
                    cursect[optname].append(value)
            # a section header or option header?
            else:
                # is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if sectname in self._sections:
                        cursect = self._sections[sectname]
                    elif sectname == DEFAULTSECT:
                        cursect = self._defaults
                    else:
                        cursect = self._dict()
                        cursect['__name__'] = sectname
                        self._sections[sectname] = cursect
                    # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self._optcre.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        optname = self.optionxform(optname.rstrip())
                        # This check is fine because the OPTCRE cannot
                        # match if it would set optval to None
                        if optval is not None:
                            if vi in ('=') and ';' in optval:
                                # ';' is a comment delimiter only if it follows
                                # a spacing character
                                pos = optval.find(';')
                                if pos != -1 and optval[pos - 1].isspace():
                                    optval = optval[:pos]
                            optval = optval.strip()
                            # allow empty values
                            if optval == '""':
                                optval = ''
                            cursect[optname] = [optval]
                        else:
                            # valueless option handling
                            cursect[optname] = optval
                    else:
                        # a non-fatal parsing error occurred.  set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, repr(line))
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

        # join the multi-line values collected while reading
        all_sections = [self._defaults]
        all_sections.extend(list(self._sections.values()))
        for options in all_sections:
            for name, val in list(options.items()):
                if isinstance(val, list):
                    options[name] = '\n'.join(val)

    def write(self, fp):
        # write with tab for options
        """Write an .ini-format representation of the configuration state."""
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in list(self._defaults.items()):
                fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")

        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in list(self._sections[section].items()):
                if key == "__name__":
                    continue
                if (value is not None) or (self._optcre == self.OPTCRE):
                    key = " = ".join((key, str(value).replace('\n', '\n\t')))
                fp.write("\t%s\n" % (key))
            fp.write("\n")
