from Jumpscale import j
import psycopg2
import time
import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import binascii
import copy

# import calendar
# from htmllib import HTMLParser
# from formatter import AbstractFormatter, DumbWriter
# from io import StringIO
# import JumpscaleLib.lib.html


JSConfigFactory = j.application.JSFactoryBaseClass
JSConfigClient = j.application.JSBaseClass

TEMPLATE = """
ipaddr = ""
port = ""
login = ""
passwd_ = ""
dbname = ""
"""


class PostgresqlFactory(JSConfigFactory):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.postgres"
        self.__imports__ = "sqlalchemy"
        JSConfigFactory.__init__(self, PostgresClient)

    def createdb(self, db, ipaddr="localhost", port=5432, login="postgres", passwd="rooter"):
        client = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (
            "template1", login, ipaddr, passwd, port))
        cursor = client.cursor()
        client.set_isolation_level(0)
        try:
            cursor.execute("create database %s;" % db)
        except Exception as e:
            if str(e).find("already exists") != -1:
                pass
            else:
                raise j.exceptions.RuntimeError(e)
        client.set_isolation_level(1)

    def dropdb(self, db, ipaddr="localhost", port=5432, login="postgres", passwd="rooter"):
        args = {}
        args["db"] = db
        args["port"] = port
        args["login"] = login
        args["passwd"] = passwd
        args["ipaddr"] = ipaddr
        args["dbname"] = db
        cmd = "cd /opt/postgresql/bin;./dropdb -U %(login)s -h %(ipaddr)s -p %(port)s %(dbname)s" % (
            args)
        j.sal.process.execute(cmd, showout=False, die=False)


class PostgresClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        c = self.config.data

        self.ipaddr = c['ipaddr']
        self.port = c['port']
        self.login = c['login']
        self.passwd = c['passwd_']
        self.dbname = c['dbname']
        self.client = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (
            self.dbname, self.login, self.ipaddr, self.passwd, self.port))
        self.cursor = None

    def getcursor(self):
        self.cursor = self.client.cursor()

    def execute(self, sql):
        if self.cursor is None:
            self.getcursor()
        return self.cursor.execute(sql)

    def getSQLAlchemyClient(self):
        """
        usage

        base,session=client.initsqlalchemy()
        session.add(base.classes.address(email_address="foo@bar.com", user=(base.classes.user(name="foo")))
        session.commit()

        """
        Base = automap_base()

        # engine, suppose it has two models 'user' and 'address' set up
        engine = create_engine(
            "postgresql://%(login)s:%(passwd)s@%(ipaddr)s:%(port)s/%(dbname)s" % self.__dict__)

        # reflect the models
        Base.prepare(engine, reflect=True)

        session = Session(engine)

        return Base, session

    def getPeeweeClient(self):
        """
        # TODO
        """
        pass

    def dump(self, path, tablesIgnore=[]):
        args = copy.copy(self.__dict__)
        j.sal.fs.createDir(path)
        base, session = self.initsqlalchemy()

        args["path"] = "%s/_schema.sql" % (path)
        cmd = "cd /opt/postgresql/bin;./pg_dump -U %(login)s -h %(ipaddr)s -p %(port)s -s -O -d %(dbname)s -w > %(path)s" % (
            args)
        j.sal.process.execute(cmd, showout=False)

        for name, obj in list(base.classes.items()):
            if name in tablesIgnore:
                continue
            self._logger.debug("process table:%s" % name)
            args["table"] = name
            args["path"] = "%s/%s.sql" % (path, name)
            #--quote-all-identifiers
            cmd = "cd /opt/postgresql/bin;./pg_dump -U %(login)s -h %(ipaddr)s -p %(port)s -t %(table)s -a -b --column-inserts -d %(dbname)s -w > %(path)s" % (
                args)
            j.sal.process.execute(cmd, showout=False)

    def restore(self, path, tables=[], schema=True):
        if not j.sal.fs.exists(path=path):
            raise j.exceptions.Input(
                "cannot find path %s to import from." % path)
        args = copy.copy(self.__dict__)
        if schema:
            args["base"] = path
            # cmd="cd /opt/postgresql/bin;./pg_restore -1 -e -s -U %(login)s -h %(ipaddr)s -p %(port)s %(base)s/_schema.sql"%(args)
            cmd = "cd /opt/postgresql/bin;./psql -U %(login)s -h %(ipaddr)s -p %(port)s -d %(dbname)s < %(base)s/_schema.sql" % (
                args)
            j.sal.process.execute(cmd, showout=False)

        for item in j.sal.fs.listFilesInDir(path, recursive=False, filter="*.sql",
                                            followSymlinks=True, listSymlinks=True):
            name = j.sal.fs.getBaseName(item).replace(".sql", "")
            if name.find("_") == 0:
                continue
            if name in tables or tables == []:
                args["path"] = item
                # cmd="cd /opt/postgresql/bin;./pg_restore -1 -e -U %(login)s -h %(ipaddr)s -p %(port)s %(path)s"%(args)
                cmd = "cd /opt/postgresql/bin;./psql -1 -U %(login)s -h %(ipaddr)s -p %(port)s -d %(dbname)s < %(path)s" % (
                    args)
                j.sal.process.execute(cmd, showout=False)

    def exportToYAML(self, path):
        """
        TODO: export

        export to $path/$objectType/$id_$name.yaml (if id & name exists)
        else: export to $path/$objectType/$id_$dest[1:20].yaml (if id & descr exists)
        else: export to $path/$objectType/$id.yaml (if id & descr exists)
        if id does not exist but guid or uid does, use that one in stead of id

        check for deletes

        """
        pass

    def importFromYAML(self, path):
        """
        TODO:
        """
        pass

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
