from Jumpscale import j
import imp

JSBASE = j.application.JSBaseClass

class CodeLoader(j.application.JSBaseClass):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.tools.loader"
        JSBASE.__init__(self)
        # self._logger_enable()
        j.sal.fs.createDir("%s/CODEGEN"%j.dirs.VARDIR)
        self._hash_to_codeobj = {}

    def _basename(self,path):
        obj_key=j.sal.fs.getBaseName(path)
        if obj_key.endswith(".py"):
            obj_key = obj_key[:-3]
        if obj_key[0] in "0123456789":
            raise RuntimeError("obj key cannot start with nr")
        return obj_key

    def load_text(self,obj_key="",text="",dest="", reload=False,md5=""):
        """

        write text as code file or in CODEGEN location or specified dest
        load this text as code in mem (module python)
        get the objkey out of the code e.g. a method or a class

        :param obj_key:  is name of function or class we need to evaluate when the code get's loaded
        :param text: if not path used, text = is the text of the template (the content)
        :param dest: if not specified will be in j.dirs.VARDIR,"CODEGEN",md5+".py" (md5 is md5 of template+msgpack of args)
        :param reload: will reload the template and re-render
        :return:
        """
        if md5 is "":
            md5 = j.data.hash.md5_string(text)
        if dest is "":
            dest = j.sal.fs.joinPaths(j.dirs.VARDIR,"CODEGEN",md5+".py")

        if reload or not j.sal.fs.exists(dest):
            j.sal.fs.writeFile(dest,text)

        return self.load(obj_key=obj_key,path=dest,reload=reload,md5=md5)


    def load(self, obj_key="", path="",reload=False,md5=""):
        """

        example:

        j.tools.loader.load(obj_key,path=path,reload=False)

        :param obj_key:  is name of function or class we need to evaluate when the code get's loaded
        :param path: path of the template (is path or text to be used)
        :param reload: will reload the template and re-render
        :return:
        """
        if not obj_key:
            obj_key = self._basename(path)

        if not j.data.types.string.check(path):
            raise RuntimeError("path needs to be string")
        if path!="" and not j.sal.fs.exists(path):
            raise RuntimeError("path:%s does not exist"%path)

        if md5=="":
            md5=j.data.hash.md5_string(path)
        if reload or md5 not in self._hash_to_codeobj:

            try:
                m=imp.load_source(name=md5, pathname=path)
            except Exception as e:
                msg = "COULD not load source:%s\n"%path
                msg+= "ERROR WAS:%s\n\n"%e
                out = j.sal.fs.readFile(path)
                msg+="SCRIPT CONTENT:\n%s\n\n"%out
                raise RuntimeError(msg)
            try:
                obj = eval("m.%s"%obj_key)
            except Exception as e:
                msg = "COULD not import source:%s\n"%path
                msg+= "ERROR WAS:%s\n\n"%e
                msg += "obj_key:%s\n"%obj_key
                out = j.sal.fs.readFile(path)
                msg+="SCRIPT CONTENT:\n%s\n\n"%out
                raise RuntimeError(msg)

            self._hash_to_codeobj[md5] = obj

        return self._hash_to_codeobj[md5]
