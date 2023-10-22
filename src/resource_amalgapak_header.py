from resource_versions import *

class resource_amalgapak_header(Structure):
    _fields_ = [("field_0", resource_versions),
                ("field_14", c_int),
                ("field_18", c_int),
                ("header_size", c_int),
                ("location_table_size", c_int),
                ("field_24", c_int),
                ("memory_map_table_size", c_int),
                ("field_2C", c_int),
                ("prerequisite_table_size", c_int),
                ("field_34", c_int)]

