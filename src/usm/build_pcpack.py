import argparse
import os
import sys
from itertools import repeat
from os.path import splitext

from .generic_mash_header import *
from .read_pcpack import *
from .resource_directory import *
from .resource_pack_header import *


def rebase(x, i, f):
    v8 = i - x % i
    if v8 < i:
        data = bytearray()
        data.extend(repeat(0xE3, v8))
        f.write(data)
        return x + v8

    return x

def build_pack(name, pack_header: resource_pack_header,
                mash_header: generic_mash_header,
                directory: resource_directory,
                size_origin_file):
    resource_file = open(name + "._PCPACK", mode="wb")

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

        f: file
        try:
            f = open(filepath, mode="rb")
        except OSError:
            print ("File does not appear to exist. %s" % filepath)

        resource_file.seek(resource_idx, 0)
        resource_file.write(f.read())

        print(f"range: {resource_idx:#X} {resource_idx + mash_data_size:#x}")

    resource_file.seek(0, 2)
    if resource_file.tell() < size_origin_file:
        data = bytearray()
        data.extend(repeat(0x0, size_origin_file - resource_file.tell()))
        resource_file.write(data)


def main():
    p = argparse.ArgumentParser(
        prog="pack",
        description="Build PACK file from directory with assets.",
    )

    p.add_argument("input", help=".PACK file")

    args = p.parse_args()

    input_path = os.path.abspath(args.input)
    if not input_path:
        sys.exit("No .pack files found.")

    name_pak, ext = splitext(input_path)

    if ext != ".PCPACK":
        sys.exit("File must be contain *.PCPACK extension")

    pack_header, mash_header, directory, buffer_bytes = read_pack(input_path)

    build_pack(name_pak, pack_header, mash_header, directory, len(buffer_bytes))


if __name__ == '__main__':
    main()
