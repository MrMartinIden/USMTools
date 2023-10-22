import io
import os
import sys
from os import listdir
from os.path import isfile, join, dirname, splitext
from ctypes import *

sys.path.append(os.path.join(sys.path[0], 'src'))
from generic_mash_data_ptrs import *
from read_pcpack import *

class resource_pack_location(Structure):
    _fields_ = [("loc", resource_location),
                ("field_10", c_int),
                ("field_14", c_int),
                ("field_18", c_int),
                ("field_1C", c_int),
                ("prerequisite_offset", c_int),
                ("prerequisite_count", c_int),
                ("field_28", c_int),
                ("field_2C", c_int),
                ("m_name", c_char * 32)
                ]

assert(sizeof(resource_pack_location) == 0x50)

DEV_MODE = 1


def main(file):
    print()
    print(os.path.join('.', 'src'))
    name_pak, ext = splitext(file)

    if ext != ".PCPACK":
        return

    _, _, directory, buffer_bytes = read_pack(file)

    folder = name_pak
    try:
        os.mkdir(folder)
    except OSError:
        print ("Creation of the directory %s failed" % folder)
    else:
        print ("Successfully created the directory %s " % folder)

    for i in range(directory.resource_locations.size()):
        res_loc: resource_location = directory.get_resource_location(i)
        #print(res_loc)

        mash_data_size = res_loc.m_size
        resource_idx = directory.get_resource(res_loc)

        ndisplay = res_loc.field_0.get_platform_string()
        filepath = os.path.join(folder, ndisplay)
        filepath = ''.join(x for x in filepath if x.isprintable())
        resource_file = open(filepath, mode="wb")

        resource_data = buffer_bytes[resource_idx : resource_idx + mash_data_size]
        resource_file.write(resource_data)
        resource_file.close()

        print("range: {0:#X} {1:#x}".format(resource_idx, resource_idx + mash_data_size))

    print("\nDone.")


fileList = [
    f for f in listdir(dirname(__file__)) if isfile(join(dirname(__file__), f))
]

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        for file in fileList:
            main(file)

