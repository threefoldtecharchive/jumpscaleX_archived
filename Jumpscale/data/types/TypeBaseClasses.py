

class TypeBaseObjClass():

    def check(self):
        '''
        Check whether provided value is the native type
        '''
        return self.typebase.check(ip=self.value)

    def possible(self):
        '''
        Check whether provided value can be converted to this type
        '''
        try:
            self.typebase.clean(self.value)
        except:
            return False
        return True

    def capnp_schema_get(self, name, nr):
        return self.typebase.capnp_schema_get(name, nr)

    def get_default(self):
        return self.typebase.get_default()

    def toString(self, v):

        return self.clean(v)

    def toData(self):
        value = self.clean(self.value)
        return self.typebase.toData(value)

    def clean(self):
        """
        can use int or string,
        will find it and return as string
        """
        return self.value

    def __equal__(self):
        # TODO
        pass

    def __str__(self):
        return "TODO: %s (default:%s)" % (self.values_str, self.default)

    __repr__ = __str__


class TypeBaseClass():

    def toString(self, v):
        return self.clean(v)

    def toHR(self, v):
        return self.clean(v)

    def toData(self, v):
        return self.clean(v)

    def check(self, value):
        '''
        - if there is a specific implementation e.g. string, float, enumeration, it will check if the input is that implementation
        - if not strict implementation or we cannot know e.g. an address will return None
        '''
        return False

    def possible(self):
        """
        will check if it can be converted to the jumpscale representation, basically the clean works without error
        :return:
        """
        try:
            self.clean()
            return True
        except Exception as e:
            return False

    def get_default(self):
        return ""

    def clean(self, value):
        """
        will do a strip and conversion to string
        """
        if value is None:
            value = ""
        value = str(value)
        value = value.strip("").strip("'").strip("\"").strip("")
        return value

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        value = self.clean(value)
        return "'%s'" % value

    def toml_string_get(self, value, key=""):
        """
        will translate to what we need in toml
        """
        if key == "":
            return "'%s'" % (self.clean(value))
        else:
            return "%s = '%s'" % (key, self.clean(value))

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Text;" % (name, nr)

    def unique_sort(self, txt):
        return "".join(j.data.types.list.clean(txt))
