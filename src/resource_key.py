import io
from ctypes import *
from string_hash import *


def tohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))


string_hash_dictionary = {}
try:
    with io.open("string_hash_dictionary.txt", mode="r") as dictionary_file:
        for i, line in enumerate(dictionary_file):
            if i > 1:

                arr = line.split()
                #print(line)

                if len(arr) != 2:
                    continue

                h = int(arr[0], 16)
                string_hash_dictionary[h] = arr[1]

        keys = string_hash_dictionary.keys()
        #print(type(keys))

except IOError:
    input("Could not open file!")

assert(len(string_hash_dictionary) != 0)


resource_key_type_ext = [".NONE", ".PCANIM", ".PCSKEL", ".ALS", ".ENT", ".ENTEXT", ".DDS", ".DDSMP", ".IFL", ".DESC", ".ENS", ".SPL", ".AB", ".QP", ".TRIG", ".PCSX", ".INST", ".FDF", ".PANEL", ".TXT", ".ICN",
                            ".PCMESH", ".PCMORPH", ".PCMAT", ".COLL", ".PCPACK", ".PCSANIM", ".MSN", ".MARKER", ".HH", ".WAV", ".WBK",
                            ".M2V", "M2V", ".PFX", ".CSV", ".CLE", ".LIT", ".GRD", ".GLS", ".LOD", ".SIN",
                            ".GV", ".SV", ".TOKENS", ".DSG", ".PATH", ".PTRL", ".LANG", ".SLF", ".VISEME", ".PCMESHDEF", ".PCMORPHDEF", ".PCMATDEF", ".MUT", ".ASG", ".BAI", ".CUT", ".INTERACT", ".CSV", ".CSV", "._ENTID_", "._ANIMID_", "._REGIONID_", "._AI_GENERIC_ID_", "._RADIOMSG_", "._GOAL_", "._IFC_ATTRIBUTE_", "._SIGNAL_", "._PACKGROUP_",
                        ]
assert(resource_key_type_ext[25] == ".PCPACK")
assert(resource_key_type_ext[48] == ".LANG")
assert(resource_key_type_ext[49] == ".SLF")

class resource_key(Structure):
    _fields_ = [("m_hash", string_hash),
                ("m_type", c_int)
                ]

    def is_set(self):
        undefined = string_hash()
        return self.m_hash != undefined

    def get_type(self):
        return self.m_type

    def get_platform_ext(self) -> str:
        return resource_key_type_ext[self.m_type]

    def get_platform_string(self) -> str:
        h = int(tohex(self.m_hash.source_hash_code, 32), 16)
        name = string_hash_dictionary.get(h, tohex(self.m_hash.source_hash_code, 32))
        ext = self.get_platform_ext()
        return (name + ext)

    def __repr__(self):
        return f'resource_key(m_hash = {self.m_hash}, m_type = {self.m_type}) => {self.get_platform_string()}'
