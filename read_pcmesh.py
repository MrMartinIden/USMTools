import io
import os
import sys
from os import listdir
from os.path import isfile, join, dirname, splitext
from ctypes import *
from enum import IntEnum

sys.path.append(os.path.join(sys.path[0], 'src'))
from generic_mash_data_ptrs import *
from read_pcpack import *

class vector4d(Structure):
    _fields_ = [
                ("arr", c_float * 4),
                ]

assert(sizeof(vector4d) == 16)


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

class TypeDirectoryEntry(IntEnum):
    MATERIAL = 1
    MESH = 2


class nglDirectoryEntry(Structure):
    _fields_ = [("field_0", c_char),
                ("field_1", c_char),
                ("field_2", c_char),
                ("typeDirectoryEntry", c_char),
                ("field_4", c_int), # <--- this is pointer to the resource (texture, mesh)
                ("field_8", c_int),
                ]

assert(sizeof(nglDirectoryEntry) == 0xC)

class Lod(Structure):
    _fields_ = [
                ("field_0", c_int),
                ("field_4", c_float),
                ]

assert(sizeof(Lod) == 0x8)

class tlHashString(Structure):
    _fields_ = [
                ("field_0", c_int),
                ]

assert(sizeof(tlHashString) == 4)

class nglVertexBuffer(Structure):
    _fields_ = [
                ("m_vertexData", c_int),
                ("Size", c_int), # <---- size of vertex data in bytes
                ("m_vertexBuffer", c_int)
            ]

class nglMeshSection(Structure):
    _fields_ = [
                ("Name", c_int), # <----- tlFixedString
                ("Material", c_int), # <----- nglMaterialBase
                ("NBones", c_int),
                ("BonesIdx", c_int), # <----- u16
                ("SphereCenter", vector4d),
                ("SphereRadius", c_float),
                ("Flags", c_int),
                ("m_primitiveType", c_int),
                ("NIndices", c_int),
                ("m_indices", c_int), # <--- u16
                ("m_indexBuffer", c_int),
                ("NVertices", c_int),
                ("VertexBuffer", nglVertexBuffer),
                ("m_stride", c_int),
                ("field_4C", c_int),
                ("field_50", c_int),
                ("VertexDef", c_int),
                ("field_58", c_int),
                ("field_5C", c_int)
                ]

class Section(Structure):
    _fields_ = [
                ("field_0", c_int),
                ("Section", c_int), # <---- nglMeshSection
                ]

class nglMesh(Structure):
    _fields_ = [
                ("Name", c_int), # <----- tlFixedString
                ("Flags", c_int),
                ("NSections", c_int),
                ("Sections", c_int),
                ("NBones", c_int),
                ("Bones", c_int),
                ("NLODs", c_int),
                ("LODs", c_int),
                ("field_20", vector4d),
                ("SphereRadius", c_int),
                ("File", c_int),
                ("NextMesh", c_int),
                ("field_3C", c_int)
                ]

assert(sizeof(nglMesh) == 0x40)

class nglMeshFileHeader(Structure):
    _fields_ = [
                ("Tag", c_char * 4),
                ("Version", c_int),
                ("NDirectoryEntries", c_int),
                ("DirectoryEntries", c_int),
                ("field_10", c_int)
                ]

assert(sizeof(nglMeshFileHeader) == 0x14)

class tlFixedString(Structure):
    _fields_ = [
                ("m_hash", c_int),
                ("field_4", c_char * 28)
                ]

assert(sizeof(tlFixedString) == 0x20)


class nglShader(Structure):
    _fields_ = [
                ("m_vtbl", c_int),
                ("field_4", c_int),
                ("field_8", c_int),
                ]

assert(sizeof(nglShader) == 0xC)

class nglTexture(Structure):
    _fields_ = [
                ("field_0", c_int),
                ]

