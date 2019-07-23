from Jumpscale import j

from Jumpscale.data.bcdb.BCDBModelIndex import BCDBModelIndex

class {{BASENAME}}(BCDBModelIndex):

    {% if index.active %}

    def _init_index(self):
        self._log_info("init index:%s"%self.schema.url)

        p = j.clients.peewee

        db = self.bcdb.sqlclient.sqlitedb
        # print(db)

        class BaseModel(p.Model):
            class Meta:
                print("*%s"%db)
                database = db

        class Index_{{schema.key}}(BaseModel):
            id = p.IntegerField(unique=True)
            nid = p.IntegerField(index=True) #need to store the namespace id
            {%- for field in index.fields %}
            {{field.name}} = p.{{field.type}}(index=True)
            {%- endfor %}

        self._sql_index_db = Index_{{schema.key}}
        self._sql_index_db.create_table(safe=True)
        self.sql=self._sql_index_db


    def _sql_index_set(self,obj):
        idict={}
        {%- for field in index.fields %}
        {%- if field.jumpscaletype.NAME == "numeric" %}
        idict["{{field.name}}"] = obj.{{field.name}}_usd
        {%- else %}
        idict["{{field.name}}"] = obj.{{field.name}}
        {%- endif %}
        {%- endfor %}
        assert obj.id
        assert obj.nid
        idict["id"] = obj.id
        idict["nid"] = obj.nid
        #need to delete previous record from index
        self._sql_index_delete(obj)
        self._sql_index_db.insert(**idict).execute()

    def _sql_index_delete(self,obj):
        # if not self._sql_index_db.select().where(self._sql_index_db.id == obj.id).count()==0:
        self._sql_index_db.delete().where(self._sql_index_db.id == obj.id).execute()

    def _sql_index_destroy(self, nid=None):
        """
        will remove all namespaces indexes
        :param nid:
        :return:
        """
        if nid:
            self._sql_index_db.delete().where(self._sql_index_db.nid == nid).execute()
        else:
            self._sql_index_db.drop_table()
            self._sql_index_db.create_table()

    {% else %}
    def _init_index(self):
        return

    def _sql_index_set(self,obj):
        return

    def _sql_index_delete(self,obj):
        return

    def _sql_index_destroy(self, nid=None):
        return

    {% endif %}


    {%- if index.active_keys %}
    def _key_index_set(self,obj):
        {%- for property_name in index.fields_key %}
        val = obj.{{property_name}}
        if val not in ["",None]:
            val=str(val)
            # self._log_debug("key:{{property_name}}:%s:%s"%(val,obj.id))
            self._key_index_set_("{{property_name}}",val,obj.id,nid=obj.nid)
        {%- endfor %}

    def _key_index_delete(self,obj):
        {%- for property_name in index.fields_key %}
        val = obj.{{property_name}}
        if val not in ["",None]:
            val=str(val)
            self._log_debug("delete key:{{property_name}}:%s:%s"%(val,obj.id))
            self._key_index_delete_("{{property_name}}",val,obj.id,nid=obj.nid)
        {%- endfor %}

    {% else %}
    def _key_index_set(self,obj):
        return

    def _key_index_delete(self,obj):
        return

    {%- endif %}

    {%- if index.active_text %}
    def _text_index_set(self,obj):
        {%- for property_name in index.fields_text %}
        val = obj.{{property_name}}
        if val not in ["",None]:
            val=str(val)
            # self._log_debug("key:{{property_name}}:%s:%s"%(val,obj.id))
            self._text_index_set_("{{property_name}}",val,obj.id,nid=obj.nid)
        {%- endfor %}

    def _text_index_delete(self,obj):
        {%- for property_name in index.fields_text %}
        val = obj.{{property_name}}
        if val not in ["",None]:
            val=str(val)
            self._log_debug("delete key:{{property_name}}:%s:%s"%(val,obj.id))
            self._text_index_delete_("{{property_name}}",val,obj.id,nid=obj.nid)
        {%- endfor %}

    {% else %}
    def _text_index_set(self,obj):
        return

    def _text_index_delete(self,obj):
        return

    {%- endif %}
