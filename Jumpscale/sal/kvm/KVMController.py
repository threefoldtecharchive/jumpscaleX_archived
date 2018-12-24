from jinja2 import Environment, FileSystemLoader
import libvirt
import atexit
from Jumpscale import j

JSBASE = j.application.JSBaseClass
class KVMController(j.application.JSBaseClass):

    def __init__(self, executor=None, base_path=None):
        JSBASE.__init__(self)
        if executor is None:
            executor = j.tools.executorLocal
        self.executor = executor
        if self.executor.prefab.id == 'localhost':
            host = 'localhost'
        else:
            host = '%s@%s' % (getattr(self.executor, '_login', 'root'), self.executor.prefab.id)
        self._host = host
        self.user = host.split('@')[0] if '@' in host else 'root'
        self.open()
        atexit.register(self.close)
        self.template_path = j.sal.fs.joinPaths(
            j.sal.fs.getParent(__file__), 'templates')
        self.base_path = base_path or "/tmp/base"
        self.executor.prefab.core.dir_ensure(self.base_path)
        self._env = Environment(loader=FileSystemLoader(self.template_path))

    def open(self):
        uri = None
        self.authorized = False
        #TODO: *1 is this right?, should this be local? (despiegk)
        j.tools.prefab.local.system.ssh.keygen(name='libvirt')
        self.pubkey = j.tools.prefab.local.core.file_read('/root/.ssh/libvirt.pub')
        if self._host != 'localhost':
            self.authorized = not self.executor.prefab.system.ssh.authorize(self.user, self.pubkey)
            uri = 'qemu+ssh://%s/system?no_tty=1&keyfile=/root/.ssh/libvirt&no_verify=1' % self._host
        self.connection = libvirt.open(uri)
        self.readonly = libvirt.openReadOnly(uri)

    def close(self):
        def close(con):
            if con:
                try:
                    con.close()
                except BaseException:
                    pass
        close(self.connection)
        close(self.readonly)
        if self.authorized:
            self.executor.prefab.system.ssh.unauthorize(self.user, self.pubkey)

    def get_template(self, template):
        return self._env.get_template(template)

    def list_machines(self):
        machines = list()
        domains = self.connection.listAllDomains()
        for domain in domains:
            machine = j.sal.kvm.Machine.from_xml(self, domain.XMLDesc())
            machines.append(machine)
        return machines