class nglMaterialBase(Structure):
    _fields_ = [("Name", c_int),
                ("field_4", POINTER(nglShader)),
                ("File", c_int),
                ("NextMaterial", c_int),
                ("field_10", c_int),
                ("field_14", c_int),
                ("field_18", POINTER(tlFixedString)),
                ("field_1C", POINTER(nglTexture)),
                ("field_20", POINTER(nglTexture)),
                ("field_24", POINTER(nglTexture)),
                ("field_28", vector4d),
                ("field_38", c_float),
                ("field_3C", c_int),
                ("field_40", c_int),
                ("field_44", c_int),
                ("m_outlineFeature", c_int),
                ("m_blend_mode", c_int),
                ]

#assert(sizeof(nglMaterialBase) == 0x50)

DEV_MODE = 1

def write_indices(resource_file, indices, primitive_type, enable_normals: bool):
    if primitive_type == 5:
        face = [indices[0], indices[1], indices[2]]

        #resource_file.write("f " + ("%d %d %d\n" % (face[0], face[1], face[2])))

        if enable_normals:
            resource_file.write("f " + ("%d/%d/%d %d/%d/%d %d/%d/%d\n" % (face[0], face[0], face[0],
                                                             face[1], face[1], face[1],
                                                             face[2], face[2], face[2])))
        else:
            resource_file.write("f " + ("%d/%d %d/%d %d/%d\n" % (face[0], face[0], face[1], face[1], face[2], face[2])))

        for idx in list(indices):
            face = [face[1], face[2], idx]
            if len(face) == len(set(face)):
                #resource_file.write("f " + ("%d %d %d\n" % (face[0], face[1], face[2])))

                if enable_normals:
                    resource_file.write("f " + ("%d/%d/%d %d/%d/%d %d/%d/%d\n" % (face[0], face[0], face[0],
                                                                 face[1], face[1], face[1],
                                                             face[2], face[2], face[2])))
                else:
                    resource_file.write("f " + ("%d/%d %d/%d %d/%d\n" % (face[0], face[0], face[1], face[1], face[2], face[2])))


    elif primitive_type == 4:
        N: int = 3
        assert(len(indices) % 3 == 0)
        faces  = [indices[n:n+N] for n in range(0, len(indices), N)]

        for face in faces:

            if enable_normals:
                resource_file.write("f " + ("%d/%d/%d %d/%d/%d %d/%d/%d\n" % (face[0], face[0], face[0],
                                                             face[1], face[1], face[1],
                                                             face[2], face[2], face[2])))
            else:
                resource_file.write("f " + ("%d/%d %d/%d %d/%d\n" % (face[0], face[0], face[1], face[1], face[2], face[2])))

    else:
        assert(0)

