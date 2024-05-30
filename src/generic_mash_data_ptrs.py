from ctypes import *

class generic_mash_data_ptrs():

    def __init__(self, arg0, arg1):
        self.field_0 = arg0
        self.field_4 = arg1

    def rebase(self, i: int):
        v8 = i - self.field_0.tell() % i
        if v8 < i:
            self.field_0.seek(v8, 1)

    def get(self, t, num = 1):
        array_t = (t * num)
        newObj = array_t()

        newObj = array_t.from_buffer_copy(self.field_0.read(sizeof(array_t)))
        return newObj


    def __repr__(self):
        return f'generic_mash_data_ptrs(field_0 = {hex(self.field_0.tell())}, field_4 = {hex(self.field_4.tell())})'
