import re
import collections
import subprocess

from Jumpscale import j


STATUS_LINE = re.compile("^Status:\s*(.+)")
RULE_LINE = re.compile("^\[\s*(\d+)\] (.+?)\s{2,}(.+?)\s{2,}(.+)$")


ParsedDestination = collections.namedtuple("ParsedDestination", "ip proto port dev")

JSBASE = j.application.JSBaseClass


class UFWError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class UFWRule(j.application.JSBaseClass):
    def __init__(self, action=None, source=None, destination=None, number=None):
        JSBASE.__init__(self)
        self._number = number
        self._source = source
        self._action = action
        self._destination = destination

    @property
    def number(self):
        return self._number

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    @property
    def action(self):
        return self._action

    def __str__(self):
        return "[%2s] %s to %s from %s" % (
            self.number if self.number is not None else "",
            self.action,
            self.destination,
            self.source,
        )

    def __repr__(self):
        return str(self)


class UFWOperation(j.application.JSBaseClass):
    def __init__(self):
        JSBASE.__init__(self)

    def cmd(self):
        raise NotImplemented()


class StatusOp(UFWOperation):
    def __init__(self, status=None):
        self._status = status
        UFWOperation.__init__(self)

    def cmd(self):
        return "--force enable" if self._status else "disable"


class ResetOp(UFWOperation):
    def __init__(self):
        UFWOperation.__init__(self)

    def cmd(self):
        return "--force reset"


class RuleOp(UFWOperation):
    def __init__(self, rule=None, add=True):
        self._add = add
        self._rule = rule
        UFWOperation.__init__(self)

    def _parser(self, src):
        src = src.replace("(v6)", "").replace("(out)", "")
        source = re.search("\d+\.\d+\.\d+.\d+[^\s]*", src)
        ip = None
        pos = 0
        if source:
            ip = source.group()
            pos = source.end()
        else:
            ip = "any"

        port_proto_m = re.search("\\b(\d+)(/([^\s]+))?", src[pos:])
        proto = None
        port = None
        if port_proto_m:
            proto = port_proto_m.group(3)
            port = port_proto_m.group(1)
            pos = port_proto_m.end()

        on_m = re.search("on \w+", src)
        dev = None
        if on_m:
            dev = on_m.group()

        return ParsedDestination(ip=ip, proto=proto, port=port, dev=dev)

    def cmd(self):
        rule = self._rule
        cmd = []
        if not self._add:
            cmd.append("delete")

        cmd.append(rule.action.lower())

        def push(src):
            cmd.append(src.ip)
            if src.proto:
                cmd.append("proto %s" % src.proto)
            if src.port:
                cmd.append("port %s" % src.port)

        src = self._parser(rule.source)
        dst = self._parser(rule.destination)

        if src.dev and dst.dev:
            raise UFWError("Both source and destination has devices")

        if src.dev:
            if "out" not in rule.action.lower():
                raise UFWError("Invalid source for %s" % rule.action)
            cmd.append(src.dev)
        elif dst.dev:
            if "in" not in rule.action.lower():
                raise UFWError("Invalid destination for %s" % rule.action)
            cmd.append(dst.dev)

        cmd.append("from")
        push(src)

        cmd.append("to")
        push(dst)

        return " ".join(cmd)


class UFWManager(j.application.JSBaseClass):
    ACTION_ALLOW_IN = "allow in"
    ACTION_ALLOW_OUT = "allow out"
    ACTION_DENY_IN = "deny in"
    ACTION_DENY_OUT = "deny out"
    ACTION_REJECT_IN = "reject in"
    ACTION_REJECT_OUT = "reject out"

    def __init__(self):
        self.__jslocation__ = "j.sal.ufw"
        self._rules = None
        self._enabled = None
        self._transactions = []
        JSBASE.__init__(self)

    def _bool(self, status):
        return status == "active"

    def _load(self):
        status = subprocess.run(["ufw", "status", "numbered"], stdout=subprocess.PIPE).stdout.decode()
        self._rules = []
        for line in status.splitlines():
            line = line.strip()
            if not line or "(v6)" in line:
                continue

            status = STATUS_LINE.match(line)
            if status is not None:
                self._enabled = self._bool(status.group(1))
                continue

            rule = RULE_LINE.match(line)
            if rule is None:
                continue

            number, destination, action, source = rule.groups()
            self._rules.append(UFWRule(action, source, destination, number))

    @property
    def rules(self):
        """
        List of current rules.
        """
        if self._rules is None:
            self._load()
        return self._rules

    @property
    def enabled(self):
        """
        Get the `current` actual status of ufw. Setting enabled on the
        otherhand will not take effect until you call commit()
        """
        if self._enabled is None:
            self._load()
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        """
        Set the anbled status. Note that this doesn't take action
        until you apply the change by calling commit.
        """
        self._transactions.append(StatusOp(value))

    def addRule(self, action, source="any", destination="any"):
        """
        Add a new UFW rule

        :action: One of the actions defined
            ACTION_ALLOW_IN
            ACTION_ALLOW_OUT
            ACTION_DENY_IN
            ACTION_DENY_OUT
            ACTION_REJECT_IN
            ACTION_REJECT_OUT

        :source: Source to match, default to 'any'. Examples of valid sources
            '192.168.1.0/24 proto tcp'
            '22/tcp'
            'any'
            'any on eth0'

        :destination: Destination to match, default to 'any'.
        """
        self._transactions.append(RuleOp(UFWRule(action, source, destination)))

    def removeRule(self, rule):
        """
        Remove the specified rule

        :rule: rule to remove
        """
        self._transactions.append(RuleOp(rule, add=False))

    def reset(self):
        """
        Remove all rules.
        """

        self._transactions.append(ResetOp())

    def portOpen(self, port):
        """
        Short cut to open port
        """

        self.addRule(UFWManager.ACTION_ALLOW_IN, "any", str(port))

    def portClose(self, port):
        """
        Short cut to closing a port (which is previously open by portOpen)
        """
        port = str(port)
        for rule in self.rules:
            if rule.destination == port:
                self.removeRule(rule)

    def commit(self):
        """
        Apply all bending actions

        :example:
            ufw.enabled = False
            ufw.reset()
            ufw.addRule(ufw.ACTION_ALLOW_IN, 'any', '22/tcp')
            ufw.enabled = True

            ufw.commit()
        """
        try:
            while self._transactions:
                op = self._transactions.pop(0)
                args = ["ufw"]
                args.extend(op.cmd().split(" "))
                subprocess.run(args)
        except Exception as e:
            raise UFWError(e)

        # force reload on next access.
        self._rules = None
        self._status = None