def read_mesh(Mesh: nglMesh, buffer_bytes):

    offset = Mesh.Name
    nameMesh = tlFixedString.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(tlFixedString))])

    folder = 'tmp'
    try:
        os.mkdir(folder)
    except OSError:
        print ("Creation of the directory %s failed" % folder)
    else:
        print ("Successfully created the directory %s " % folder)

    ndisplay = nameMesh.field_4.decode("utf-8")
    filepath = os.path.join('.', 'tmp', ndisplay + ".obj")
    filepath = ''.join(x for x in filepath if x.isprintable())
    resource_file = open(filepath, mode="w")

    #resource_file.write("MeshName = %s, NSections = %d\n" % (nameMesh.field_4, Mesh.NSections))
    offset = Mesh.Sections
    sections_t = Section * int(Mesh.NSections)
    sections = sections_t.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(sections_t))])

    prev_NVertices = 0

    for idx, section in enumerate(sections):

        offset = section.Section
        meshSection = nglMeshSection.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(nglMeshSection))])

        offset = meshSection.Name
        name = tlFixedString.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(tlFixedString))])

        resource_file.write("o " + ndisplay + '_' + str(idx) + '\n')

        #resource_file.write("\nidx_section = %d, name = %s, primitiveType = %d, stride = %d, NIndices = %d, NVertices = %d, SizeVertexDataInBytes = %d\n"
        #        % (idx, name.field_4, meshSection.m_primitiveType, meshSection.m_stride, meshSection.NIndices, meshSection.NVertices, meshSection.VertexBuffer.Size))

        primCount = 0
        if meshSection.m_primitiveType == 5:
            primCount = meshSection.NIndices - 2
        elif meshSection.m_primitiveType == 4:
            primCount = meshSection.NIndices / 3

        assert(meshSection.m_stride == 64)
        assert(meshSection.m_stride * meshSection.NVertices == meshSection.VertexBuffer.Size)

        #resource_file.write("NPrimitive = %d\n" % primCount)

        class VertexData(Structure):
            _fields_ = [
                        ("pos", c_float * 3),
                        ("normal", c_float * 3),
                        ("uv", c_float * 2),
                        ("bone_indices", c_float * 4),
                        ("bone_weights", c_float * 4)
                        ]

            def __repr__(self):
                return f'VertexData: pos = {list(self.pos)}, normal = {list(self.normal)}, uv = {list(self.uv)}, bone_indices = {list(self.bone_indices)}, bone_weights = {list(self.bone_weights)}'

        assert(sizeof(VertexData) == 0x40)

        offset = meshSection.VertexBuffer.m_vertexData
        print(offset)
        vertex_data_t = VertexData * int(meshSection.NVertices)
        vertex_data = vertex_data_t.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(vertex_data_t))])

        for vtx in vertex_data:
            print(vtx)
            resource_file.write("v " + ("%.6f %.6f %.6f" % (vtx.pos[0], vtx.pos[1], vtx.pos[2])) + '\n')

        for vtx in vertex_data:
            resource_file.write("vt " + ("%.6f %.6f" % (vtx.uv[0], 1.0 - vtx.uv[1])) + '\n')

        for vtx in vertex_data:
            resource_file.write("vn " + ("%.6f %.6f %.6f" % (vtx.normal[0], vtx.normal[1], vtx.normal[2])) + '\n')

        resource_file.write("s off\n")

        offset = meshSection.m_indices
        indices_data_t = c_short * int(meshSection.NIndices)
        indices = indices_data_t.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(indices_data_t))])

        #resource_file.write("\nIndices: ")

        print("NIndices = %d" % (meshSection.NIndices))

        if meshSection.NIndices != 0:

            num_vertices = int(meshSection.NVertices)
            max_index = max(list(indices))
            print("max_index = %d, NVertices = %d" % (max_index, num_vertices))

            for i, index in enumerate(indices):
                indices[i] = prev_NVertices + index + 1

            write_indices(resource_file, indices, meshSection.m_primitiveType, False)
        elif meshSection.NVertices == 6:

            resource_file.write("f " + ("%d %d %d\n" % (1, 2, 3)))
            resource_file.write("f " + ("%d %d %d\n" % (4, 5, 6)))
        else:

            print("\nidx_section = %d, name = %s, primitiveType = %d, stride = %d, NIndices = %d, NVertices = %d, SizeVertexDataInBytes = %d\n"
                % (idx, name.field_4, meshSection.m_primitiveType, meshSection.m_stride, meshSection.NIndices, meshSection.NVertices, meshSection.VertexBuffer.Size))
            assert(0)

        prev_NVertices = meshSection.NVertices + prev_NVertices

        #resource_file.write(str(list(indices)) + '\n')
        resource_file.write("\n\n")

        for vtx in vertex_data:
            bones_scale = 3.0
            bones_offset = 11.0
            indices = [0.0, 0.0, 0.0, 0.0]
            indices[0] = vtx.bone_indices[0] * bones_scale + bones_offset
            indices[1] = vtx.bone_indices[1] * bones_scale + bones_offset
            indices[2] = vtx.bone_indices[2] * bones_scale + bones_offset
            indices[3] = vtx.bone_indices[3] * bones_scale + bones_offset
            #print("indices " + ("%f %.6f %.6f %.6f" % (indices[0], indices[1], indices[2], indices[3])) + '\n')


