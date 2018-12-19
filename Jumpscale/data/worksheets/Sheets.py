
from Jumpscale import j
from .Sheet import *

JSBASE = j.application.JSBaseClass


class Sheets(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.worksheets"
        JSBASE.__init__(self)
        self.sheets = {}
        self.sheetsByCategory = {}
        self.sheetNames = []

    def sheet_new(self, name, nrcols=72, headers=[], period="M"):
        """
        @param period is M,Q or Y
        """
        return Sheet(name, nrcols=nrcols, headers=headers, period=period)
        

    def sheet_add(self, sheet, category=None):
        self.sheets[sheet.name] = sheet
        if category is not None:
            if category not in self.sheetsByCategory:
                self.sheetsByCategory[category] = []
            self.sheetsByCategory[category].append(sheet.name)
        self.sheetNames.append(sheet.name)

    def dict2sheet(self, data):
        sheet = Sheet("", nrmonths=72, headers=[])
        sheet.dict2obj(data)
        return sheet

    def aggregateSheets(self, sheetnames, rowdescr, category, aggregateSheetName="Total", aggregation={}):
        """
        @param sheetnames are the sheets to aggregate
        @param rowdescr {groupname:[rownames,...]}
        """
        sheettotal = self.new(name=aggregateSheetName, category=category)
        sheettotal.description = "sheet aggregation of %s" % category
        sheettotal.addRows(rowdescr, aggregation)
        sheets = []
        for name in sheetnames:
            sheets.append(self.sheets[name])
        for group in list(rowdescr.keys()):
            rownames = rowdescr[group]
            for rowname in rownames:
                for x in range(0, sheettotal.nrcols):
                    rowdest = sheettotal.rows[rowname]
                    sumvalue = 0.0
                    for sheet in sheets:
                        if sheet.rows[rowname].cells[x] is None:
                            raise j.exceptions.RuntimeError(
                                "could not aggregate sheet%s row:%s, found None value" % (sheet.name, rowname))
                        sumvalue += sheet.rows[rowname].cells[x]
                    rowdest.cells[x] = sumvalue
        return sheettotal

    def applyFunction(self, rows, method, rowDest=None, params={}):
        """
        @param rows is array if of rows we would like to use as inputvalues
        @param rowDest if empty will be same as first row
        @param method is python function with params (values,params) values are inputvalues from the rows
        """
        if rowDest == "":
            rowDest = rows[0]
        for colnr in range(rowDest.nrcols):
            input = []
            for row in rows:
                val = row.cells[colnr]
                if val is None:
                    val = 0.0
                input.append(val)
            rowDest.cells[colnr] = method(input, params)
        return rowDest

    def sumRows(self, rows, newRow):
        """
        make sum of rows
        @param rows is list of rows to add
        @param newRow is the row where the result will be stored
        """
        def sum(values, params):
            total = 0.0
            for value in values:
                total += value
            return total
        rows2 = []
        for row in rows:
            if row is not None:
                rows2.append(row)
        newRow = self.applyFunction(rows2, sum, newRow)
        return newRow

    def multiplyRows(self, rows, newRow):
        def mult(values, params):
            total = 1.0
            for value in values:
                total = total * value
            return total
        rows2 = []
        for row in rows:
            if row is not None:
                rows2.append(row)
        newRow = self.applyFunction(rows2, mult, newRow)
        return newRow

    def test(self):
        '''
        js_shell 'j.data.worksheets.test()'
        '''

        s=self.sheet_new("test")
        r=s.addRow("nrCU",groupname="units")
        r.setCell(posx=0,value=1,maxvalue=50)
        r.setCell(posx=10,value=10,maxvalue=50)
        r.setCell(posx=48,value=40,maxvalue=50)
        r.interpolate()

        r=s.addRow("nrSU",groupname="units")
        r.setCell(posx=0,value=1,maxvalue=60)
        r.setCell(posx=10,value=5,maxvalue=60)
        r.setCell(posx=48,value=20,maxvalue=60)
        r.interpolate()

        res=[4.0,8.0,11.0,15.0,19.0,22.0,26.0,29.0,33.0,36.0,40.0,43.0,47.0,50.0,54.0,58.0,60.0,60.0,60.0,60.0,60.0,60.0,60.0,60.0]
        assert r.aggregate("Q")==res

        r=s.addRow("unitsTotal",groupname="units")
        r0=s.sumRows(["nrCU","nrSU"],"unitsTotal")

        r1=s.addRow("nrNU",groupname="units")
        r1.text2row("2:100,5:200", standstill=5, defval=None,round=False, interpolate=True)

        r2=s.addRow("amount",groupname="price")
        r2.text2row("0:100mEGP,10:1k EUR", interpolate=True)

        # unit tests need to be non-interactive.  if an interactive
        # version is needed, make a test function named _interactive_test
        # which calls the other function
        #from IPython import embed;embed(colors='Linux')
