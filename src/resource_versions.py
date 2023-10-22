from ctypes import *

class resource_versions(Structure):
    _fields_ = [("field_0", c_int),
                ("field_4", c_int),
                ("field_8", c_int),
                ("field_C", c_int),
                ("field_10", c_int)]

assert(sizeof(resource_versions) == 0x14)