def read_meshfile(file):
    print("Resource pack:", file)
    with io.open(file, mode="rb") as rPack:
        buffer_bytes = rPack.read()

        print("0x%02X" % buffer_bytes[0])
        print("0x%02X" % buffer_bytes[1])
        print(len(buffer_bytes))

        rPack.seek(0, 2)
        numOfBytes = rPack.tell()
        print("Total Size:", numOfBytes, "bytes")

        Header = nglMeshFileHeader.from_buffer_copy(buffer_bytes[0:sizeof(nglMeshFileHeader)])
        assert(Header.Tag == b'PCM ')
        assert(Header.Version == 0x601)
        assert(Header.NDirectoryEntries == 8)
        assert(Header.field_10 == 0)

        for i in range(Header.NDirectoryEntries):
            print("\nidx = %d" % i)

            offset = Header.DirectoryEntries + i * sizeof(nglDirectoryEntry)
            print("0x%X" % offset);
            exit();

            entry = nglDirectoryEntry.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(nglDirectoryEntry))])
            print("typeDirectoryEntry = %s" % ("MATERIAL" if int.from_bytes(entry.typeDirectoryEntry) == 1 else "MESH") )
            print("0x%X 0x%X" % (entry.field_4, entry.field_8))

            type_dir_entry = int.from_bytes(entry.typeDirectoryEntry)
            if type_dir_entry == int(TypeDirectoryEntry.MATERIAL):

                offset = entry.field_4
                Material = nglMaterialBase.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(nglMaterialBase))])
                print("0x%08X" % Material.Name)

                offset = Material.Name
                MaterialName = tlFixedString.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(tlFixedString))])
                print("%s" % MaterialName.field_4)

                assert(Material.field_44 == 1)

            elif type_dir_entry == int(TypeDirectoryEntry.MESH):

                offset = entry.field_4
                mesh = nglMesh.from_buffer_copy(buffer_bytes[offset : (offset + sizeof(nglMesh))])

                read_mesh(mesh, buffer_bytes)

        return

        directory_offset = pack_header.directory_offset
        base = pack_header.res_dir_mash_size

        mash_header = generic_mash_header.from_buffer_copy(buffer_bytes[directory_offset : (directory_offset + sizeof(generic_mash_header))])
        print(mash_header)

        cur_ptr = directory_offset + sizeof(generic_mash_header)

        directory = resource_directory.from_buffer_copy(buffer_bytes[cur_ptr : cur_ptr + sizeof(resource_directory)])
        print(directory)

        assert(directory.parents.from_mash())
        assert(directory.resource_locations.from_mash())
        assert(directory.texture_locations.from_mash())
        assert(directory.mesh_file_locations.from_mash())
        assert(directory.mesh_locations.from_mash())
        assert(directory.morph_file_locations.from_mash())
        assert(directory.morph_locations.from_mash())

        mash_data_ptrs = generic_mash_data_ptrs()
        mash_data_ptrs.field_0 = cur_ptr + sizeof(resource_directory)
        mash_data_ptrs.field_4 = directory_offset + mash_header.field_8
        print(mash_data_ptrs)

        assert(directory_offset % 4 == 0)

        directory.un_mash_start(mash_data_ptrs, buffer_bytes)

        directory.constructor_common(base, 0, pack_header.field_20 - base, pack_header.field_24)

        assert(directory.get_tlresource_count( TLRESOURCE_TYPE_MESH_FILE ) == directory.get_resource_count( RESOURCE_KEY_TYPE_MESH_FILE_STRUCT ))

        assert(directory.get_tlresource_count( TLRESOURCE_TYPE_MATERIAL_FILE ) == directory.get_resource_count( RESOURCE_KEY_TYPE_MATERIAL_FILE_STRUCT ))

        return (pack_header, mash_header, directory, buffer_bytes)


def main(file):
    print()
    print(os.path.join('.', 'src'))
    name_pak, ext = splitext(file)

    if ext != ".PCMESH":
        return

    _, _, directory, buffer_bytes = read_meshfile(file)
    return

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

