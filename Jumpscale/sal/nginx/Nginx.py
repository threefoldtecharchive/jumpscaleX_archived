from Jumpscale import j

JSBASE = j.application.JSBaseClass


class NginxFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal.nginx"
        JSBASE.__init__(self)

    def get(self, path="/etc/nginx"):
        # TODO: *2 let work on path
        return Nginx()


class Nginx(JSBASE):

    def __init__(self):
        self.configPath = j.tools.path.get('/etc').joinpath('nginx', 'conf.d')
        self._executor = j.tools.executorLocal
        JSBASE.__init__(self)

    def list(self):
        return self.configPath.files()

    def configure(self, fwObject):
        json = j.data.serializers.serializers.getSerializerType('j')
        fwDict = j.data.serializers.json.loads(fwObject)
        wsForwardRules = fwDict.get('wsForwardRules')
        configfile = self.configPath.joinpath('%s.conf' % fwDict['name'])
        config = ''
        for rule in wsForwardRules:
            if len(rule['toUrls']) == 1:
                config += '''server {
    listen 80;
    server_name _;
    location %s {
        proxy_pass       %s;
        proxy_set_header Host      $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}''' % (rule['url'], rule['toUrls'][0])
            else:
                config += '''
upstream %s {
''' % fwDict['name']
                for toUrl in rule['toUrls']:
                    config += '    server %s;\n' % toUrl
                config += '}\n'
                config += '''
server {
    listen 80;
    server_name _;
    location %s {
        proxy_pass  http://%s;
    }
}''' % (rule['url'], fwDict['name'])

        if config:
            configfile.write_text(config)
            self.reload()

    def deleteConfig(self, name):
        configfile = self.configPath.joinpath('%s.conf' % name)
        if configfile.exists():
            configfile.remove_p()
            self.reload()

    def start(self):
        self._executor.execute('service nginx start')

    def stop(self):
        self._executor.execute('service nginx stop')

    def reload(self):
        self._executor.execute('service nginx reload')

    def restart(self):
        self._executor.execute('service nginx restart')
