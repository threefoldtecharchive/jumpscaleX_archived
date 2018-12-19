from Jumpscale import j

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import class_mapper
from sqlalchemy import *
from sqlalchemy.event import listen

from sqlalchemy.ext.declarative import declarative_base
from copy import copy
import collections

Base0 = declarative_base()


def object_to_dict(obj, found=None, path="", notfollow=[], depth=0, maxdepth=1, subprimkeyonly=True):
    # print "%s %s"%(depth,path)
    depth += 1
    if found is None:
        found = set()
    mapper = class_mapper(obj.__class__)

    # #to work with dates, but we don't use that
    # def get_key_value (c):
    #     if isinstance(getattr(obj, c), datetime):
    #         return c,getattr(obj, c).isoformat()
    #     else:
    #         return c,getattr(obj, c)

    # if subprimkeyonly then we only return the primary key and not the other
    # properties of related objects
    if depth > 1 and subprimkeyonly:
        for column in mapper.columns:
            if column.primary_key:
                out = getattr(obj, column.key)
    else:
        out = {}
        for column in mapper.columns:
            out[column.key] = getattr(obj, column.key)
    path0 = copy(path)
    for name, relation in list(mapper.relationships.items()):
        path = path0 + "/%s" % name
        if path in notfollow:
            continue
        if depth > maxdepth:
            continue
        if relation not in found:
            found.add(relation)
            related_obj = getattr(obj, name)
            if related_obj is not None:
                if relation.uselist:
                    out[name] = [object_to_dict(
                        child, found, path, notfollow, depth, maxdepth, subprimkeyonly) for child in related_obj]
                else:
                    out[name] = object_to_dict(
                        related_obj, found, path, notfollow, depth, maxdepth, subprimkeyonly)
    return out


class Base(Base0):

    __abstract__ = True
    _totoml = False

    def __init__(self, **kwargs):
        for attr in self.__mapper__.column_attrs:
            if attr.key in kwargs:
                continue

            # TODO: Support more than one value in columns?
            assert len(attr.columns) == 1
            col = attr.columns[0]

            if col.default and not isinstance(col.default.arg, collections.Callable):
                kwargs[attr.key] = col.default.arg

        super(Base, self).__init__(**kwargs)

    def getDataAsDict(self):
        return object_to_dict(self, maxdepth=1, notfollow="/sync")

    def _tomlpath(self, sqlalchemy):
        path = "%s/%s/%s.toml" % (sqlalchemy.tomlpath,
                                  self.__tablename__, self.id.lower())
        return path

    def __repr__(self):
        return str(self.getDataAsDict())


JSConfigFactory = j.application.JSFactoryBaseClass
JSConfigClient = j.application.JSBaseClass

TEMPLATE = """
connectionstring = ""
sqlitepath = ""
tomlpath = "../data"
"""


class SQLAlchemyFactory(JSConfigFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.sqlalchemy"
        self.__imports__ = "sqlalchemy"
        JSConfigFactory.__init__(self, SQLAlchemy)

    def getBaseClass(self):
        """
        complete example how to use sqlalchemy:
        https://github.com/Jumpscale/jumpscaleX/wiki/SQLAlchemy
        """
        return Base

    def validate_lower_strip(self, target, value, oldvalue, initiator):
        value = value.lower().strip()
        return value

    def validate_tel(self, target, value, oldvalue, initiator):
        value = value.lower().strip()
        value = value.replace(".", "")
        value = value.replace(",", "")
        value = value.replace("+", "")
        return value

    def validate_email(self, target, value, oldvalue, initiator):
        value = value.lower().strip()
        if value.find("@") == -1:
            raise j.exceptions.Input(
                "Property error, email not formatted well, needs @.Val:%s\nObj:\n%s" % (value, target))
        return value


class SQLAlchemy(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        c = self.config.data
        if c['sqlitepath'] != "":
            self.connectionstring = 'sqlite:///%s' % c['sqlitepath']
        else:
            self.connectionstring = c['connectionstring']

        self.tomlpath = c['tomlpath']
        self.engine = None
        self.session = None
        self.sqlitepath = c['sqlitepath']
        self._initsql()

    def _initsql(self):
        if self.engine is None:
            if self.sqlitepath != "":
                if not j.sal.fs.exists(path=self.sqlitepath):
                    self.engine = self.resetDB()
                else:
                    self.engine = create_engine(
                        self.connectionstring, echo=False)
            self._Session = sessionmaker(bind=self.engine)
            self.session = self._Session()
            listen(Base, 'before_insert', self.data2toml, propagate=True)
            listen(Base, 'before_update', self.data2toml, propagate=True)
            listen(Base, 'after_delete', self.removetoml, propagate=True)

    def resetDB(self):
        if self.sqlitepath != "":
            j.sal.fs.remove(self.sqlitepath)
            engine = create_engine('sqlite:///%s' %
                                   self.sqlitepath, echo=False)
            Base.metadata.create_all(engine)
            self.engine = None
            return engine

    def data2toml(self, mapper, connection, target):
        if target._totoml and self.tomlpath != "":
            data = target.getDataAsDict()
            out = j.data.serializers.toml.dumps(data)
            path = target._tomlpath(self)
            j.sal.fs.createDir(j.sal.fs.getDirName(path))
            j.sal.fs.writeFile(filename=path, contents=out)

    def removetoml(self, mapper, connection, target):
        if target._totoml and self.tomlpath != "":
            path = target._tomlpath(self)
            path = "%s/%s/%s.toml" % (self.tomlpath,
                                      target.__tablename__, target.id.lower())
            j.sal.fs.remove(path)
