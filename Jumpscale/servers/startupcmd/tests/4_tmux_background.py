from Jumpscale import j

"""
there are issues when running on console 
no need to run, but we leave it here, its a good reference
"""

START_BASH = """
    set -x

    if [ "$1" == "kill" ] ; then
        js_shell 'j.tools.tmux.kill()' || exit 1
        exit 1
    fi
    
    tmux -f /sandbox/cfg/.tmux.conf has-session
    if [ "$?" -eq 1 ] ; then
        echo "no server running need to start"
        tmux -f /sandbox/cfg/.tmux.conf new -s main -d 'bash --rcfile /sandbox/bin/env_tmux_detach.sh'
    else
        echo "tmux session already exists"
    fi
    
    if [ "$1" != "start" ] ; then
        tmux a
    fi
    
    """


def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="corex")' --debug
    """
    return "OK"

    self.tmuxserver.delete()
    startup_cmd = self.tmuxserver  # grab an instance
    startup_cmd.executor = "foreground"  # because detaches itself automatically
    startup_cmd.interpreter = "direct"
    startup_cmd.cmd_start = j.core.text.strip(START_BASH)
    startup_cmd.timeout = 5

    startup_cmd.monitor.process_strings_regex = "^tmux"

    startup_cmd.start()
    assert startup_cmd.is_running() == True
    assert startup_cmd.pid

    r = startup_cmd.stop()

    assert startup_cmd.is_running() == False

    return "OK"
