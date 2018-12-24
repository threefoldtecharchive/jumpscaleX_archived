from Jumpscale import j
# import _mysql
import time
import calendar

JSBASE = j.application.JSBaseClass


class MySQLFactory(j.builder._BaseClass):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.mysql"
        JSBASE.__init__(self)
        self.clients = {}

    def getClient(self, ipaddr, port, login, passwd, dbname):
        key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, passwd, dbname)
        if key not in self.clients:
            self.clients[key] = _mysql.connect(
                ipaddr, login, passwd, dbname, port=port)
        return MySQLClient(self.clients[key])


class MySQLClient(j.builder._BaseClass):

    def __init__(self, cl):
        JSBASE.__init__(self)
        self.client = cl

    def _html2text(self, html):
        return j.data.html.html2text(html)

    def _mysqlTimeToEpoch(self, mysql_time):
        if mysql_time is None:
            return 0
        mysql_time_struct = time.strptime(mysql_time, '%Y-%m-%d %H:%M:%S')
        mysql_time_epoch = calendar.timegm(mysql_time_struct)
        return mysql_time_epoch

    def _eptochToMysqlTime(self, time_epoch):
        time_struct = time.gmtime(time_epoch)
        time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
        return time_formatted

    def deleteRow(self, tablename, whereclause):
        Q = "DELETE FROM %s WHERE %s" % (tablename, whereclause)
        self.client.query(Q)
        result = self.client.use_result()
        if result is not None:
            result.fetch_row()

        return result

    def select1(self, tablename, fieldname, whereclause):
        Q = "SELECT %s FROM %s WHERE %s;" % (fieldname, tablename, whereclause)
        result = self.queryToListDict(Q)
        if len(result) == 0:
            return None
        else:
            return result

    def queryToListDict(self, query):
        self.client.query(query)
        fields = {}
        result = self.client.use_result()
        counter = 0
        for field in result.describe():
            fields[counter] = field[0]
            counter += 1

        resultout = []
        while True:
            row = result.fetch_row()
            if len(row) == 0:
                break
            row = row[0]
            rowdict = {}
            for colnr in range(0, len(row)):
                colname = fields[colnr]
                if colname.find("dt__") == 0:
                    colname = colname[4:]
                    col = self._mysqlTimeToEpoch(row[colnr])
                elif colname.find("id__") == 0:
                    colname = colname[4:]
                    col = int(row[colnr])
                elif colname.find("bool__") == 0:
                    colname = colname[6:]
                    col = str(row[colnr]).lower()
                    if col == "1":
                        col = True
                    elif col == "0":
                        col = False
                    elif col == "false":
                        col = False
                    elif col == "true":
                        col = False
                    else:
                        raise j.exceptions.RuntimeError(
                            "Could not decide what value for bool:%s" % col)
                elif colname.find("html__") == 0:
                    colname = colname[6:]
                    col = self._html2text(row[colnr])
                else:
                    col = row[colnr]

                rowdict[colname] = col
            resultout.append(rowdict)

        return resultout
