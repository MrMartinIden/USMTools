from ctypes import *

class generic_mash_header(Structure):
    _fields_ = [("safety_key", c_int),
                ("field_4", c_int),
                ("field_8", c_int),
                ("class_id", c_short),
                ("field_E", c_short)
                ]

    def __repr__(self):
        return f'generic_mash_header(safety_key = {hex(self.safety_key)}, field_4={self.field_4}, field_8={hex(self.field_8)})'

    def generate_safety_key(self):
        return (self.field_8 + 0x7BADBA5D - (self.field_4 & 0xFFFFFFF) + self.class_id + self.field_E) & 0xFFFFFFF | 0x70000000

    def is_flagged(self, f: c_int):
        return (f & self.field_4) != 0

    def get_mash_data(self) -> c_char_p:
        return cast(this, c_char_p) + self.field_8

assert(sizeof(generic_mash_header) == 0x10)

