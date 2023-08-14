import io
import shutil
import os
from os import listdir
from os.path import isfile, join, dirname, splitext
from ctypes import *

fileList = [ 
    f for f in listdir(dirname(__file__)) if isfile(join(dirname(__file__), f))
]

class resource_versions(Structure):
    _fields_ = [("field_0", c_int),
                ("field_4", c_int),
                ("field_8", c_int),
                ("field_C", c_int),
                ("field_10", c_int)]
                
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

assert(sizeof(resource_versions) == 0x14)

class string_hash(Structure):
    _fields_ = [("field_0", c_int)]

class resource_key(Structure):
    _fields_ = [("m_hash", string_hash),
                ("m_type", c_int)
                ]

class resource_location(Structure):
    _fields_ = [("field_0", resource_key),
                ("field_8", c_int),
                ("m_size", c_int)
                ]


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

#Header_Section 0x38
#LBA_Section 0xBFE0
#FileData Individual Section 0x50

DEV_MODE = 1

for file in fileList:
    _, ext = splitext(file)
    if ext == ".PAK":
        print("Resource pack:", file)
        with io.open(file, mode="rb") as rPack:
            rPack.seek(0, 2)
            numOfBytes = rPack.tell()
            print("Total Size:", numOfBytes, "bytes")
            
            rPack.seek(0, 0)
            pack_file_header = resource_amalgapak_header()
            rPack.readinto(pack_file_header)
            
            rpVersion = pack_file_header.field_0.field_0
            
            #Header Section Size
            headerSize = pack_file_header.header_size
            
            #LBA_SECTION
            location_table_size = pack_file_header.location_table_size

            if rpVersion == 14:
                print("Game: Ultimate Spider-Man NTSC 1.0")
            elif rpVersion == 10:
                print("Game: Ultimate Spider-Man NTSC 06/20/2005 Prototype")

            base_offset = pack_file_header.field_18

            if DEV_MODE == 1:
                print("\nDeveloper info:\n")
                
                versions = pack_file_header.field_0
                print("RESOURCE_PACK_VERSION", versions.field_0)
                print("RESOURCE_ENTITY_MASH_VERSION", versions.field_4)
                print("RESOURCE_NOENTITY_MASH_VERSION", versions.field_8)
                print("RESOURCE_AUTO_MASH_VERSION", versions.field_C)
                print("RESOURCE_RAW_MASH_VERSION", versions.field_10)
                
                print("base_offset:", hex(base_offset))
                
                print("Header Section Size:", hex(headerSize), "bytes")
                print("LBA Section Size:", hex(location_table_size), "bytes")

            #Read LBA
            amalgapak_pack_location_table_t = resource_pack_location * int(location_table_size / 0x50)
            amalgapak_pack_location_table = amalgapak_pack_location_table_t()
            rPack.readinto(amalgapak_pack_location_table)
            
            amalgapak_pack_location_count = len(amalgapak_pack_location_table)
            print(amalgapak_pack_location_count, "Files detected")

            folder = "resourcepack"
            try:
                os.mkdir(folder)
            except OSError:
                print ("Creation of the directory %s failed" % folder)
            else:
                print ("Successfully created the directory %s " % folder)
                
            for fileIndex in range(amalgapak_pack_location_count):
                pack_loc = amalgapak_pack_location_table[fileIndex]
                ndisplay = pack_loc.m_name.decode('utf-8')
                print(ndisplay)
                offset_loc = pack_loc.loc.field_8
                filesize = pack_loc.loc.m_size
                
                filepath = os.path.join(folder, ndisplay + ".XBPACK")
                filepath = ''.join(x for x in filepath if x.isprintable())
                
                rPack.seek(base_offset + offset_loc, 0)
                
                filePos = rPack.tell()
                print(filepath, hex(filePos))
                
                nfldata = rPack.read(filesize)
                nflfile = open(filepath, mode="wb")
                nflfile.write(nfldata)
                nflfile.close()
            

print("\nDone.")
