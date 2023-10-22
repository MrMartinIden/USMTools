from ctypes import *

class generic_mash_data_ptrs(Structure):
    _fields_ = [("field_0", c_int),
                ("field_4", c_int)
                ]

    def rebase(self, i: int):
        v8 = i - self.field_0 % i;
        if v8 < i:
            self.field_0 += v8;

    def __repr__(self):
        return f'generic_mash_data_ptrs(field_0 = {hex(self.field_0)}, field_4 = {hex(self.field_4)})'
