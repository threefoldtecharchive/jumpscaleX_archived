from Jumpscale import j


JSBASE = j.application.JSBaseClass

class TODO(j.builder._BaseClass):

    def __init__(self,obj,todo):
        JSBASE.__init__(self)
        self.obj=obj
        self.path=obj.path
        self.todo=todo

    def __repr__(self):
        return "Todo %s:%s:%s:%s   "%(self.obj.type,self.obj.name,self.path,self.todo)

    __str__=__repr__        


class Device(j.builder._BaseClass):
    def __init__(self,tomlpath):
        JSBASE.__init__(self)
        tomlpath=tomlpath.replace("//","/")
        self.path=tomlpath
        self.todo = []
        self.type="device"
        self.status="OK"
        self.name="unknown"

        try:
            data=j.data.serializers.toml.load(tomlpath)
        except Exception as e:
            self.todo.append(TODO(self,"cannot parse toml file\n```\n%s```\n\n"%e))
            self.status="ERROR"
            return

        self.data = data
        self.ipaddr=[]
        try:
            self.ipaddr = j.data.serializers.fixType(data["ssh_ipaddr"],[])
        except:
            self.todo.append(TODO(self,"cannot find ipaddr: ssh_ipaddr in toml"))

        try:
            self.name = j.data.serializers.fixType(data["name"],"")
        except:
            self.todo.append(TODO(self,"cannot find name in toml"))

        try:
            self.status = j.data.serializers.fixType(data["status"],"")
        except:
            self.todo.append(TODO(self,"cannot find status in toml"))

        try:
            self.location = j.data.serializers.fixType(data["location"],"")
        except:
            self.todo.append(TODO(self,"cannot find location in toml"))

        try:
            self.id = j.data.serializers.fixType(data["id"],"")
        except:
            self.todo.append(TODO(self,"cannot find id in toml"))

        #walk over ipaddresses & fix
        if len (self.ipaddr)>1:
            self._logger.debug("ipaddr")
            from IPython import embed;embed(colors='Linux')          

    def ip_exists(self,ipaddr):
        ipaddr=ipaddr.lower()
        for ipaddr0 in self.ipaddr:
            if ipaddr in ipaddr0:
                return True
        return False

    @property
    def is_free(self):
        if self.status.lower()=="free":
            return True
        return False

    @property
    def ssd_size(self):
        gb=float(self.data["ssd"]["nr"])*float(self.data["ssd"]["size"])
        return gb

    def has_ssd(self):
        return self.ssd_size>0

    @property
    def todo_md(self):
        if self.todo==[]:
            return ""
        md="# TODO FOR : device %s\n\n"%(self.name)
        md +="\npath: %s\n\n"%self.path
        for todo in self.todo:
            md+="- %s\n"%(todo.todo)
        md+="\n"

        return md    

    def save(self):
        j.data.serializers.toml.dump(self.path,self.data)
        self.saveToMeConfig()

    @property
    def ipAddrPort(self):
        ipaddr=self.ipaddr[0]
        if ":" in ipaddr:
            ipaddr,port=ipaddr.split(":")
            port=int(port)
            ipaddr=ipaddr.strip()
        else:
            port=22
        return ipaddr,port
            
    @property
    def ipAddr(self):
        self._logger.debug("ipaddr")
        from IPython import embed;embed(colors='Linux')
        return self.ipAddrPort[0]

    @property
    def ipPort(self):
        return self.ipAddrPort[1]


    def saveToMeConfig(self):
        """
        if in container write: /hostcfg/nodes.cfg
        if in host write: ~/jumpscale/cfg/nodes.cfg
        """
        # 
        j.tools.develop.nodes.nodeSet(self.name, self.ipAddr, port=self.ipPort, cat='', description='', selected=None)
        j.tools.develop.nodes.save()

    def __repr__(self):
        ipaddr = ",".join(self.ipaddr)
        return "Device %-30s %-14s %-50s:%s   "%(self.name,self.status,ipaddr,self.path)

    __str__=__repr__             

