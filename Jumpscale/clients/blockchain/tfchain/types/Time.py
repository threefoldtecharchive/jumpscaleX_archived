from Jumpscale import j

from datetime import datetime

"""
Time Utils, combing several Jumpscale types
"""

def parse_time_str(time_str):
    """
    If the string contains a prefix "+" character, it will be interpreted as a Jumpscale Duration,
    otherwise it is interpreted as a Jumpscale DateTime.

    :return int: epoch time seconds
    """
    if not isinstance(time_str, str):
        raise TypeError("time_str has to be a string, cannot be of type {}".format(type(time_str)))
    time_str = time_str.lstrip()
    if time_str[0] == "+":
        # interpret string as a duration
        offset = j.data.types.duration.fromString(time_str[1:])
        return int(datetime.now().timestamp()) + offset
    # interpret string as a datetime
    return j.data.types.datetime.fromString(time_str[1:])
