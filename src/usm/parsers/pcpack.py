import os
from itertools import repeat
from os.path import splitext

from usm.generic_mash_header import *
from usm.mashable_vector import *
from usm.pack_file import *
from usm.parsers.pack import PackParser
from usm.resource_directory import *
from usm.resource_pack_header import *


def rebase(x, i, f):
    v8 = i - x % i
    if v8 < i:
        data = bytearray()
        data.extend(repeat(0xE3, v8))
        f.write(data)
        return x + v8

    return x


class PCPackParser(PackParser):
    def read(self, file: str) -> PACKFile:
        print("Resource pack:", file)
        with open(file, mode="rb") as rPack:
            rPack.seek(0, 2)
            numOfBytes = rPack.tell()
            print("Total Size:", numOfBytes, "bytes")

            rPack.seek(0, 0)
            magic = rPack.read(2)
            print(f"0x{magic[0]:02X}")
            print(f"0x{magic[1]:02X}")

            rPack.seek(0, 0)
            pack_header = resource_pack_header.from_buffer_copy(rPack.read(sizeof(resource_pack_header)))

            rpVersion = pack_header.field_0.field_0

            if rpVersion == 14:
                print("Game: Ultimate Spider-Man NTSC 1.0")
            elif rpVersion == 10:
                print("Game: Ultimate Spider-Man NTSC 06/20/2005 Prototype")

            print(pack_header.field_0)

            directory_offset = pack_header.directory_offset
            base = pack_header.res_dir_mash_size

            rPack.seek(directory_offset)
            mash_header = generic_mash_header.from_buffer_copy(rPack.read(sizeof(generic_mash_header)))
            print(mash_header)

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
            print(mash_data_ptrs)

            assert(directory_offset % 4 == 0)

            directory.un_mash_start(mash_data_ptrs)

            directory.constructor_common(base, 0, pack_header.field_20 - base, pack_header.field_24)

            assert(directory.get_tlresource_count( TLRESOURCE_TYPE_MESH_FILE ) == directory.get_resource_count( RESOURCE_KEY_TYPE_MESH_FILE_STRUCT ))

            assert(directory.get_tlresource_count( TLRESOURCE_TYPE_MATERIAL_FILE ) == directory.get_resource_count( RESOURCE_KEY_TYPE_MATERIAL_FILE_STRUCT ))

            resources = {}
            for i in range(directory.resource_locations.size()):
                res_loc = directory.get_resource_location(i)
                resource_idx = directory.get_resource(res_loc)
                name = ''.join(x for x in res_loc.field_0.get_platform_string() if x.isprintable())

                rPack.seek(resource_idx)
                resources[name] = rPack.read(res_loc.m_size)

            return PACKFile(pack_header, mash_header, directory, numOfBytes, resources)

    def list(self, file: str) -> None:
        for name in self.read(file).resources:
            print(name)

    def extract(self, file: str) -> None:
        name_pak, _ = splitext(file)

        pack = self.read(file)

        folder = name_pak
        try:
            os.mkdir(folder)
        except OSError:
            print (f"Creation of the directory {folder} failed")
        else:
            print (f"Successfully created the directory {folder} ")

        for name, data in pack.resources.items():
            filepath = os.path.join(folder, name)
            with open(filepath, mode="wb") as resource_file:
                resource_file.write(data)

    def build(self, name, pack: PACKFile) -> None:
        pack_header = pack.pack_header
        mash_header = pack.mash_header
        directory = pack.directory
        size_origin_file = pack.file_size

        with open(name + "._PCPACK", mode="wb") as resource_file:
            resource_file.write(bytes(pack_header))
            resource_file.seek(pack_header.directory_offset, 0)
            resource_file.write(bytes(mash_header))

            res_dir = resource_directory.from_buffer_copy(bytes(directory))
            res_dir.parents.m_data = 0
            res_dir.resource_locations.m_data = 0
            res_dir.texture_locations.m_data = 0
            res_dir.mesh_file_locations.m_data = 0
            res_dir.mesh_locations.m_data = 0
            res_dir.morph_file_locations.m_data = 0
            res_dir.morph_locations.m_data = 0
            res_dir.material_file_locations.m_data = 0
            res_dir.material_locations.m_data = 0
            res_dir.anim_file_locations.m_data = 0
            res_dir.anim_locations.m_data = 0
            res_dir.scene_anim_locations.m_data = 0
            res_dir.skeleton_locations.m_data = 0

            resource_file.write(bytes(res_dir))

            offset = resource_file.tell()
            offset = rebase(offset, 8, resource_file)

            offset = rebase(offset, 4, resource_file)
            offset = rebase(offset, 4, resource_file)

            resource_file.seek(offset, 0)

            data = directory._parents_ptr[0].to_bytes(4, "little")
            print(data)
            resource_file.write(data)

            offset = resource_file.tell()
            offset = rebase(offset, 4, resource_file)

            ####
            offset = rebase(offset, 8, resource_file)
            offset = rebase(offset, 4, resource_file)
            resource_file.seek(offset, 0)

            for i in range(directory.resource_locations.m_size):
                data = bytes(directory._resource_locations_ptr[i])
                resource_file.write(data)

            offset = resource_file.tell()
            offset = rebase(offset, 4, resource_file)

            def save(vector, ptr, f):
                offset = f.tell()
                offset = rebase(offset, 8, f)
                offset = rebase(offset, 4, f)
                resource_file.seek(offset, 0)

                for i in range(vector.m_size):
                    tlres_loc = ptr[i]
                    resource_file.write(tlres_loc)

                offset = f.tell()
                offset = rebase(offset, 4, f)

            save(directory.texture_locations, directory._texture_locations_ptr, resource_file)

            save(directory.mesh_file_locations, directory._mesh_file_locations_ptr, resource_file)

            save(directory.mesh_locations, directory._mesh_locations_ptr, resource_file)

            save(directory.morph_file_locations, directory._morph_file_locations_ptr, resource_file)

            save(directory.morph_locations, directory._morph_locations_ptr, resource_file)

            save(directory.material_file_locations, directory._material_file_locations_ptr, resource_file)

            save(directory.material_locations, directory._material_locations_ptr, resource_file)

            save(directory.anim_file_locations, directory._anim_file_locations_ptr, resource_file)

            save(directory.anim_locations, directory._anim_locations_ptr, resource_file)

            save(directory.scene_anim_locations, directory._scene_anim_locations_ptr, resource_file)

            save(directory.skeleton_locations, directory._skeleton_locations_ptr, resource_file)

            folder = name
            for i in range(directory.resource_locations.size()):
                res_loc: resource_location = directory.get_resource_location(i)

                mash_data_size = res_loc.m_size
                resource_idx = directory.get_resource(res_loc)

                ndisplay = res_loc.field_0.get_platform_string()
                filepath = os.path.join(folder, ndisplay)
                filepath = ''.join(x for x in filepath if x.isprintable())

                try:
                    with open(filepath, mode="rb") as f:
                        resource_file.seek(resource_idx, 0)
                        resource_file.write(f.read())
                except OSError:
                    print(f"File does not appear to exist. {filepath}")
                    continue

                print(f"range: {resource_idx:#X} {resource_idx + mash_data_size:#x}")

            resource_file.seek(0, 2)
            if resource_file.tell() < size_origin_file:
                data = bytearray()
                data.extend(repeat(0x0, size_origin_file - resource_file.tell()))
                resource_file.write(data)
