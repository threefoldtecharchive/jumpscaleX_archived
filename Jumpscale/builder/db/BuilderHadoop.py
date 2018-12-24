from Jumpscale import j



# TODO: *4 unfinished but ok for now


class BuilderHadoop(j.builder.system._BaseClass):

    def _install(self):

        if j.builder.tools.isUbuntu:
            C = """\
            apt-get install -y apt-get install openjdk-7-jre
            cd {DIR_TEMP}
            wget -c http://www-us.apache.org/dist/hadoop/common/hadoop-2.7.2/hadoop-2.7.2.tar.gz
            tar -xf hadoop-2.7.2.tar.gz -C /opt/
            """
            C = j.builder.tools.replace(C)
            C = j.core.tools.text_replace(C)
            j.sal.process.execute(C, profile=True)
            j.builder.sandbox.addPath("/opt/hadoop-2.7.2/bin")
            j.builder.sandbox.addPath("/opt/hadoop-2.7.2/sbin")
            j.builder.sandbox.envSet("JAVA_HOME", "/usr/lib/jvm/java-7-openjdk-amd64")
            j.builder.sandbox.envSet("HADOOP_PREFIX", "/opt/hadoop-2.7.2/")
        else:
            raise NotImplementedError("unsupported platform")

    def install(self):
        self._install()
