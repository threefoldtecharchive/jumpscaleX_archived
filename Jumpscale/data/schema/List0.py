import collections
from Jumpscale import j

from collections.abc import MutableSequence

class List0(MutableSequence):

    def __init__(self, schema_property):
        self._inner_list = []
        self.schema_property = schema_property
        self.changed = False

    def __len__(self):
        """
        get length of list
        """

        return len(self._inner_list)

    def __eq__(self, val):
        return val == self._inner_list

    def __delitem__(self, index):
        """
        delete the item using index of collections
        """

        self._inner_list.__delitem__(index)
        self.changed = True

    def insert(self, index, value):
        """
        insert value in specific index in collections 

        Arguments:
            index : location in collections
            value : value that add in collections
        """

        if self.schema_property.pointer_type is None:
            value = self.schema_property.jumpscaletype.SUBTYPE.clean(value)
        else:
            if j.data.types.dict.check(value):
                o = self.new()
                o.load_from_data(data=value)
                self.changed = True
                return
            elif not "_JSOBJ" in value.__dict__:
                raise RuntimeError("need to insert JSOBJ, use .new() on list before inserting.")
        self._inner_list.insert(index, value)
        self.changed = True

    def __setitem__(self, index, value):
        """
        insert value in specific index in collections 
        Arguments:
            index : location in collections
            value : value that add in collections
        """

        if self.schema_property.pointer_type is None:
            value = self.schema_property.jumpscaletype.SUBTYPE.clean(value)
        else:
            if not "_JSOBJ" in value.__dict__:
                raise RuntimeError("need to insert JSOBJ, use .new() on list before inserting.")
        self._inner_list.__setitem__(index, value)
        self.changed = True

    def __getitem__(self, index):
        """
        get item from list using index
        """

        return self._inner_list.__getitem__(index)

    def pylist(self, subobj_format="D"):
        """
        python clean list

        :param subobj_format
        +--------------------+--------------------+-----------------------------------------------------------------------------------+
        |     value          |     Description    |                example                                                            |
        +--------------------+--------------------+-----------------------------------------------------------------------------------+
        |       J            |     DDICT_JSON     | ['{\n"valid": false,\n"token_price": "\\u00000\\u0005\\u0000\\u0000\\u0000"\n}']  |
        |       D            |     DDICT          | [{'valid': False, 'token_price': b'\x000\x05\x00\x00\x00'}]                       |
        |       H            |     DDict_HR       | [{valid': False, 'token_price': '5 EUR'}]                                         |
        +--------------------+--------------------+-----------------------------------------------------------------------------------+
        """
        if self.schema_property.pointer_type is None:
            return self._inner_list
        else:
            if subobj_format == "J":
                return [item._ddict_json for item in self._inner_list]
            elif subobj_format == "D":
                return [item._ddict for item in self._inner_list]
            elif subobj_format == "H":
                return [item._ddict_hr for item in self._inner_list]
            else:
                raise RuntimeError("only support type J,D,H")

    def new(self, data=None):
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
                data = self.pointer_schema.new()
            else:
                data = self.pointer_schema.get(capnpbin=data)
        if data:
            self.append(data)
        self.changed = True
        return data

    @property
    def pointer_schema(self):
        if self.schema_property.pointer_type is None:
            raise RuntimeError("can only be used when pointer_types used")
        return j.data.schema.get(url=self.schema_property.pointer_type)

    def __repr__(self):
        out = ""
        for item in self.pylist(subobj_format="D"):
            out += "- %s\n" % item
        if out.strip() == "":
            return "[]"
        return out

    __str__ = __repr__
