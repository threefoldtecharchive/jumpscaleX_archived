from Jumpscale import j

JSBASE = j.application.JSBaseClass


class Row(j.application.JSBaseClass):
    def __init__(
        self,
        name="",
        ttype="float",
        nrcols=72,
        aggregate="T",
        description="",
        groupname="",
        groupdescr="",
        format="",
        defval="default",
        nrfloat=None,
    ):
        """
        @param ttype int,perc,float,empty,str,unknown
        @param aggregate= T,MIN,MAX,LAST,FIRST,AVG
        @format bold (if empty then normal)
        """
        self.name = name
        if defval == "default":
            if ttype == "float" or ttype == "perc" or ttype == "int":
                defval = 0.0
            if ttype == "empty":
                defval = ""

        self.cells = [defval for item in range(nrcols)]
        self.defval = defval

        self.ttype = ttype
        self.format = format
        self.description = description
        self.groupname = groupname
        self.groupdescr = groupdescr
        self.aggregateAction = aggregate
        self.nrfloat = nrfloat
        if aggregate not in ["T", "MAX", "MIN", "LAST", "FIRST", "AVG"]:
            raise j.exceptions.RuntimeError("Cannot find action:%s for agreggate" % self.aggregateAction)
        if ttype not in ["int", "perc", "float", "empty", "str", "unknown"]:
            raise j.exceptions.RuntimeError("only support format: int,perc,float,empty,str,unknown")
        self.nrcols = nrcols
        JSBASE.__init__(self)

    def setDefaultValue(self, defval=None, stop=None):
        if defval is None:
            defval = self.defval
        if defval is None:
            defval = 0.0
        if stop is None:
            stop = self.nrcols
        else:
            stop += 1
        for colid in range(0, int(stop)):
            if self.cells[colid] is None:
                self.cells[colid] = defval

    def indexation(self, yearlyIndexationInPerc, roundval=100):

        for year in range(2, 7):
            now = 12 * (year - 1)
            prev = 12 * (year - 2)
            self.cells[now] = self.cells[prev] * (1 + yearlyIndexationInPerc)
            self.setDefaultValue(0.0)
            self.round(roundval=roundval)
            self.makeGoHigher()

    def makeGoHigher(self):
        """
        make sure each cell of row is higher than previous cell
        """
        prev = 0
        for colid in range(0, self.nrcols):
            if self.cells[colid] < prev:
                self.cells[colid] = prev
            prev = self.cells[colid]

    def aggregate(self, period="Y"):
        """
        @param period is Q or Y (Quarter/Year)
        """

        def calc(months):

            if self.aggregateAction == "LAST":
                return self.cells[months[-1]]
            if self.aggregateAction == "FIRST":
                return self.cells[months[0]]
            result = 0.0
            if self.aggregateAction == "MIN":
                result = 9999999999999999999
            for m in months:
                val = self.cells[m]
                if val is None:
                    raise j.exceptions.RuntimeError(
                        "Cannot aggregrate row %s from group %s,\n%s" % (self.name, self.groupname, self.cells)
                    )
                if self.aggregateAction == "T" or self.aggregateAction == "AVG":
                    result += val
                if self.aggregateAction == "MIN":
                    if (val < 0 and val < result) or (val > 0 and val > result):
                        result = val
                if self.aggregateAction == "MAX":
                    if (val > 0 and val > result) or (val < 0 and val < result):
                        result = val
            if self.aggregateAction == "AVG":
                result = result / len(months)
            return result

        # monthAttributes=[item.name for item in self.months[1].JSModel_MODEL_INFO.attributes]
        if period == "Y":
            result = [0.0 for item in range(6)]
            for year in range(1, 7):
                months = [12 * (year - 1) + i for i in range(12)]
                # name=self._getYearStringFromYearNr(year)
                result[year - 1] = calc(months)
        if period == "Q":
            result = [0.0 for item in range(6 * 4)]
            for quarter in range(1, 4 * 6 + 1):
                months = [3 * (quarter - 1) + i for i in range(3)]
                # name=self._getYearStringFromYearNr(year)
                result[quarter - 1] = calc(months)
        return result

    def interpolate(self, start=None, stop=None, variation=0, min=None, max=None):
        """
        @param random if 5 means will put 5% variation on it while interpolating
        """
        # tointerpolate=[]
        # for item in self.cells:
        # if item==0.0:
        # item=None
        # tointerpolate.append(item)
        if start is None:
            start = 0
        if stop is None:
            stop = len(self.cells) - 1
        tointerpolate = self.cells[start : stop + 1]
        try:
            interpolated = j.tools.numtools.interpolateList(tointerpolate, floatnr=self.nrfloat)
        except Exception as e:
            self._log_error(("could not interpolate row %s" % self.name))
            self._log_error("DEBUG NOW cannot interpolate, explore self & tointerpolate")
        xx = 0
        for x in range(start, stop + 1):
            self.cells[x] = interpolated[xx]
            xx += 1

        self.randomVariation(variation, min=min, max=max)

    def randomVariation(self, variation, start=None, stop=None, min=None, max=None):
        if variation == 0:
            return
        if start is None:
            start = 0
        if stop is None:
            stop = len(self.cells) - 1
        # variation=float(self.getMax())/100*float(random)
        variation = int(float(variation) * 100.0)
        roundd = self.ttype in ["perc", "int"]
        for x in range(start, stop + 1):
            self.cells[x] = (
                self.cells[x] - variation / 200 + float(j.data.idgenerator.generateRandomInt(1, variation)) / 100
            )
            if roundd:
                self.cells[x] = int(self.cells[x])

    def complete(self, start, vvariation=0.2, hvariation=0, minvalue=0, maxvalue=100, lastpos=70):
        """
        will copy beginning of row with certain variation to rest of row
        will start doing that from mentioned startpoint
        @param hvariation not implemented
        """
        stop = len(self.cells) - 1
        blocksize = start - 1
        halt = False
        x = start
        while halt is False:
            for xInBlock in range(0, blocksize + 1):
                x += 1
                xorg = xInBlock
                if x > self.nrcols:
                    halt = True
                    self.setCell(self.nrcols - 1, lastpos, minvalue, maxvalue)
                    break
                if self.cells[xorg] is not None:
                    val = self.cells[xorg]
                    val = val + self._getVariationRelative(vvariation, val)
                    self.setCell(x, val, minvalue, maxvalue)

    def setCell(self, posx, value, minvalue=None, maxvalue=None):
        if minvalue is not None and value < minvalue:
            value = minvalue
        if maxvalue is not None and value > maxvalue:
            value = maxvalue
        if posx > self.nrcols - 1:
            self._log_debug(("out of range: x:%s y:%s" % (posx, value)))
            return None, None
        self.cells[posx] = value
        return posx, value

    def _getVariationAbsoluteInt(self, val, variation):
        variation = int(variation)
        changeMin = int(val - variation)
        changeMax = int(val + variation)
        gd = j.data.idgenerator.generateRandomInt(changeMin, changeMax)
        return gd

    def _getVariationPositive(self, change, variation):
        change = float(change)
        if change < 0:
            raise j.exceptions.RuntimeError("change needs to be positive")
        variation = float(variation)
        if variation < 0 or variation > 1:
            raise j.exceptions.RuntimeError("Variation cannot be more than 1 and not less than 0.")
        changeMin = int(100.0 * (change - variation * change))
        changeMax = int(100.0 * (change + variation * change))
        gd = float(j.data.idgenerator.generateRandomInt(changeMin, changeMax) / 100.0)
        return gd

    def goDown(self, start, stop, godown, nrSteps, hvariation, vvariation, isActiveFunction=None):
        start = int(start)
        stop = int(stop)
        blocksize = float(stop + 1 - start) / float(nrSteps)
        runNr = 0
        if start > self.nrcols:
            return start, None
        y = self.cells[start]  # start height
        if y is None:
            raise j.exceptions.RuntimeError("start position y needs to is not None")
        y = float(y)
        minvalue = y - godown
        if minvalue < 0:
            raise j.exceptions.RuntimeError("Minvalue in go down can not be < 0")
        godown = float(godown) / float(nrSteps)
        maxvalue = y - 1
        while True:
            runNr += 1
            start2 = start + blocksize * (runNr)
            if isActiveFunction is not None:
                if not isActiveFunction(start2):
                    stop += int(blocksize)
                    continue
            x = self._getVariationAbsoluteInt(start2, hvariation)
            y = y - self._getVariationPositive(godown, vvariation)
            y2 = y
            if x > stop:
                return self.setCell(stop, y)
            x, y = self.setCell(x, y, minvalue, maxvalue)
            if y is None:
                self.setCell(self.nrcols - 1, y2)
                return x, y2

    def goUp(self, start, stop, goup, nrSteps, hvariation, vvariation, isActiveFunction=None):
        start = int(start)
        stop = int(stop)
        blocksize = float(stop + 1 - start) / float(nrSteps)
        runNr = 0
        if start > self.nrcols:
            return start, None
        y = self.cells[start]  # start height
        if y is None:
            raise j.exceptions.RuntimeError("start position y needs to is not None")
        y = float(y)
        minvalue = y
        if minvalue < 0:
            raise j.exceptions.RuntimeError("Minvalue in go up can not be < 0")
        maxvalue = y + goup
        goup = float(goup) / float(nrSteps)
        while True:
            runNr += 1
            start2 = start + blocksize * (runNr)
            if isActiveFunction is not None:
                if not isActiveFunction(start2):
                    stop += int(blocksize)
                    continue
            x = self._getVariationAbsoluteInt(start2, hvariation)
            y = y + self._getVariationPositive(goup, vvariation)
            y2 = y
            if x > stop:
                return self.setCell(stop, y)
            x, y = self.setCell(x, y, minvalue, maxvalue)
            if y is None:
                self.setCell(self.nrcols - 1, y2)
                return x, y

    def getMax(self, start=None, stop=None):
        if start is None:
            start = 0
        if stop is None:
            stop = len(self.cells) - 1
        r = 0
        for x in range(start, stop + 1):
            if self.cells[x] > r:
                r = self.cells[x]
        return r

    def checkFilledIn(self, start, stop):
        for x in range(start, stop + 1):
            if start < 0:
                continue
            if self.cells[x] is not None:
                return True
        return False

    def _roundNrCumul(self, val, x, args):
        nr = val
        if nr is None:
            nr = 0.0
        if nr + self._cumul > 0.5 and nr + self._cumul < 10:
            self._cumul = nr + self._cumul
            nr2 = j.tools.numtools.roundDown(self._cumul * 2, 0) / 2
            self._cumul += nr - nr2
            self._cumul = self._cumul - nr2
            return nr2
        elif nr + self._cumul == 0.5:
            self._cumul = 0.0
            return 0.5
        elif nr + self._cumul < 0.5:
            self._cumul += nr
            return 0
        elif nr + self._cumul >= 10:
            nr2 = j.tools.numtools.roundDown(nr, 0)
            self._cumul += nr - nr2
            return nr2
        else:
            raise j.exceptions.RuntimeError("error in normalizing, should not get here")
        return nr

    def applyFunction(self, ffunction, args={}):
        """
        call ffunction with params (val of cell, x, args as dict)
        row gets modified
        """
        for x in range(0, self.nrcols):
            self.cells[x] = ffunction(self.cells[x], x, args)

    def text2row(self, data, standstill=0, defval=None, round=False, interpolate=False):
        """
        convert string format 2:100,5:200 to row (month 2=100, ...)

        values can be 10%,0.1,100,1m,1k  m=million USD/EUR/CH/EGP/GBP are also understood

        result will be put into the given row
        data kan be 1 string or list
        if list then list need to be of length len(row)/12 so is a value per year
        standstill is first X nr of months which are made 0

        e.g. data="2:100,5:200"

        """

        def custom2rowvalues(data):
            if str(data).find(",") == -1 and str(data).find(":") == -1:
                raise j.exceptions.Base("not properly formatted needs to be 5:1,10:2")
            data = data.replace("'", "").strip()
            splitted = data.split(",")
            for item in splitted:
                if len(item.split(":")) != 2:
                    raise j.exceptions.RuntimeError(
                        "text2row input not properly formatted: %s, subpart: %s" % (data, item)
                    )
                pos, value = item.split(":")
                pos = int(pos)
                try:
                    value = j.tools.numtools.text2val(value)
                except Exception as e:
                    out = "error: %s \n" % e
                    out += "error in parsing input data for %s\n" % value
                    out += "error in element %s\n" % data
                    out += "row:%s\n" % self.name
                    raise j.exceptions.Base(out)
                self.cells[pos] = value

        if defval is not None:
            self.defval = defval

        if standstill > 0:
            for x in range(0, standstill):
                self.cells[x] = self.defval

        if not j.data.types.string.check(data):
            raise j.exceptions.Base("needs to be string")

        if str(data).find(",") == -1 and str(data).find(":") == -1:
            # is only 1 value so set all data
            if str(data).strip() == "" or data is None:
                data = "0.0"
            self.setDefaultValue(float(data))
        else:
            custom2rowvalues(data)

        if interpolate:
            self.interpolate()

        self.setDefaultValue()

        if self.ttype == "int":
            self.round(0, 0)

        if round:
            self._cumul = 0.0
            self.applyFunction(self._roundNrCumul)

    def recurring(self, row, delay, start, churn, nrmonths):
        """
        @param row is the row we will fill in with recurring calc
        @param start value to start with at month 0 (is first month)
        @param churn 2 means 2% churn
        @param delay is different beween selling & being active
        """
        if churn == "1000%":
            row.setDefaultValue(0.0)
            return row
        delay = int(round(delay, 0))
        for delaynr in range(0, delay):
            row.cells[delaynr] = start
        for colid in range(0, int(self.nrcols)):
            nractive = float(start)
            if (colid - int(nrmonths)) < 0:
                start2 = 0
            else:
                start2 = colid - int(nrmonths)
            for monthprevid in range(start2, colid + 1):
                nractive += float(self.cells[monthprevid]) * ((1 - float(churn) / 12) ** (colid - monthprevid))
            if colid + delay < row.nrcols:
                row.cells[colid + delay] = nractive

        row.round()
        return row

    def round(self, nrfloat=None, roundval=None):
        """
        @param roundval if e.g. 10 means round will be done with values of 10
            nr float will then be 0 (automatically)
        """
        if nrfloat is None:
            nrfloat = self.nrfloat
        if roundval > 0:
            nrfloat = 0

        for colid in range(0, int(self.nrcols)):
            if self.cells[colid] is not None:
                if roundval > 0:
                    self.cells[colid] = round(self.cells[colid] / roundval, nrfloat) * roundval
                if self.ttype == "int":
                    self.cells[colid] = int(round(self.cells[colid], nrfloat))
                elif self.ttype == "float":
                    self.cells[colid] = round(self.cells[colid], nrfloat)

    def areCosts(self):
        """
        negate the values in the row
        """
        for colid in range(0, int(self.nrcols)):
            if self.cells[colid] > 0:
                self.cells[colid] = -self.cells[colid]

    def invert(self):
        """
        invert + becomes - and reverse
        """
        for colid in range(0, int(self.nrcols)):
            self.cells[colid] = -self.cells[colid]

    def delay(self, delay=0, defval=None):
        if defval is not None:
            self.defval = defval
        delay = int(delay)
        out = [0.0 for item in range(self.nrcols)]
        nrmax = self.nrcols
        if delay > 0:
            for i in range(delay):
                out[i] = self.defval
        delayed = 0.0
        if delay < 0:
            for i in range(-delay + 1):
                delayed += self.cells[i]
        i = delay
        for cell in self.cells:
            if i < nrmax and i > -1:
                out[i] = cell
            i += 1
        i = 0
        if delay < 0:
            out[0] += delayed
        self.cells = out

    def __str__(self):
        if self.nrcols > 18:
            l = 18
        else:
            l = self.nrcols
        result = [self.name]
        result.extend([self.cells[col] for col in range(l)])
        return str(result)

    __repr__ = __str__

    def _dict2obj(self, dict):
        self.name = dict["name"]
        self.cells = dict["cells"]
        self.ttype = dict["ttype"]
        self.format = dict["format"]
        self.description = dict["description"]
        self.groupname = dict["groupname"]
        self.groupdescr = dict["groupdescr"]
        self.aggregateAction = dict["aggregateAction"]
        self.nrcols = dict["nrcols"]
        self.nrfloat = dict["nrfloat"]
        return self
