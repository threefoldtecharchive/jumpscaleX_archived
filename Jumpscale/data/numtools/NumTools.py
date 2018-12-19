from Jumpscale import j
import numpy
import struct
import math
JSBASE = j.application.JSBaseClass

class NumTools(JSBASE):

    __jslocation__ = "j.tools.numtools"

    def __init__(self):
        JSBASE.__init__(self)
        self.__imports__ = "numpy"
        self._currencies = {}

    @property
    def currencies(self):
        return j.clients.currencylayer.cur2usd

    def _getYearFromMonthId(self, monthid, startyear=0):
        """
        @param monthid is an int representing a month over
        a period of time e.g. month 24, is the 24th month
        """
        year = numpy.floor(float(monthid) / 12) + startyear
        return int(round(year))

    def getMonthsArrayForXYear(self, X, initvalue=None):
        """
        return array which represents all months of X year, each value = None
        """
        # create array for 36 months
        months = []
        for i in range(X * 12 + 1):
            months.append(initvalue)
        return months

    def getYearAndMonthFromMonthId(self, monthid, startyear=0):
        """
        @param monthid is an int representing a month over
        a period of time e.g. month 24, is the 24th moth
        @return returns year e.g. 1999 and month in the year
        """
        monthid = monthid - 1
        year = self._getYearFromMonthId(monthid)
        month = monthid - year * 12
        year += startyear
        return [year, month + 1]

    def roundDown(self, value, floatnr=0):
        value = value * (10 ** floatnr)
        return round(numpy.floor(value) / (10 ** floatnr), floatnr)

    def roundUp(self, value, floatnr=0):
        value = value * (10 ** floatnr)
        return round(numpy.ceil(value) / (10 ** floatnr), floatnr)

    def interpolateList(self, tointerpolate, left=0, right=None, floatnr=None):
        """
        interpolates a list (array)
        if will fill in the missing information of an array
        each None value in array will be interpolated
        """
        xp = []
        fp = []
        x = []
        isint = True
        allNone = True

        for x2 in tointerpolate:
            if x2 is not None:
                allNone = False
        if allNone:
            tointerpolate = [0.0 for item in tointerpolate]

        for xpos in range(len(tointerpolate)):
            if not tointerpolate[xpos] is None \
                and not j.data.types.int.check(
                    tointerpolate[xpos]):
                isint = False
            if tointerpolate[xpos] is None:
                x.append(xpos)
            if tointerpolate[xpos] is not None:
                xp.append(xpos)
                fp.append(tointerpolate[xpos])
        if len(x) > 0 and len(xp) > 0:
            result = numpy.interp(x, xp, fp, left, right)

            result2 = {}
            for t in range(len(result)):
                result2[x[t]] = result[t]
            result3 = []
            for xpos in range(len(tointerpolate)):
                if xpos in result2:
                    result3.append(result2[xpos])
                else:
                    result3.append(tointerpolate[xpos])
            if isint:
                result3 = [int(round(item, 0)) for item in result3]
            else:
                if floatnr is not None:
                    result3 = [round(float(item), floatnr) for item in result3]
                else:
                    result3 = [float(item) for item in result3]
        else:
            result3 = tointerpolate

        return result3

    def collapseDictOfArraysOfFloats(self, dictOfArrays):
        """
        format input {key:[,,,]}
        """
        result = []
        for x in range(len(dictOfArrays[keys()[0]])):
            result[x] = 0.0
            for key in list(dictOfArrays.keys()):
                result[x] += dictOfArrays[key][x]
        return result

    def collapseDictOfDictOfArraysOfFloats(self, data):
        """
        format input {key:{key:[,,,]},key:{key:[,,,]},...}
        """
        result = {}
        key1 = list(data.keys())[0]  # first element key
        key2 = list(data[key1].keys())[0]
        nrX = len(data[key1][key2])

        for x in range(nrX):
            for key in list(
                    data.keys()):  # the keys we want to ignore (collapse)
                datasub = data[key]
                for keysub in list(datasub.keys()):
                    if keysub not in result:
                        result[keysub] = []
                        for y in range(0, nrX):
                            result[keysub].append(0.0)
                    result[keysub][x] += datasub[keysub][x]
        return result

    def setMinValueInArray(self, array, minval):
        result = []
        for item in array:
            if item < minval:
                result.append(minval)
            else:
                result.append(item)
        return result

    def text2val(self, value, curcode="usd"):
        """
        value can be 10%,0.1,100,1m,1k  m=million
        USD/EUR/CH/EGP/GBP are also understood
        all gets translated to usd
        e.g.: 10%
        e.g.: 10EUR or 10 EUR (spaces are stripped)
        e.g.: 0.1mEUR or 0.1m EUR or 100k EUR or 100000 EUR


        j.tools.numtools.text2val("0.1mEUR")

        """
        d = j.data.types.numeric.str2bytes(value)
        return j.data.types.numeric.bytes2cur(d, curcode=curcode)

    def int_to_bitstring(self, val):
        """
        bitstring is like '10101011'
        """
        if j.data.types.int.check(val):
            bits = "{0:b}".format(val)
        else:
            raise RuntimeError("bits need to be an integer")

        while(len(bits)) < 8:
            bits = "0%s" % bits

        return bits

    def bitstring8_to_int(self, val):
        if not j.data.types.string.check(val):
            raise RuntimeError("bits need to be string")
        if len(val) != 8:
            raise RuntimeError("bitstring needs to be 8 char")
        return int(val, 2)

    def bitstring_set_bit(self, bits, pos=7):
        """
        bitstring is like '10101011'

        give bits as string of 8 chars or as int

        set a bit in the byte

        pos 7 means most left bit, 0 is most right bit (least value)

        """

        bitsnew = self.int_to_bitstring(int(math.pow(2, pos)))

        if not j.data.types.string.check(bits):
            bits = self.int_to_bitstring(bits)

        bits = int(bits, 2) | int(bitsnew, 2)

        return bits

    def bitstring_get_bit(self, bits, pos=7):
        """
        bitstring is like '10101011'

        give bits as string of 8 chars or as int

        get a bit in the byte

        pos 7 means most left bit, 0 is most right bit (least value)

        """

        if not j.data.types.string.check(bits):
            bits = self.int_to_bitstring(bits)

        bitsnew = self.int_to_bitstring(int(math.pow(2, pos)))

        res = int(bits, 2) & int(bitsnew, 2)

        return res > 0

    def listint_to_bin(self, llist, meta="00000000"):
        """
        convert list of integers to binary

        @PARM meta are the bits of a byte, the first one is reserved
        for short or long format, 1 if long format

        """
        shortFormat = True
        for item in llist:
            if item > 65535:
                shortFormat = False
                meta = self.bitstring_set_bit(meta, 7)
                break
        if shortFormat:
            meta = self.bitstring8_to_int(meta)

        bindata = b""
        if shortFormat:
            sformat = "<H"
        else:
            sformat = "<I"
        for item in llist:
            bindata += struct.pack(sformat, item)
        return struct.pack("<B", meta) + bindata

    def bin_to_listint(self, bindata):
        """
        for each 4 bytes convert to int
        """
        res = []
        if self.bitstring_get_bit(self.int_to_bitstring(bindata[0]), 7):
            # longformat
            sformat = "<I"
        else:
            sformat = "<H"

        bindata = bindata[1:]

        for item in struct.iter_unpack(sformat, bindata):
            res.append(item[0])
        return res

    def test(self):
        """
        js_shell 'j.tools.numtools.test()'
        """
        assert self.text2val("10k") == 10000.0

        assert (1 / self.currencies["egp"]
                ) * 10000000 == self.text2val("10 m egp")
        assert (1 / self.currencies["egp"]
                ) * 10000000 == self.text2val("10m egp")
        assert (1 / self.currencies["egp"]
                ) * 10000000 == self.text2val("10mEGP")

        assert self.int_to_bitstring(10) == '00001010'
        assert self.bitstring8_to_int('00001010') == 10

        assert self.bitstring_set_bit("00000000", 7) == 128
        assert self.bitstring_set_bit("00000000", 0) == 1

        assert self.bitstring_get_bit("00000000", 0) == False
        assert self.bitstring_get_bit(128, 7)
        assert self.bitstring_get_bit("00000001", 0)
        assert self.bitstring_get_bit("00000011", 1)
        assert self.bitstring_get_bit("00000011", 2) == False
        assert self.bitstring_get_bit("10000011", 7)
        assert self.bitstring_get_bit("00000011", 7) == False

        llist0 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        bbin = self.listint_to_bin(llist0)
        llist = self.bin_to_listint(bbin)
        assert llist == llist0
        assert len(bbin) == 21

        # now the binary struct will be double as big because there is 1 long
        # int in (above 65000)
        llist2 = [1, 2, 3, 400000, 5, 6, 7, 8, 9, 10]
        bbin2 = self.listint_to_bin(llist2)
        assert len(bbin2) == 41
        llist3 = self.bin_to_listint(bbin2)
        assert llist3 == llist2

        # max value in short format
        llist2 = [1, 2, 3, 65535, 5, 6, 7, 8, 9, 10]
        bbin2 = self.listint_to_bin(llist2)
        assert len(bbin2) == 21
        llist3 = self.bin_to_listint(bbin2)
        assert llist3 == llist2
