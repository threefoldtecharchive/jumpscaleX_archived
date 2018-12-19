from libc.stdio cimport printf

# from libcpp.string cimport string

ctypedef unsigned char char_type

cdef char_type[:] _ustring(s):
    if isinstance(s, unicode):
        # encode to the specific encoding used inside of the module
        s = (< unicode > s).encode('utf8')
    return s


def echo():
    print("Hello World")

#
# def spam(i, char_type[:] s):
#
#     # cdef char_type[:] t
#     # t = _ustring(s)
#     ss = bytes(s).split("test")
#     # printf(bytes(ss))
#     return bytes(ss)
#     # print(s)
#     # print("%s_%s" % (s, i))
