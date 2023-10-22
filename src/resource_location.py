from ctypes import *
from resource_key import *

class resource_location(Structure):
    _fields_ = [("field_0", resource_key),
                ("m_offset", c_int),
                ("m_size", c_int)
                ]

    def __repr__(self):
        return f'resource_location(field_0 = {self.field_0}, m_offset = {hex(self.m_offset)}, m_size = {hex(self.m_size)})'

assert(sizeof(resource_location) == 0x10)
