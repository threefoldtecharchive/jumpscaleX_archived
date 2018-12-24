
from Jumpscale import j
import time
import psutil
import copy
JSBASE = j.application.JSBaseClass

class Pane(j.builder._BaseClass):

    def __init__(self, window, pane,name=""):
        JSBASE.__init__(self)
        self.mgmt = pane
        self.id = pane.get("pane_id")
        self.window = window
        if name != "":
            self.name_set(name)
        else:
            self.name = self.mgmt.get("pane_title")
        self._logger_enable()

    # @property
    # def name(self):
    #     res = j.core.db.hget("tmux:%s:name" % self.window.name, str(self.id))
    #     if res is None:
    #         return ""
    #     else:
    #         res = res.decode()
    #         return res

    # @name.setter
    # def name(self, name):
    #     j.core.db.hset("tmux:%s:name" % self.window.name, str(self.id), name)

    def name_set(self,name):
        cmd="\nprintf '\\033]2;%s\\033\\\\' '"+name+"'\n"
        self.mgmt.send_keys(cmd)
        self.name=name
        self.clear()


    def select(self):
        self.mgmt.select_pane()

    def splitVertical(self, name):
        pane = self.mgmt.split_window(attach=False, vertical=True, start_directory=None)
        self.window.reload()
        return Pane(self.window, pane,name)

    def splitHorizontal(self,  name):
        pane = self.mgmt.split_window(attach=False, vertical=False, start_directory=None)
        self.window.reload()
        return Pane(self.window, pane,name)


    def out_get(self,start=0,end=None):
        """
        will get content from pane, std gives the content of the active pane
        :param start:
        :param end:
        :return:
        """

        if not end:
            cmd="tmux capture-pane -t %%%s -pS -%s > /tmp/out.txt"%(self.id,start)
        else:
            cmd="tmux capture-pane -t %%%s -pS -%s -E %s > /tmp/out.txt"%(self.id,start,end)

        self._logger.debug(cmd)


        cmd=cmd.replace("%%","%")
        rc,out,err = j.sal.process.execute(cmd)


        out2=""
        lastline_empty=False

        for line in out.split("\n"):
            if line.strip()=="":
                if not lastline_empty==True:
                    lastline_empty=True
                    out2+="\n"
            else:
                lastline_empty=False
                out2+="%s\n"%line

        return out2



    def execute(self, cmd, wait=False):
        self._logger.debug (cmd)
        if not cmd.endswith("\n"):
            cmd+="\n"
        self.mgmt.send_keys(cmd)

    @property
    def pid(self):
        return int(self.mgmt.get("pane_pid"))

    @property
    def process_obj(self):
        p =  j.sal.process.getProcessObject(self.pid)
        return p

    @property
    def process_obj_children(self):
        return self._process_children_get(1)

    @property
    def cmd_running(self):
        return len(self.process_obj_children)>0

    @property
    def process_obj_child(self):
        cs = self.process_obj_children
        if len(cs)==1:
            return cs[0]
        elif len(cs)>1:
            raise RuntimeError("only support 1 child")
        else:
            return None

    def _process_children_get(self,depth=None,curdepth=0,res=None,process_obj=None):
        if process_obj is None:
            process_obj = self.process_obj
        if res is None:
            res=[]
        curdepth = curdepth+1
        for child in process_obj.children():
            if curdepth==depth or depth is None:
                res.append(child)
            res = self._process_children_get(process_obj=child, curdepth=curdepth,depth=depth,res=res)
        return res


    def kill(self):

        #a lot of work to get this working properly

        cmd='tmux list-panes -a -F "#{pane_pid} #{pane_id}"'
        cs=self.process_obj_children

        for child in  self.process_obj_children:
            try:
                child.send_signal(psutil.signal.SIGSTOP.value)
            except:
                pass

        time.sleep(0.1)

        for child in self.process_obj_children:
            try:
                child.send_signal(psutil.signal.SIGKILL.value)
            except:
                pass

        running=False
        for child in  self.process_obj_children:
            if child.is_running():
                running=True

        if running:
            time.sleep(0.1)
            p = j.sal.process.getProcessObject(int(pid))
            for child in  p.children():
                #now hardkill
                child.kill()

        while running:
            self._logger.debug("kill all processes")
            cs = self.process_obj_children
            if len(cs)==0:
                running=False
                break
            for child in  self.process_obj_children:
                self._logger.debug("try to kill:%s"%child)
                status = None
                try:
                    status = child.status()
                except Exception as e:
                    self._logger.debug(str(e))
                    if str(e).find("process no longer exists")!=-1:
                        continue
                    raise e

                if status is None:
                    continue

                child.kill()

            time.sleep(0.1)

        self.name_set(self.name.split("__",1)[0])

        self.clear()
        self.mgmt.reset()







    def clear(self):
        self.mgmt.clear()

    # def resetState(self):
    #     """
    #     make sure that previous exit code is removed and all is clean for next run
    #     """
    #     j.core.db.hset("tmux:%s:exec" % self.window.name, self.name, "")

    # def check(self):
    #     # res = j.core.db.hget("tmux:%s:exec" % self.window.name, self.name)
    #     if res == "":
    #         return ""
    #     res = res.decode()
    #     if ":" in res:
    #         epoch, rc = res.split(":")
    #         state = "OK"
    #     else:
    #         state = "INIT"
    #         rc = 0
    #         epoch = res
    #
    #     epoch = int(epoch)
    #     rc = int(rc)
    #     if rc > 0:
    #         state = "ERROR"
    #
    #     # duration=j.data.time.getTimeEpoch()-epoch
    #     return state, epoch, rc
    #
    # def wait(self):
    #     while True:
    #         state, epoch, rc = self.check()
    #         if state != "INIT":
    #             return state, epoch, rc
    #         time.sleep(0.1)

    def __repr__(self):
        return ("panel:%s:%s" % (self.id, self.name))

    __str__ = __repr__
