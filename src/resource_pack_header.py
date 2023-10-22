from ctypes import *
from resource_versions import *

class resource_pack_header(Structure):
    _fields_ = [("field_0", resource_versions),
                ("field_14", c_int),
                ("directory_offset", c_int),
                ("res_dir_mash_size", c_int),
                ("field_20", c_int),
                ("field_24", c_int),
                ("field_28", c_int)
                ]

assert(sizeof(resource_pack_header) == 0x2C)

