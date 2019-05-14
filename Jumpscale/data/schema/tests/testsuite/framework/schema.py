from Jumpscale import j


class Schema:
    def __init__(self, schema):
        self.schema = schema
        self.schema_obj = None
            
    @property
    def schema_object(self):
        self.schema_obj = j.data.schema.get_from_text(schema_text=self.schema)
        return self.schema_obj
   
    def new(self):
        self.schema_obj = self.schema_obj or self.schema_object
        return self.schema_obj.new()
