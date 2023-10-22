import sys
import os
from os.path import isfile, join, dirname, splitext
from itertools import repeat

from read_pcpack import *

sys.path.append(os.path.join(sys.path[0], 'src'))
from generic_mash_header import *
from resource_pack_header import *
from resource_directory import *


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
    res_dir.parents.m_data = None
    res_dir.resource_locations.m_data = None
    res_dir.texture_locations.m_data = None
    res_dir.mesh_file_locations.m_data = None
    res_dir.mesh_locations.m_data = None
    res_dir.morph_file_locations.m_data = None
    res_dir.morph_locations.m_data = None
    res_dir.material_file_locations.m_data = None
    res_dir.material_locations.m_data = None
    res_dir.anim_file_locations.m_data = None
    res_dir.anim_locations.m_data = None
    res_dir.scene_anim_locations.m_data = None
    res_dir.skeleton_locations.m_data = None

    resource_file.write(bytes(res_dir))

    offset = resource_file.tell()
    offset = rebase(offset, 8, resource_file)

    offset = rebase(offset, 4, resource_file)
    offset = rebase(offset, 4, resource_file)

    resource_file.seek(offset, 0)

    data = directory.parents.m_data[0].to_bytes(4, "little")
    print(data)
    resource_file.write(data)

    offset = resource_file.tell()
    offset = rebase(offset, 4, resource_file)

    ####
    offset = rebase(offset, 8, resource_file)
    offset = rebase(offset, 4, resource_file)
    resource_file.seek(offset, 0)

    for i in range(directory.resource_locations.m_size):
        data = bytes(directory.resource_locations.m_data[i])
        resource_file.write(data)

    offset = resource_file.tell()
    offset = rebase(offset, 4, resource_file)

    def save(vector, f):
        offset = f.tell()
        offset = rebase(offset, 8, f)
        offset = rebase(offset, 4, f)
        resource_file.seek(offset, 0)

        for i in range(vector.m_size):
            tlres_loc = vector.m_data[i]
            resource_file.write(tlres_loc)

        offset = f.tell()
        offset = rebase(offset, 4, f)

    save(directory.texture_locations, resource_file)

    save(directory.mesh_file_locations, resource_file)

    save(directory.mesh_locations, resource_file)

    save(directory.morph_file_locations, resource_file)

    save(directory.morph_locations, resource_file)

    save(directory.material_file_locations, resource_file)

    save(directory.material_locations, resource_file)

    save(directory.anim_file_locations, resource_file)

    save(directory.anim_locations, resource_file)

    save(directory.scene_anim_locations, resource_file)

    save(directory.skeleton_locations, resource_file)

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
        except IOError:
            print ("File does not appear to exist. %s" % filepath)

        resource_file.seek(resource_idx, 0)
        resource_file.write(f.read())

        print("range: {0:#X} {1:#x}".format(resource_idx, resource_idx + mash_data_size))

    resource_file.seek(0, 2)
    if resource_file.tell() < size_origin_file:
        data = bytearray()
        data.extend(repeat(0x0, size_origin_file - resource_file.tell()))
        resource_file.write(data)


def main(file):
    name_pak, ext = splitext(file)

    if ext != ".PCPACK":
        print("File must be contain *.PCPACK extension")
        return

    pack_header, mash_header, directory, buffer_bytes = read_pack(file)

    build_pack(name_pak, pack_header, mash_header, directory, len(buffer_bytes))


if __name__ == '__main__':
    main(sys.argv[1])