class Client(j.builder._BaseClass):
    def __init__(self,tomlpath):
        JSBASE.__init__(self)
        tomlpath=tomlpath.replace("//","/")
        self.path=tomlpath
        self.todo = []
        self.type="client"
        self.status="OK"
        self.name="unknown"

        try:
            data=j.data.serializers.toml.load(tomlpath)
        except Exception as e:
            self.todo.append(TODO(self,"cannot parse toml file\n```\n%s```\n\n"%e))
            self.status="ERROR"
            return

        self.config = data

        try:
            self.name = data["name"]
        except:
            self.todo.append(TODO(self,"cannot find name in toml"))

        try:
            self.schema_type = data["schema_type"]
        except:
            self.todo.append(TODO(self,"cannot find schema_type in toml"))

        try:
            self.cpath = data["path"]
        except:
            self.todo.append(TODO(self,"cannot find config: path in toml"))

        try:
            self.description = data["description"]
        except:
            self.todo.append(TODO(self,"cannot find description in toml"))

    @property
    def todo_md(self):
        if self.todo==[]:
            return ""
        md="# TODO FOR : client %s\n\n"%(self.name)
        md +="\npath: %s\n\n"%self.path
        for todo in self.todo:
            md+="- %s\n"%(todo.todo)
        md+="\n"

        return md    

    def __repr__(self):
        return "%-25s:%-20s:%s   "%(self.schema_type,self.name,self.path)

    __str__=__repr__   

class itenv(j.builder._BaseClass):
    def __init__(self,company,name,path):
        JSBASE.__init__(self)
        self.company = company
        self.path=path
        self.name=name
        self.todo = []
        self.type="itenv"

    def addTodo(self,path,todo):
        todo=todo.replace("_","-")
        td=TODO(self,path,todo)
        self._logger.debug(td)
        self.todo.append(td)

    @property
    def todoPerItEnv(self):
        todo2={}
        for todo in self.todo:
            if todo.itenv not in todo2:
                todo2[todo.person]=[]
            todo2[todo.itenv].append(todo)
        return todo2

    @property
    def todo_md(self):
        md="# TODO FOR : %s %s\n\n"%(self.company,self.name)
        for person,todos in self.todoPerPerson.items():
            md+="## %s\n\n"%person
            for todo in todos:
                md+="- %s\n"%(todo.todo)
            md+="\n"

        return md

    def __repr__(self):
        return "itenv %s:%s:%s"%(self.company,self.name,self.path)

    __str__=__repr__

    


class ITEnvManager(j.builder._BaseClass):
    def __init__(self):
        self.__jslocation__ = "j.tools.itenv_manager"
        JSBASE.__init__(self)
        self.itenvs = {}
        self.devices = []
        self.clients = []

    def ip_exists(self,ipaddr):
        for key,device in self.devices.items():
            if device.ip_exists(ipaddr):
                return True
        return False

    def process(self,path="."):

        path0=path+"/data"

        if not j.sal.fs.exists(path0):
            raise RuntimeError("Cannot find teampath:%s"%path0)

        for tomlpath in j.sal.fs.listFilesInDir(path0, recursive=True, filter="device_*",followSymlinks=True, listSymlinks=False):
            d=Device(tomlpath)
            self.devices.append(d)

        for tomlpath in j.sal.fs.listFilesInDir(path0, recursive=True, filter="client_*",followSymlinks=True, listSymlinks=False):
            d=Client(tomlpath)
            self.clients.append(d)

        j.sal.fs.createDir("%s/todo"%path)

        out=""
        for device in self.devices:
            out+=device.todo_md
        path1="%s/todo/devices.md"%path
        if out=="":
            j.sal.fs.remove(path1)
        else:
            j.sal.fs.writeFile(path1,out)

        out=""
        for client in self.clients:
            out+=client.todo_md
        path1="%s/todo/clients.md"%path
        if out=="":
            j.sal.fs.remove(path1)
        else:
            j.sal.fs.writeFile(path1,out)


    def getDeviceFromName(self,name,die=False):
        for device in self.devices:
            if device.name==name.lower():
                return device
        if die:
            raise RuntimeError("Could not find device:%s"%name)
        return None
        
    def getDeviceFromIpAddr(self,ipaddr):
        for device in self.devices:
            if device.ip_exists(ipaddr):
                return device
        return None

    def getDevicesFree(self):
        res=[]
        for device in self.devices:
            if device.is_free:
                res.append(device)
        return res

    def getDevicesFreeLocation(self,location):
        res=[]
        for device in self.devices:
            if device.is_free:
                res.append(device)
        res=[item for item in res if location in item.location]
        return res
            

    def getClientConfigFromName(self,name):
        for client in self.clients:
            if client.name==name.lower():
                return client
        return None

    def getClientConfigsFromTypePart(self,ttype):
        """
        part from schema_type e.g. dnsapi
        """
        res=[]
        for client in self.clients:
            if ttype in client.schema_type:
                res.append(client)
        return res

    def getClientConfig(self,ttype,name,die=True):
        for client in self.getClientConfigsFromTypePart(ttype):
            if client.name==name.lower():
                return client
        if die:
            raise RuntimeError("Could not find client config with type:%s and name:%s"%(ttype,name))
        return None    

    def saveToMeConfig(self):
        """
        will remeber the nodes found in local host file as well as in your own config for js_config tool (where you can select nodes)
        """
        for device in self.devices:
            device.saveToMeConfig()
