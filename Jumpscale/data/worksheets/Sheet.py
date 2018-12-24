
from Jumpscale import j
from .Row import *

JSBASE = j.application.JSBaseClass


class Sheet(j.builder._BaseClass):

    def __init__(self, name, nrcols=72, headers=[], period="M"):
        """
        @param period is M,Q or Y
        """
        JSBASE.__init__(self)
        self.name = name
        self.description = ""
        self.nrcols = nrcols
        self.remarks = ""
        self.period = period  # M, Q or Y

        if headers == []:
            self.headers = [item + 1 for item in range(nrcols)]
        else:
            self.headers = headers
            self.nrcols = len(self.headers)

        self.rows = {}
        self.rowNames = []

    # def _obj2dict(self):
        # ddict={}
        # ddict["name"]=self.name
        # ddict["headers"]=self.headers
        # ddict["nrcols"]=self.nrcols
        #ddict["rows"]=[item.obj2dict() for item in self.rows]
        # return ddict

    def _dict2obj(self, dict):
        self.name = dict["name"]
        self.headers = dict["headers"]
        self.nrcols = dict["nrcols"]
        slf.period = dict["period"]
        for key in list(dict["rows"].keys()):
            item = dict["rows"][key]
            row = j.tools.code.dict2object(Row(), item)
            self.rows[row.name] = row

    def addRow(
            self,
            name,
            ttype="float",
            aggregate="T",
            description="",
            groupname="",
            groupdescr="",
            nrcols=None,
            format="",
            values=[],
            defval=None,
            nrfloat=None):
        """
        @param ttype int,perc,float,empty,str
        @param aggregate= T,A,MIN,MAX
        @param values is array of values to insert
        @param defval is default value for each col
        @param round is only valid for float e.g. 2 after comma
        """
        if nrcols is None:
            nrcols = self.nrcols
        if ttype == "float" and nrfloat is None:
            nrfloat = 2
        row = Row(name, ttype, nrcols, aggregate, description=description, groupname=groupname,
                  groupdescr=groupdescr, format=format, defval=defval, nrfloat=nrfloat)
        self.rows[name] = row
        self.rowNames.append(name)
        if values != []:
            for x in range(nrcols):
                self.setCell(name, x, values[x])
        return self.rows[name]

    # def renting(self,row,interest,nrmonths):
    # DOES NOT WORK, JUST COPY PASTE TO START DOING IT
        #"""
        #@param row is the row in which we need to fill in
        #@param start value to start with at month 0 (is first month)
        #@param churn 2 means 2% churn
        #@param delay is different beween selling & being active
        #"""
        # print "churn:%s" % churn
        # if churn=="1000%":
        # row.setDefaultValue(0.0)
        # return row
        # delay=int(round(delay,0))
        # for delaynr in range(0,delay):
        # row.cells[delaynr]=start
        # for colid in range(0,int(self.nrcols)):
        # nractive=float(start)
        # if (colid-int(nrmonths))<0:
        # start2=0
        # else:
        # start2=colid-int(nrmonths)
        # for monthprevid in range(start2,colid+1):
        # nractive+=float(self.cells[monthprevid])*((1-float(churn)/12)**(colid-monthprevid))
        # if colid+delay<row.nrcols:
        # row.cells[colid+delay]=nractive

        # row.round()
        # return row

    def aggregate(self, rownames=[], period="Y"):
        """
        @param rownames names of rows to aggregate
        @param period is Q or Y (Quarter/Year)
        """
        rows = []
        header = [""]
        headerDone = False
        if rownames == []:
            rownames = self.rowNames

        for rowName in rownames:
            row = [rowName]
            row2 = self.getRow(rowName)
            result = row2.aggregate(period)
            for key in range(len(result)):
                if headerDone is False:
                    if period == "Y":
                        hid = "Y%s" % int(key + 1)
                    else:
                        year = j.tools.numtools.roundDown(float(key) / 4)
                        Q = "Q%s" % int(j.tools.numtools.roundDown(float(key - 1 - year * 4)) + 2)
                        year = "Y%s" % int(year + 1)
                        hid = "%s %s" % (year, Q)
                    header.append(hid)
                row.append(result[key])
            headerDone = True
            rows.append(row)

        return rows, header

    def copyFrom(self, sheets, sheetname, rowname, newRowName, newGroupName):
        """
        @param sheets if None then this sheetobject
        """
        if sheets is None:
            sheetfrom = self
        else:
            sheetfrom = sheets.sheets[sheetname]
        rowfrom = sheetfrom.rows[rowname]
        newrow = self.addRow(newRowName, groupname=newGroupName)
        newrow.aggregateAction = rowfrom.aggregateAction
        newrow.nrfloat = rowfrom.nrfloat
        # newrow.groupname=rowfrom.groupname
        newrow.ttype = rowfrom.ttype
        newrow.format = rowfrom.format
        for x in range(0, rowfrom.nrcols):
            newrow.cells[x] = rowfrom.cells[x]
        return newrow

    def getSheetAggregated(self, period="Y"):
        """
        @param period is Q or Y (Quarter/Year)
        """
        rows, headers = self.aggregate(period=period)
        lenx = len(headers) - 1
        sheet2 = j.tools.sheet.new(self.name, self.nrcols, headers)
        sheet2.description = self.description
        sheet2.remarks = self.remarks
        sheet2.period = period
        for row in rows:
            roworg = roworg = self.getRow(row[0])
            rownew = sheet2.addRow(
                roworg.name,
                roworg.ttype,
                roworg.aggregateAction,
                roworg.description,
                roworg.groupname,
                roworg.groupdescr,
                lenx,
                roworg.format,
                nrfloat=roworg.nrfloat)
            if roworg.ttype == "float":
                rownew.ttype = "int"
                rownew.nrfloat = 0

            rownew.description = roworg.description
            for x in range(0, lenx):
                rownew.cells[x] = row[x + 1]
            rownew.round()
        return sheet2

    def getRow(self, rowName):
        if rowName not in self.rows:
            raise j.exceptions.RuntimeError("Cannot find row with name %s" % rowName)
        return self.rows[rowName]

    def getCell(self, rowName, month):
        row = self.getRow(rowName)
        return row.cells[int(month)]

    def setCell(self, rowName, month, value):
        if month > self.nrcols - 1:
            raise ValueError("max month = %s, %s given" % (self.nrcols - 1, month))
        row = self.getRow(rowName)

        row.cells[month] = value

    def addCell(self, rowName, month, value):
        if month > self.nrcols - 1:
            raise ValueError("max month = %s, %s given" % (self.nrcols - 1, month))
        row = self.getRow(rowName)
        row.cells[month] += value

    def interpolate(self, rowname):
        row = self.getRow(rowname)
        row.interpolate()
        return row

    # def delay(self,rowName,delay=0,defValue=0.0,copy2otherRowName=None):
        # delay=int(delay)
        #out=[0.0 for item in range(self.nrcols)]
        # nrmax=self.nrcols
        # for i in range(delay):
        # out[i]=defValue
        # i=delay
        # row=self.getRow(rowName)
        # for cell in row.cells:
        # if i<nrmax:
        # out[i]=cell
        # else:
        # break
        # i+=1
        # i=0
        # if copy2otherRowName is not None:
        # check if row already exists
        # if not self.rows.has_key(copy2otherRowName):
        # self.addRow(copy2otherRowName,"float")
        # dest=copy2otherRowName
        # else:
        # dest=rowName

        # for month in range(self.nrcols):
        # self.setCell(dest,month,out[month])

        # return self.rows[dest]

    def accumulate(self, rowNameInput, rowNameDest):
        """
        add previous month on top of current and keep on adding (accumulating)
        @param rowNameInput is name of row we would like to aggregate
        @param rowNameDest if empty will be same as rowNameInput1
        """
        previous = 0
        for colnr in range(self.nrcols):
            input = self.getCell(rowNameInput, colnr)
            self.setCell(rowNameDest, colnr, input + previous)
            previous = self.getCell(rowNameDest, colnr)
        return self.rows[rowNameDest]

    def setDefaultValue(self, rowNameInput, defval=0.0):
        """
        add previous month on top of current and keep on adding (accumulating)
        @param rowNameInput is name of row we would like to aggregate
        """
        previous = 0
        for colnr in range(self.nrcols):
            input = self.getCell(rowNameInput, colnr)
            if input is None:
                self.setCell(rowNameInput, colnr, defval)
        return self.rows[rowNameInput]

    def applyFunction(self, rowNames, method, rowNameDest="", params={}):
        """
        @param rowNames is array if names of row we would like to use as inputvalues
        @param rowNameDest if empty will be same as first rowName
        @param method is python function with params (sheet,**input) returns the result
            input is dict with as key the arguments & the keys of params (so all collapsed in same input dict)
        """
        if rowNameDest == "":
            rowNameDest = rowNames[0]
        if rowNameDest not in self.rows:
            self.addRow(rowNameDest, "float")
        for colnr in range(self.nrcols):
            input = {}
            for name in rowNames:
                input[name] = self.getCell(name, colnr)
                if input[name] is None:
                    input[name] = 0.0
            for key in params:
                input[key] = params[key]
            self.setCell(rowNameDest, colnr, method(**input))
        return self.rows[rowNameDest]

    def getColumnsWidth(self):
        def getwidth(value):
            width = 0
            if value < 0:
                width += 1
                valuepos = -value
            else:
                valuepos = value
            if valuepos < 1000:
                pass
            elif valuepos < 1000000:
                width += 1
            elif valuepos < 1000000000:
                width += 2
            elif valuepos < 1000000000000:
                width += 3
            if valuepos < 1 and round(valuepos) != valuepos:
                width += 3
            elif valuepos < 10 and round(valuepos) != valuepos:
                width += 2
            valueposround = int(round(valuepos))
            width += len(str(valueposround))
            return width

        cols = {}
        for key in list(self.rows.keys()):
            row = self.rows[key]
            for colnr in range(0, len(row.cells)):
                if colnr not in cols:
                    cols[colnr] = 0
                w = getwidth(row.cells[colnr])
                if w > cols[colnr]:
                    cols[colnr] = w
        return cols

    def addRows(self, rows2create, aggregation):
        """
        @para rows2create {groupname:[rownames,...]}
        """
        for group in list(rows2create.keys()):
            rownames = rows2create[group]
            for rowname in rownames:
                if rowname in aggregation:
                    aggr = aggregation[rowname]
                else:
                    aggr = "T"
                rowx = self.addRow(rowname, description="", nrfloat=1, aggregate=aggr)
                rowx.groupname = group

    def applyFunctionOnValuesFromRows(self, rownames, method, rowDest, params={}):
        """
        @param rows is array if of rows we would like to use as inputvalues
        @param rowDest if empty will be same as first row
        @param method is python function with params (values,params) values are inputvalues from the rows
        """
        for colnr in range(rowDest.nrcols):
            input = []
            for rowname in rownames:
                val = self.getCell(rowname, colnr)
                if val is None:
                    val = 0.0
                input.append(val)

            rowDest.cells[colnr] = method(input, params)
        return rowDest

    def sumRows(self, rownames, newRow):
        """
        make sum of rows
        @param rownames is list of rows to add specified by list or rownames
        @param newRow is the row where the result will be stored (can also be the name of the new row then row will be looked for)
        """
        if j.data.types.string.check(newRow):
            newRow = self.getRow(newRow)

        def summ(values, params):
            total = 0.0
            for value in values:
                total += value
            return total
        newRow = self.applyFunctionOnValuesFromRows(rownames, summ, newRow)
        return newRow

    def multiplyRows(self, rownames, newRow):
        """
        make procuct of rows
        @param rownames is list of rows to add specified by list or rownames
        @param newRow is the row where the result will be stored (can also be the name of the new row then row will be looked for)
        """
        if j.data.types.string.check(newRow):
            newRow = self.getRow(newRow)

        def mult(values, params):
            total = 1.0
            for value in values:
                total = total * value
            return total

        newRow = self.applyFunctionOnValuesFromRows(rownames, mult, newRow)
        return newRow

    def __str__(self):
        result = ""
        for row in self.rows:
            result += "%s\n" % row
        return result

    __repr__ = __str__


