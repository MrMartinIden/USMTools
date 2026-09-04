from typing import *


class resource_pack_location(Structure):
    _fields_: ClassVar = (
                ("loc", resource_location),
                ("field_10", c_int),
                ("field_14", c_int),
                ("field_18", c_int),
                ("field_1C", c_int),
                ("prerequisite_offset", c_int),
                ("prerequisite_count", c_int),
                ("field_28", c_int),
                ("field_2C", c_int),
                ("m_name", c_char * 32),
                )
                
assert(sizeof(resource_pack_location) == 0x50)

