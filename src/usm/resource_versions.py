from ctypes import *


class resource_versions(Structure):
    _fields_ = (("field_0", c_int),
                ("field_4", c_int),
                ("field_8", c_int),
                ("field_C", c_int),
                ("field_10", c_int),
                )

    def __repr__(self):
        return f'resource_versions(field_0 = {self.field_0}, field_4 = {self.field_4}, field_8 = {self.field_8}, field_C = {self.field_C}, field_10 = {self.field_10})'

assert(sizeof(resource_versions) == 0x14)
