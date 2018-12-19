import collections
from Jumpscale import j
class List0(collections.MutableSequence):

    def __init__(self,schema_property):
        self._inner_list = []
        self.schema_property = schema_property
        self.changed = False

    def __len__(self):
        return len(self._inner_list)

    def __eq__ (self,val):
        return val == self._inner_list

    def __delitem__(self, index):
        self._inner_list.__delitem__(index )
        self.changed = True

    def insert(self, index, value):
        if self.schema_property.pointer_type is None:
            value = self.schema_property.jumpscaletype.SUBTYPE.clean(value)
        else:
            if j.data.types.dict.check(value):
                o=self.new()
                o.load_from_data(data=value)
                # value = o
                self.changed = True
                return
            elif not "_JSOBJ" in value.__dict__:
                raise RuntimeError("need to insert JSOBJ, use .new() on list before inserting.")
        self._inner_list.insert(index, value)
        self.changed = True

    def __setitem__(self, index, value):
        if self.schema_property.pointer_type is None:
            value = self.schema_property.jumpscaletype.SUBTYPE.clean(value)
        else:
            if not "_JSOBJ" in value.__dict__:
                raise RuntimeError("need to insert JSOBJ, use .new() on list before inserting.")
        self._inner_list.__setitem__(index, value)
        self.changed = True

    def __getitem__(self, index):
        return self._inner_list.__getitem__(index)

    def pylist(self, subobj_format="D"):
        """
        python clean list

        :param subobj_format, will be dict of J=DDICT_JSON, D=DDICT H=DDict_HR  representations of the object
        """
        if self.schema_property.pointer_type is None:
            return self._inner_list
        else:
            if subobj_format=="J":
                return [item._ddict_json for item in self._inner_list]
            elif subobj_format == "D":
                return [item._ddict for item in self._inner_list]
            elif subobj_format == "H":
                return [item._ddict_hr for item in self._inner_list]
            else:
                raise RuntimeError("only support type J,D,H")

    def new(self,data=None):
        """
        return new subitem, only relevant when there are pointer_types used
        """
        if self.schema_property.pointer_type is None:
            if data is not None:
                data = self.schema_property.jumpscaletype.SUBTYPE.clean(data)
            else:
                data = self.schema_property.jumpscaletype.SUBTYPE.get_default()
        else:

            if data is None:
                data=self.pointer_schema.new()
            else:
                data = self.pointer_schema.get(capnpbin=data)
        if data:
            self.append(data)
        self.changed = True
        return data

    @property
    def pointer_schema(self):
        # issue #35 *REALLY* obscure bug, probably down to properties
        # being accessed in the wrong order (some cached, some not)
        # by ignoring self._pointer_schema and always re-generating
        # using get, the problem "goes away".
        # definitely needs full investigation.
        if True or self._pointer_schema is None:
            if self.schema_property.pointer_type==None:
                raise RuntimeError("can only be used when pointer_types used")
            s =  j.data.schema.get(url=self.schema_property.pointer_type)
            self._pointer_schema = s
        return self._pointer_schema

    def __repr__(self):
        out=""
        for item in self.pylist(subobj_format="D"):
            out+="- %s\n"%item
        if out.strip()=="":
            return "[]"
        return out
            

    __str__ = __repr__
