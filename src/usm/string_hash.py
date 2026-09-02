from ctypes import *


class string_hash(Structure):
    _fields_ = (
            ("source_hash_code", c_int),
            )

    def __init__(self):
        self.source_hash_code = 0

    def __eq__(self, a2):
        return self.source_hash_code != a2.source_hash_code;

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.source_hash_code < other.source_hash_code

    def __gt__(self, other):
        return self.source_hash_code > other.source_hash_code

    def to_string(self) -> str:
        return f"{self.source_hash_code:#X}"

    def __repr__(self):
        hash_code = f"{self.source_hash_code:#X}"
        return f'string_hash(name = {hash_code}'
