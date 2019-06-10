from Jumpscale import j
import time
import calendar

JSConfigClient = j.application.JSBaseConfigClass


class MySQLClient(JSConfigClient):
    _SCHEMATEXT = """
    @url = jumpscale.mysql.client
    name* = "" (S)
    ipaddr = "127.0.0.1" (ipaddr)
    port = 3306 (ipport)
    login = "" (S)
    passwd = "" (S)
    dbname = "" (S)
    """

    def connect(self):
        if not self.client.is_connected():
            self.client.connect()

    def _html2text(self, html):
        return j.data.html.html2text(html)

    def _mysqlTimeToEpoch(self, mysql_time):
        if mysql_time is None:
            return 0
        mysql_time_struct = time.strptime(mysql_time, "%Y-%m-%d %H:%M:%S")
        mysql_time_epoch = calendar.timegm(mysql_time_struct)
        return mysql_time_epoch

    def _eptochToMysqlTime(self, time_epoch):
        time_struct = time.gmtime(time_epoch)
        time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        return time_formatted

    def deleteRow(self, tablename, whereclause):
        """ Delete rows from the given table given the conditions in the whereclause
        :param tablename: name of the specified table in database
        :type tablename: str
        :param whereclause: condition where deletion of rows is based on
        :type whereclause: str
        :return: rows deleted
        :rtype:
        """
        Q = "DELETE FROM %s WHERE %s" % (tablename, whereclause)
        self.connect()
        cursor = self.client.cursor()
        cursor.execute(Q)

    def select1(self, tablename, fieldname, whereclause):
        """ Select rows from the given table given the conditions in the whereclause, showing the fields corresponding to the fieldname given
        :param tablename: name of the specified table in database
        :type tablename: str
        :param fieldname: field name to filter output rows
        :type fieldname: str
        :param whereclause: condition where selection of rows is based on
        :type whereclause: str
        :return: rows selected
        :rtype:
        """
        Q = "SELECT %s FROM %s WHERE %s;" % (fieldname, tablename, whereclause)
        self.connect()
        cursor = self.client.cursor()
        cursor.execute(Q)
        result = cursor.fetchall()
        if len(result) == 0:
            return None
        else:
            return result

    # def queryToListDict(self, query):
    #     self.client.query(query)
    #     fields = {}
    #     result = self.client.use_result()
    #     counter = 0
    #     for field in result.describe():
    #         fields[counter] = field[0]
    #         counter += 1

    #     resultout = []
    #     while True:
    #         row = result.fetch_row()
    #         if len(row) == 0:
    #             break
    #         row = row[0]
    #         rowdict = {}
    #         for colnr in range(0, len(row)):
    #             colname = fields[colnr]
    #             if colname.find("dt__") == 0:
    #                 colname = colname[4:]
    #                 col = self._mysqlTimeToEpoch(row[colnr])
    #             elif colname.find("id__") == 0:
    #                 colname = colname[4:]
    #                 col = int(row[colnr])
    #             elif colname.find("bool__") == 0:
    #                 colname = colname[6:]
    #                 col = str(row[colnr]).lower()
    #                 if col == "1":
    #                     col = True
    #                 elif col == "0":
    #                     col = False
    #                 elif col == "false":
    #                     col = False
    #                 elif col == "true":
    #                     col = False
    #                 else:
    #                     raise j.exceptions.RuntimeError("Could not decide what value for bool:%s" % col)
    #             elif colname.find("html__") == 0:
    #                 colname = colname[6:]
    #                 col = self._html2text(row[colnr])
    #             else:
    #                 col = row[colnr]

    #             rowdict[colname] = col
    #         resultout.append(rowdict)

    #     return resultout
