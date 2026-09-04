import os
from ctypes import *
from os import listdir
from os.path import dirname, isfile, join, splitext

from .resource_amalgapak_header import *
from .resource_key import *
from .resource_location import *
from .resource_pack_location import *
from .resource_versions import *
from .string_hash import *

fileList = [
    f for f in listdir(dirname(__file__)) if isfile(join(dirname(__file__), f))
]

#Header_Section 0x38
#LBA_Section 0xBFE0
#FileData Individual Section 0x50

DEV_MODE = 1

for file in fileList:
    _, ext = splitext(file)
    if ext == ".PAK":
        print("Resource pack:", file)
        with open(file, mode="rb") as rPack:
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
                print (f"Creation of the directory {folder} failed")
            else:
                print (f"Successfully created the directory {folder} ")
                
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
                with open(filepath, mode="wb") as nflfile:
                    nflfile.write(nfldata)
            

print("\nDone.")
