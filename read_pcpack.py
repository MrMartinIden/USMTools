import io
import sys
import os

sys.path.append(os.path.join(sys.path[0], 'src'))
from generic_mash_header import *
from resource_pack_header import *
from mashable_vector import *
from resource_directory import *


def read_pack(file):
    print("Resource pack:", file)
    with io.open(file, mode="rb") as rPack:
        buffer_bytes = rPack.read()
        print("0x%02X" % buffer_bytes[0])
        print("0x%02X" % buffer_bytes[1])
        print(len(buffer_bytes))

        rPack.seek(0, 2)
        numOfBytes = rPack.tell()
        print("Total Size:", numOfBytes, "bytes")

        rPack.seek(0, 0)
        pack_header = resource_pack_header.from_buffer_copy(rPack.read(sizeof(resource_pack_header)))

        rpVersion = pack_header.field_0.field_0

        if rpVersion == 14:
            print("Game: Ultimate Spider-Man NTSC 1.0")
        elif rpVersion == 10:
            print("Game: Ultimate Spider-Man NTSC 06/20/2005 Prototype")

        directory_offset = pack_header.directory_offset
        base = pack_header.res_dir_mash_size

        rPack.seek(directory_offset)
        mash_header = generic_mash_header.from_buffer_copy(rPack.read(sizeof(generic_mash_header)))
        print(mash_header)

        cur_ptr = directory_offset + sizeof(generic_mash_header)

        directory = resource_directory.from_buffer_copy(rPack.read(sizeof(resource_directory)))
        print(directory)

        assert(directory.parents.from_mash())
        assert(directory.resource_locations.from_mash())
        assert(directory.texture_locations.from_mash())
        assert(directory.mesh_file_locations.from_mash())
        assert(directory.mesh_locations.from_mash())
        assert(directory.morph_file_locations.from_mash())
        assert(directory.morph_locations.from_mash())

        mash_data_ptrs = generic_mash_data_ptrs(rPack, rPack)

        #mash_data_ptrs.field_0 = cur_ptr + sizeof(resource_directory)
        #mash_data_ptrs.field_4 = directory_offset + mash_header.field_8
        print(mash_data_ptrs)

        assert(directory_offset % 4 == 0)

        directory.un_mash_start(mash_data_ptrs)

        directory.constructor_common(base, 0, pack_header.field_20 - base, pack_header.field_24)

        assert(directory.get_tlresource_count( TLRESOURCE_TYPE_MESH_FILE ) == directory.get_resource_count( RESOURCE_KEY_TYPE_MESH_FILE_STRUCT ))

        assert(directory.get_tlresource_count( TLRESOURCE_TYPE_MATERIAL_FILE ) == directory.get_resource_count( RESOURCE_KEY_TYPE_MATERIAL_FILE_STRUCT ))

        return (pack_header, mash_header, directory, buffer_bytes)
