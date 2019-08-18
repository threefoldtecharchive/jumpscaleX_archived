from Jumpscale import j
import psycopg2
import time
import datetime

# try:
#     from sqlalchemy.ext.automap import automap_base
#     from sqlalchemy.orm import Session
#     from sqlalchemy import create_engine
# except:
#     pass
import binascii
import copy

JSConfigClient = j.application.JSBaseConfigClass


class PostgresClient(JSConfigClient):
    _SCHEMATEXT = """
    @url = jumpscale.postgres.client
    name* = "" (S)
    ipaddr = "" (S)
    port = 5432 (ipport)
    login = "root" (S)
    passwd_ = "" (S)
    dbname = "odoo_test" (S)
    """

    def _init(self, **kwargs):
        self._client = None
        self.cursor = None

    @property
    def client(self):
        if not self._client:
            self._client = psycopg2.connect(
                "dbname='%s' user='%s' host='%s' password='%s' port='%s'"
                % ("postgres", self.login, self.ipaddr, self.passwd_, self.port)
            )
        return self._client

    def db_names_get(self):
        r = self.execute("SELECT * FROM pg_catalog.pg_database")
        r2 = [i[0] for i in r]
        return r2

    def cursor_get(self):
        """Get client dict cursor
        """
        return self.client.cursor()

    def execute_cursor(self, sql):
        """Execute sql code

        c=cl.execute("SELECT version();")
        c.fetchone()


        :param sql: sql code to be executed
        :type sql: str
        :return: psycopg2 client
        :rtype: dict cursor
        """
        cursor = self.cursor_get()
        cursor.execute(sql)
        return cursor

    def execute(self, sql):
        """
        print(cl.execute("SELECT version();"))
        :param sql:
        :return:
        """
        r = self.execute_cursor(sql)
        return r.fetchall()

    def peewee_client_get(self):
        cl = j.clients.peewee.get(**self._data._ddict)
        return cl

    def sqlalchemy_client_get(self):
        """ usage

        base,session=client.sqlalchemy_client_get()
        # engine, suppose it has two models 'user' and 'address' set up
        session.add(base.classes.address(email_address="foo@bar.com", user=(base.classes.user(name="foo")))
        session.commit()
        
        :return: Base, session
        """
        try:
            from sqlalchemy.ext.automap import automap_base
        except:
            j.builders.runtimes.python.pip_package_install("sqlalchemy")

        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy.orm import Session
        from sqlalchemy import create_engine

        Base = automap_base()

        engine = create_engine("postgresql://%(login)s:%(passwd_)s@%(ipaddr)s:%(port)s/%(dbname)s" % self._data._ddict)

        # reflect the models
        Base.prepare(engine, reflect=True)

        session = Session(engine)

        return Base, session

    def db_drop(self, dbname=None):
        """Drop a database
        :param dbname: db name to be dropped, if None will be current database
        """
        args = self._data._ddict
        if dbname:
            args["dbname"] = dbname
        cmd = "cd /opt/postgresql/bin;./dropdb -U %(login)s -h %(ipaddr)s -p %(port)s %(dbname)s" % (args)
        j.sal.process.execute(cmd, showout=False, die=False)

    def db_create(self, dbname=None, die=False):
        """Create new database
        :param dbname: db name to be dropped, if None will be current database
        :raises j.exceptions.RuntimeError: Exception if db already exists
        """
        if not dbname:
            dbname = self.dbname

        cursor = self.client.cursor()
        self.client.set_isolation_level(0)
        try:
            cursor.execute("create database %s;" % dbname)
        except Exception as e:
            if str(e).find("already exists") != -1:
                if die:
                    raise ("database already exists:'%s'" % dbname)
            else:
                raise j.exceptions.RuntimeError(e)
        self.client.set_isolation_level(1)

    def dump_tables(self, path=None, tables_ignore=[]):
        """Dump data from db to path/_schema.sql

        TODO: not sure this always works because what if tables are dependent on each other?

        :param path: path of dir where all will be dumped
        :type path: str
        :param tables_ignore: tables to be ignored and its records are not considered, defaults to []
        :type tables_ignore: list, optional
        """
        args = self._data._ddict
        j.sal.fs.createDir(path)
        base, session = self.sqlalchemy_client_get()
        if not path:
            path = "/tmp/postgresql_dump"
        args["path"] = "%s/_schema.sql"
        cmd = (
            "cd /opt/postgresql/bin;./pg_dump -U %(login)s -h %(ipaddr)s -p %(port)s -s -O -d %(dbname)s -w > %(path)s"
            % (args)
        )
        j.sal.process.execute(cmd, showout=False)

        for name, obj in list(base.classes.items()):
            if name in tables_ignore:
                continue
            self._log_debug("process table:%s" % name)
            args["table"] = name
            args["path"] = "%s/%s.sql" % (path, name)
            # --quote-all-identifiers
            cmd = (
                "cd /opt/postgresql/bin;./pg_dump -U %(login)s -h %(ipaddr)s -p %(port)s -t %(table)s -a -b --column-inserts -d %(dbname)s -w > %(path)s"
                % (args)
            )
            j.sal.process.execute(cmd, showout=False)

    def restore_tables(self, path, tables=[], schema=True):
        """Restore db

        :param path: path to import from
        :type path: str
        :param tables: tables to be considered, defaults to [] which means all are imported
        :type tables: list, optional
        :param schema: schema exists, defaults to True
        :type schema: bool, optional
        :raises j.exceptions.Input: Path to import from not found
        """
        if not path:
            path = "/tmp/postgresql_dump"
        if not j.sal.fs.exists(path=path):
            raise j.exceptions.Input("cannot find path %s to import from." % path)
        args = self._data._ddict
        if schema:
            args["base"] = path
            # cmd="cd /opt/postgresql/bin;./pg_restore -1 -e -s -U %(login)s -h %(ipaddr)s -p %(port)s %(base)s/_schema.sql"%(args)
            self.execute(j.sal.fs.readFile("%s/_schema.sql" % path))
        for item in j.sal.fs.listFilesInDir(
            path, recursive=False, filter="*.sql", followSymlinks=True, listSymlinks=True
        ):
            name = j.sal.fs.getBaseName(item).replace(".sql", "")
            if name.find("_") == 0:
                continue
            if name in tables or tables == []:
                self.execute(j.sal.fs.readFile("%s/%s.sql" % (path, name)))

    # def exportToYAML(self, path):
    #     """
    #     TODO: export

    #     export to $path/$objectType/$id_$name.yaml (if id & name exists)
    #     else: export to $path/$objectType/$id_$dest[1:20].yaml (if id & descr exists)
    #     else: export to $path/$objectType/$id.yaml (if id & descr exists)
    #     if id does not exist but guid or uid does, use that one in stead of id

    #     check for deletes

    #     """
    #     pass

    # def importFromYAML(self, path):
    #     """
    #     TODO:
    #     """
    #     pass

    # def _html2text(self, html):
    #     return j.data.html.html2text(html)

    # def _postgresTimeToEpoch(self,postgres_time):
    #     if postgres_time==None:
    #         return 0
    #     postgres_time_struct = time.strptime(postgres_time, '%Y-%m-%d %H:%M:%S')
    #     postgres_time_epoch = calendar.timegm(postgres_time_struct)
    #     return postgres_time_epoch

    # def _eptochToPostgresTime(self,time_epoch):
    #     time_struct = time.gmtime(time_epoch)
    #     time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    #     return time_formatted

    # def deleteRow(self,tablename,whereclause):
    #     Q="DELETE FROM %s WHERE %s"%(tablename,whereclause)
    #     self.client.execute(Q)
    #     result = self.client.use_result()
    #     if result!=None:
    #         result.fetch_row()

    #     return result

    # def select1(self,tablename,fieldname,whereclause):
    #     Q="SELECT %s FROM %s WHERE %s;"%(fieldname,tablename,whereclause)
    #     result=self.queryToListDict(Q)
    #     if len(result)==0:
    #         return None
    #     else:
    #         # from IPython import embed
    #         # embed()

    #         return result

    # def queryToListDict(self,query):
    #     self.client.query(query)
    #     fields={}
    #     result = self.client.use_result()
    #     counter=0
    #     for field in result.describe():
    #         fields[counter]=field[0]
    #         counter+=1

    #     resultout=[]
    #     while True:
    #         row=result.fetch_row()
    #         if len(row)==0:
    #             break
    #         row=row[0]
    #         rowdict={}
    #         for colnr in range(0,len(row)):
    #             colname=fields[colnr]
    #             if colname.find("dt__")==0:
    #                 colname=colname[4:]
    #                 col=self._postgresTimeToEpoch(row[colnr])
    #             elif colname.find("id__")==0:
    #                 colname=colname[4:]
    #                 col=int(row[colnr])
    #             elif colname.find("bool__")==0:
    #                 colname=colname[6:]
    #                 col=str(row[colnr]).lower()
    #                 if col=="1":
    #                     col=True
    #                 elif col=="0":
    #                     col=False
    #                 elif col=="false":
    #                     col=False
    #                 elif col=="true":
    #                     col=False
    #                 else:
    #                     raise j.exceptions.RuntimeError("Could not decide what value for bool:%s"%col)
    #             elif colname.find("html__")==0:
    #                 colname=colname[6:]
    #                 col=self._html2text(row[colnr])
    #             else:
    #                 col=row[colnr]

    #             rowdict[colname]=col
    #         resultout.append(rowdict)

    #     return resultout
