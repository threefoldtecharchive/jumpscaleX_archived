""" This module converts numbers to a best-fit string representation.
    Anyone familiar with "du -h" or "ls -lh" will recognise it immediately.

    Two versions are provided: one which does binary (Bytes) - this will
    return the number in powers of 2^10 (1024).  The other is decimal
    10^3 (1000).
"""

# each power goes up another suffix.  BASE^0: no suffix. BASE^1: K BASE^2: M
order = ["", "K", "M", "G", "T", "P", "E", "Z", "Y"]


class Sizes:
    """ converts numbers to power-of-10^3 representations.
        less than 1000: 1000.
        less than 1000000: divide by 1000, return "K" as the suffix.  etc.
    """

    _BASE = 1000.0

    __jslocation__ = "j.data_units.sizes"

    def toSize(self, value, input="", output="K"):
        """
        Convert value in other measurement
        """
        input = order.index(input)
        output = order.index(output)
        factor = input - output
        return value * (self._BASE ** factor)

    def converToBestUnit(self, value, input=""):
        divider = len(str(int(self._BASE))) - 1
        output = (len(str(value)) - 2) / divider
        output += order.index(input)
        if output > len(order):
            output = len(order) - 1
        elif output < 0:
            output = 0
        output = order[int(output)]
        return self.toSize(value, input, output), output


class Bytes(Sizes):
    """ converts numbers to power-of-2^2 representations (1024^0, 1024^1 ...)
    """

    _BASE = 1024.0

    __jslocation__ = "j.data_units.bytes"
