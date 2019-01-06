from Jumpscale import j
from .Item import Item

JSBASE = j.application.JSBaseClass




class CodeGenerator(j.application.JSBaseClass):
    """
    """

    __jslocation__ = "j.tools.codegenerator"

    def _init(self):
        pass

    def get_structure(self,config):
        """
        example config

        ```
        ZOS
            network (j.tools.network:j.tools.network2)      !jumpscale.tools.network.1
                port                                        !jumpscale.tools.network.port.1
            container                                       !jumpscale.world.4          #fake schema's ofcourse, just to make the point
            webgateway                                      !jumpscale.world.4
                firewall  (j.sal.zos.firewall)              !jumpscale.world.4
                    firewall_rule.rule                      !jumpscale.world.4
                loadbalancer                                !jumpscale.world.4
                    lb_rule                                                             #should be jsbase class only, no data
        WORLD                                               !jumpscale.world.4
            ZOS                                             !jumpscale.tools.network.1


        @url = jumpscale.tools.network.1
        name* = ""
        path = ""
        git_url = ""
        description = ""
        last_process_data = (D)

        @url = jumpscale.tools.network.port.1
        name* = ""
        path = ""
        git_url = ""
        description = ""
        last_process_data = (D)

        @url = jumpscale.world.4
        name* = ""
        path = ""
        git_url = ""
        description = ""
        last_process_data = (D)


        ```

        :param config:
        :return:
        """

        config=j.core.tools.text_strip(config)

        #FIND THE 2 PARTS
        pre=""
        post=
        state="STRUCTURE"

        for line in config.split("\n"):
            if line.strip()=="":
                continue
            if line.strip().startswith("#"):
                continue
            if "#" in line:
                line = line.split("#",1)[0]
            #line is now clean
            if line.startswith("@"):
                state="SCHEMA"
            if state == "STRUCTURE":
                pre+="%s\n"%line
            else:
                post+="%s\n"%line


        #lets parse the structure
        levels=[None,None,None,None,None,None,None,]
        for line in pre.split("\n"):

            level=(len(line)-len(line.lstrip()))/4
            if level not in [0,1,2,3,4,5,6]:
                raise RuntimeError("level should be int between 0 and 6, is now:%s"%level)

            line2=copy.copy(line)
            if "!" in line2:
                if "(" in line2:
                    raise RuntimeError("schema (!) needs to be after location.")
                line2,schemalink=line2.split("!",1)
                j.shell()
            if "(" in line2:
                line2,location=line2.split("(",1)
                location=location.split(")",1)[0]
                location=location.strip()

            name = line2.strip()

            if "(" in name or "!" in name:
                raise RuntimeError("should be no ( or ! in the line at this point.\n%s"%name)


            leves[level] =





    def test(self):
        """
        js_shell  'j.tools.codegenerator.test()'
        :return:
        """

        config = """
        ZOS
            network
                port
            container
            webgateway
                firewall
                    firewall_rule
                loadbalancer
                    lb_rule
        """

        struct = self.get_structure(config)





