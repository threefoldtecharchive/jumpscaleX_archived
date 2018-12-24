from Jumpscale import j

JSBASE = j.application.JSBaseClass


class SerializerBase(j.builder._BaseClass):

    def dump(self, filepath, obj):
        data = self.dumps(obj)
        j.sal.fs.writeFile(filepath, data)

    def load(self, path):
        b = j.sal.fs.readFile(path)
        try:
            r = self.loads(b)
        except Exception as e:
            error = "error:%s\n" % e
            error += "\could not parse:\n%s\n" % b
            error += '\npath:%s\n' % path
            raise j.exceptions.Input(message=error)
        return r



# class SerializerHalt(j.builder._BaseClass):
#
#     def __init__(self):
#         JSBASE.__init__(self)
#
#     def dump(self, filepath, obj):
#         raise RuntimeError("should not come here")
#
#     def load(self, path):
#         raise RuntimeError("should not come here")
#
#     def dumps(self, val):
#         raise RuntimeError("should not come here")
#
#     def loads(self, data):
#         raise RuntimeError("should not come here")
