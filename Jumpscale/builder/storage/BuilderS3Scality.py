from Jumpscale import j
from time import sleep





class BuilderS3Scality(j.builder.system._BaseClass):
    NAME = 's3scality'

    def install(self, start=False, storageLocation="/data/", metaLocation="/meta/"):
        """
        put backing store on /storage/...
        """
        j.builder.system.package.mdupdate()
        j.builder.system.package.ensure('build-essential')
        j.builder.system.package.ensure('python2.7')
        j.core.tools.dir_ensure(storageLocation)
        j.core.tools.dir_ensure(metaLocation)

        j.core.tools.dir_ensure('/opt/code/github/scality')
        path = j.clients.git.pullGitRepo('https://github.com/scality/S3.git', ssh=False)
        profile = #j.builder.sandbox.profile_default
        profile.path_add('{DIR_BIN}')
        profile.save()
        j.builder.runtimes.nodejs.install()
        j.sal.process.execute('cd {} && npm install --python=python2.7'.format(path), profile=True)
        j.builder.tools.dir_remove('{DIR_BASE}/apps/S3', recursive=True)
        j.core.tools.dir_ensure('{DIR_BASE}/apps/')
        j.sal.process.execute('mv {} {DIR_BASE}/apps/'.format(path))

        cmd = 'S3DATAPATH={data} S3METADATAPATH={meta} npm start'.format(
            data=storageLocation,
            meta=metaLocation,
        )

        content = j.core.tools.file_text_read('{DIR_BASE}/apps/S3/package.json')
        pkg = j.data.serializers.json.loads(content)
        pkg['scripts']['start_location'] = cmd

        content = j.data.serializers.json.dumps(pkg, indent=True)
        j.sal.fs.writeFile('{DIR_BASE}/apps/S3/package.json', content)

        if start:
            self.start()

    def start(self, name=NAME):
        nodePath = '{DIR_BASE}/node/lib/node_modules'
        # Temporary. Should be removed after updating the building process
        j.core.tools.dir_ensure('/data/data')
        j.core.tools.dir_ensure('/data/meta')
        # Temporary. npm install should be added to install() function after updating the building process
        if not j.builder.tools.dir_exists('%s/npm-run-all' % nodePath):
            j.sal.process.execute('npm install npm-run-all')
        nodePath = j.builder.tools.replace('{DIR_BASE}/node/lib/node_modules/s3/node_modules:%s' % nodePath)
        if #j.builder.sandbox.profile_default.env_get('NODE_PATH') != nodePath:
            #j.builder.sandbox.profile_default.env_set("NODE_PATH", nodePath)
            #j.builder.sandbox.profile_default.path_add(j.builder.tools.replace("{DIR_BASE}/node/bin/"))
            #j.builder.sandbox.profile_default.save()
        path = j.sal.fs.joinPaths(j.dirs.JSAPPSDIR, 'S3')
        j.sal.process.execute('cd {} && npm run start_location'.format(path), profile=True)

    def test(self):
        # put/get file over S3 interface using a python S3 lib
        raise NotImplementedError
