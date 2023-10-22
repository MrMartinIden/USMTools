from ctypes import *
from string_hash import *

class tlresource_location(Structure):
    _fields_ = [("name", string_hash),
                ("type", c_char),
                ("offset", c_int)
                ]

    def get_type(self) -> int:
        return int.from_bytes(self.type, "little")

    def __repr__(self):
        return f'tlresource_location(name = {self.name}, type = {self.get_type()}, offset={hex(self.offset)})'

assert(sizeof(tlresource_location) == 0xC)

