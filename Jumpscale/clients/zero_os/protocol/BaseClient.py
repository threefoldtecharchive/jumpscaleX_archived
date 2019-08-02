import json
import shlex
from Jumpscale import j
from . import typchk
from .FilesystemManager import FilesystemManager
from .InfoManager import InfoManager
from .IPManager import IPManager
from .JobManager import JobManager
from .ProcessManager import ProcessManager
from .Response import ResultError

DEFAULT_TIMEOUT = 10  # seconds


class BaseClient:

    _system_chk = typchk.Checker(
        {"name": str, "args": [str], "dir": str, "stdin": str, "env": typchk.Or(typchk.Map(str, str), typchk.IsNone())}
    )

    _bash_chk = typchk.Checker({"stdin": str, "script": str})

    def __init__(self, timeout=None, **kwargs):
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout
        self._info = InfoManager(self)
        self._job = JobManager(self)
        self._process = ProcessManager(self)
        self._filesystem = FilesystemManager(self)
        self._ip = IPManager(self)

    @property
    def info(self):
        """
        info manager
        :return:
        """
        return self._info

    @property
    def job(self):
        """
        job manager
        :return:
        """
        return self._job

    @property
    def process(self):
        """
        process manager
        :return:
        """
        return self._process

    @property
    def filesystem(self):
        """
        filesystem manager
        :return:
        """
        return self._filesystem

    @property
    def ip(self):
        """
        ip manager
        :return:
        """
        return self._ip

    def raw(
        self, command, arguments, queue=None, max_time=None, stream=False, tags=None, id=None, recurring_period=None
    ):
        """
        Implements the low level command call, this needs to build the command structure
        and push it on the correct queue.

        :param command: Command name to execute supported by the node (ex: core.system, info.cpu, etc...)
                        check documentation for list of built in commands
        :param arguments: A dict of required command arguments depends on the command name.
        :param queue: command queue (commands on the same queue are executed sequentially)
        :param max_time: kill job server side if it exceeded this amount of seconds
        :param stream: If True, process stdout and stderr are pushed to a special queue (stream:<id>) so
            client can stream output
        :param tags: job tags
        :param id: job id. Generated if not supplied
        :return: Response object
        """
        raise j.exceptions.NotImplemented()

    def sync(self, command, arguments, tags=None, id=None):
        """
        Same as self.raw except it do a response.get() waiting for the command execution to finish and reads the result
        :param command: Command name to execute supported by the node (ex: core.system, info.cpu, etc...)
                        check documentation for list of built in commands
        :param arguments: A dict of required command arguments depends on the command name.
        :param tags: job tags
        :param id: job id. Generated if not supplied
        :return: Result object
        """
        response = self.raw(command, arguments, tags=tags, id=id)

        result = response.get()
        if result.state != "SUCCESS":
            if not result.code:
                result._code = 500
            raise ResultError(msg="%s" % result.data, code=result.code)

        return result

    def json(self, command, arguments, tags=None, id=None):
        """
        Same as self.sync except it assumes the returned result is json, and loads the payload of the return object
        if the returned (data) is not of level (20) an error is raised.
        :Return: Data
        """
        result = self.sync(command, arguments, tags=tags, id=id)
        if result.level != 20:
            raise j.exceptions.Base("invalid result level, expecting json(20) got (%d)" % result.level)

        return json.loads(result.data)

    def ping(self):
        """
        Ping a node, checking for it's availability. a Ping should never fail unless the node is not reachable
        or not responsive.
        :return:
        """
        return self.json("core.ping", {})

    def system(
        self,
        command,
        dir="",
        stdin="",
        env=None,
        queue=None,
        max_time=None,
        stream=False,
        tags=None,
        id=None,
        recurring_period=None,
    ):
        """
        Execute a command

        :param command:  command to execute (with its arguments) ex: `ls -l /root`
        :param dir: CWD of command
        :param stdin: Stdin data to feed to the command stdin
        :param env: dict with ENV variables that will be exported to the command
        :param id: job id. Auto generated if not defined.
        :return:
        """
        parts = shlex.split(command)
        if len(parts) == 0:
            raise j.exceptions.Value("invalid command")

        args = {"name": parts[0], "args": parts[1:], "dir": dir, "stdin": stdin, "env": env}

        self._system_chk.check(args)
        response = self.raw(
            command="core.system",
            arguments=args,
            queue=queue,
            max_time=max_time,
            stream=stream,
            tags=tags,
            id=id,
            recurring_period=recurring_period,
        )

        return response

    def bash(
        self, script, stdin="", queue=None, max_time=None, stream=False, tags=None, id=None, recurring_period=None
    ):
        """
        Execute a bash script, or run a process inside a bash shell.

        :param script: Script to execute (can be multiline script)
        :param stdin: Stdin data to feed to the script
        :param id: job id. Auto generated if not defined.
        :return:
        """
        args = {"script": script, "stdin": stdin}
        self._bash_chk.check(args)
        response = self.raw(
            command="bash",
            arguments=args,
            queue=queue,
            max_time=max_time,
            stream=stream,
            tags=tags,
            id=id,
            recurring_period=recurring_period,
        )

        return response

    def subscribe(self, job, id=None):
        """
        Subscribes to job logs. It return the subscribe Response object which you will need to call .stream() on
        to read the output stream of this job.

        Calling subscribe multiple times will cause different subscriptions on the same job, each subscription will
        have a copy of this job streams.

        Note: killing the subscription job will not affect this job, it will also not cause unsubscripe from this stream
        the subscriptions will die automatically once this job exits.

        example:
            job = client.system('long running job')
            subscription = client.subscribe(job.id)

            subscription.stream() # this will print directly on stdout/stderr check stream docs for more details.

        hint: u can give an optional id to the subscriber (otherwise a guid will be generate for you). You probably want
        to use this in case your job watcher died, so u can hook on the stream of the current subscriber instead of creating a new one

        example:
            job = client.system('long running job')
            subscription = client.subscribe(job.id, 'my-job-subscriber')

            subscription.stream()

            # process dies for any reason
            # on next start u can simply do

            subscription = client.response_for('my-job-subscriber')
            subscription.stream()


        :param job: the job ID to subscribe to
        :param id: the subscriber ID (optional)
        :return: the subscribe Job object
        """
        return self.raw("core.subscribe", {"id": job}, stream=True, id=id)
