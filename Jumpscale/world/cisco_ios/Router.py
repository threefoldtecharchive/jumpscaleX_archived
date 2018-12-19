'''
Created on Nov 17, 2012

@author: ambarik
'''

import pexpect
import string
import time
import os
from Jumpscale import j
SCRIPT_LOG = 'Script Logs.log'
IOS = 'IOS'
IOS_XR = 'IOS XR'
MORE_OUTPUT_PROMPT = " --More-- "
STRIP_ASCII_CHAR = '\x08'

# TODO: Fix STRIP_ASCII_CHAR

JSBASE = j.application.JSBaseClass


def printable_out(str_in):
    # In case of --More--
    str_in = str_in.replace(STRIP_ASCII_CHAR, '')

    # In general
    str_out = [x for x in str_in if x in string.printable]
    return str_out


class Router(JSBASE):

    def __init__(self, hostname, software=IOS, logfile=None, **kwargs):
        JSBASE.__init__(self)
        self.hostname = hostname
        self.software = software        # IOS or IOS XR
        self.logged_in = False

        self._pexpect_session = None
        self._prompt_current = None
        self._prompt_session_start = None

        self._LOGIN_YES_PROMPTS = hostname + '#'
        self._LOGIN_USERNAME_PROMPTS = 'Username:'
        self._LOGIN_PASSWORD_PROMPTS = 'Password:|password:'

        self.PROMPT_SYNTAX_XR = '\w+/[0-9]/\w+/\w+:'
        if self.software == IOS:
            self.PROMPT_USER_EXEC_MODE = hostname + '>'
            self.PROMPT_PRIVILEGED_EXEC_MODE = hostname + '#'
            self.PROMPT_GLOBAL_CONFIG_MODE = hostname + '\(config\)#'
            self.PROMPT_CONFIG_SUB_MODE = hostname + '\(config-.*\)#'
        elif self.software == IOS_XR:
            prompt_syntax_xr = self.PROMPT_SYNTAX_XR
            self.PROMPT_USER_EXEC_MODE = prompt_syntax_xr + hostname + '>'
            self.PROMPT_PRIVILEGED_EXEC_MODE = (prompt_syntax_xr +
                                                hostname + '#')
            self.PROMPT_GLOBAL_CONFIG_MODE = (prompt_syntax_xr +
                                              hostname + '\(config\)#')
            self.PROMPT_CONFIG_SUB_MODE = (prompt_syntax_xr + hostname +
                                           '\(config-.*\)#')

        if logfile is None:
            direc = os.getcwd()
            logfilename = (self.hostname + '-' +
                           time.strftime("%m-%d-%Y_%H-%M-%S") +
                           '.log')
            logfile = os.path.join(direc, logfilename)

        self._log('Console Logs are in {0}'.format(logfile))
        self._console_logfile = logfile
        self._console_log = None

    def login(self, cmd, username=None, password=None, final_prompt=None):
        """
        Tries to Login. Returns the final matched string
        """
        os.environ["TERM"] = "dumb"
        self._log("Giving cmd: '{0}'".format(repr(cmd)))
        self._pexpect_session = pexpect.spawn(cmd, env={"TERM": "dumb"})
        self._pexpect_session.timeout = 60

        self._console_log = open(self._console_logfile, 'w+')
        self._pexpect_session.setecho(False)
        self._pexpect_session.logfile_read = self._console_log

        if final_prompt is None:
            self._prompt_current = self.PROMPT_USER_EXEC_MODE
            self._prompt_session_start = self._prompt_current
        else:
            self._prompt_current = final_prompt
            self._prompt_session_start = final_prompt

        expect_list = [self._LOGIN_YES_PROMPTS,
                       self._LOGIN_USERNAME_PROMPTS,
                       self._LOGIN_PASSWORD_PROMPTS]

        i = self._pexpect_session.expect(expect_list)
        matched = expect_list[i]

        if i == expect_list.index(self._LOGIN_YES_PROMPTS):
            matched = self.exec_cmd("yes", expects=expect_list,
                                    return_matched=True)
            try:
                i = expect_list.index(matched)
            except ValueError:
                msg = ('After giving yes, {0} not in list {1}'
                       ''.format(matched, repr(expect_list)))
                self._log(msg, level='WARNING')

        if i == expect_list.index(self._LOGIN_USERNAME_PROMPTS):
            if username is None:
                self._exit("Username not provided")
            matched = self.exec_cmd(username, expects=expect_list,
                                    return_matched=True)
            try:
                i = expect_list.index(matched)
            except ValueError:
                msg = ('After giving username, {0} not in list {1}'
                       ''.format(matched, repr(expect_list)))
                self._log(msg, level='WARNING')

        if i == expect_list.index(self._LOGIN_PASSWORD_PROMPTS):

            if password is None:
                self._exit("Password not provided")
            matched = self.exec_cmd(
                password, expects=expect_list, return_matched=True)
            try:
                i = expect_list.index(matched)
            except ValueError:
                msg = ('After giving password, {0} not in list {1}'
                       ''.format(matched, repr(expect_list)))
                self._log(msg, level='WARNING')

            if i == expect_list.index(self._LOGIN_USERNAME_PROMPTS):
                msg = ('Prompt: "{0}" returned again... Indicates '
                       'invalid Username/Password'
                       ''.format(self._LOGIN_USERNAME_PROMPTS))
                self._log(msg, level='WARNING')

        self.logged_in = True
        return matched

    def logout(self):
        if self.logged_in is True:
            self._log('Logging out...')
            self._exit()
            self.logged_in = False

    def exec_cmd(self, cmd, **kwargs):
        """ Execute Command

        Arguments:
        cmd                  -- String. Command to be executed
                                (Mandatory)
        expects              -- List. List of possible matches
                                (Default to [])
        return_output        -- Boolean. If True, returns Output
                                (Default to True)
        return_matched        -- Boolean. If True, returns matched expect
                                (Default to False)
        prompt               -- String. Expected Prompt after
                                command execution (Default to None)
        auto_complete        -- Boolean. If True, hits spaces
                                till prompt is seen (in case of huge output)
                                (Default to True)

        Example:
        login("Telnet R1")                       # Go to User Exec Mode
        exec_cmd("show clock")                   # Returns Output
        exec_cmd("enable",
                 expects=["Password:", "R1#"],
                 prompt="R1#")                       # Go to Enable Mode
        exec_cmd("Conf t", prompt="R1\(Config\)#")   # Go to Config Mode

        """

        # Setting Parameters
        expects = kwargs.get('expects', [])
        return_output = kwargs.get('return_output', True)
        return_matched = kwargs.get('return_matched', False)
        auto_complete = kwargs.get('auto_complete', True)
        if return_matched is True and return_output is True:
            return_output = False

        return_output = True

        prompt = kwargs.get('prompt')
        self._log('Giving cmd: {0}'.format(cmd))
        self._pexpect_session.sendline(cmd)

        if prompt is not None:
            self._prompt_current = prompt
        if isinstance(expects, list) is False:
            expects = [expects]

        # Order of this list should be considered while modifying the code
        expects = (expects + [MORE_OUTPUT_PROMPT] +
                   [self._prompt_current] + [pexpect.EOF])
        i = self._pexpect_session.expect(expects)
        output = self._pexpect_session.before
        output = output.replace(cmd, '').strip()
        self._log("Output for previous cmd: '{0}'"
                  "".format(repr(output)))

        matched = expects[i]
        if i == len(expects) - 1:       # If EOF
            msg = ("""Expected Prompt not found
                      Match list: {0}
                      Output After Prompt: '{1}'""".format(expects,
                                                           repr(self._pexpect_session.after)))
            self._exit(msg)

        elif i != len(expects) - 2:       # If not Current Prompt
            msg = ("Warning: Last command matched: '{0}'."
                   " Should have matched prompt: '{1}'"
                   "".format(expects[i], expects[len(expects) - 2]))
            self._log(msg)

            # --More--
            if (i == len(expects) - 3) and auto_complete is True:
                # If --More-- is seen, keep hitting spaces till
                # current prompt is seen
                more_seen = True
                cnt = 1
                while more_seen:
                    self._pexpect_session.send(' ')
                    new_expects = [MORE_OUTPUT_PROMPT,
                                   self._prompt_current, pexpect.EOF]
                    j = self._pexpect_session.expect(new_expects)
                    more_out = str(self._pexpect_session.before)
                    output += more_out

                    matched = new_expects[j]
                    if j == 2:
                        msg = ("""Expected Prompt not found
                                  Match list: {0}
                                  Output After Prompt: '{1}'"""
                               """""".format(new_expects,
                                             repr(self._pexpect_session.after)))
                        self._exit(msg)
                    elif j == 1:
                        self._log('{0} stopped showing. Matched {1} finally'
                                  ''.format(new_expects[0], new_expects[1]))
                        break
                    elif i == 0:
                        self._log('{0} seen {1} times'
                                  ''.format(new_expects[0], cnt))
                        cnt += 1

        if return_output is True:
            return printable_out(output)

        elif return_matched is True:
            return matched

    def _log(self, msg, **kwargs):
        if self._logger is None:
            # print msg
            pass
        else:
            self._logger.log(msg, **kwargs)

    def _clean_logfile(self):
        out = open(self._console_logfile).read()
        out = printable_out(out)
        out = out.replace(MORE_OUTPUT_PROMPT, '')
        with open(self._console_logfile, 'w') as logfile:
            logfile.write(out)

    def _exit(self, msg=''):
        if self._pexpect_session.isalive() is True:
            try:
                self._log('Hitting Ctrl-Z and Enters...')
                self._pexpect_session.sendcontrol('Z')
                self._pexpect_session.sendline('')
                expect_list = [self.PROMPT_USER_EXEC_MODE,
                               self.PROMPT_PRIVILEGED_EXEC_MODE,
                               self._prompt_session_start,
                               self._prompt_current]
                self._pexpect_session.expect(expect_list)
                self._log('exiting...')
                self._pexpect_session.sendline('exit')
                expect_list = ['Connection closed', 'closed',
                               'connection']
                self._pexpect_session.expect(expect_list)
            except Exception as e:
                msg1 = ('Exception caught during closing '
                        'connection: {0}'.format(e))
                self._log(msg1, level='ERROR')
            finally:
                self._pexpect_session.close(True)
                self._pexpect_session.terminate(True)

        # Close the file
        if self._console_log is not None:
            if self._console_log.closed is False:
                self._console_log.close()

        # Reopen the file and clean it up
        self._clean_logfile()

        if msg != '':
            raise Exception(msg)


def main():
    # Testing
    from Localhost import Localhost
    hostname = 'R1'
    R1 = Router(
        hostname, logfile='C:\\Barik\\MyPythonWinProject\\SyslogAutomation\\TEST\\Log.log')
    login_cmd = 'telnet ' + hostname + '.com'
    username = 'abarik'
    password = '123'
    Localhost1 = Localhost()
    #password = Localhost1.get_rsa_token()
    #login_expect = hostname
    # login_expect = hostname + '#'
    login_expect = '{0}#|{0}>'.format(hostname)
    out = R1.login(login_cmd, username, password, login_expect)
    if out != R1._LOGIN_USERNAME_PROMPTS:
        R1.logout()
        time.sleep(60)
        R1 = Router(
            hostname, logfile='C:\\Barik\\MyPythonWinProject\\SyslogAutomation\\TEST\\Log1.log')
        password = Localhost1.get_rsa_token()
        out = R1.login(login_cmd, username, password, login_expect)
        print((repr(R1.exec_cmd('show clock'))))
    R1.logout()


if __name__ == '__main__':
    main()
