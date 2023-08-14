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
                
assert(sizeof(resource_versions) == 0x14)
                
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
                
class resource_pack_header(Structure):
    _fields_ = [("field_0", resource_versions),
                ("field_14", c_int),
                ("directory_offset", c_int),
                ("res_dir_mash_size", c_int),
                ("field_20", c_int),
                ("field_24", c_int),
                ("field_28", c_int)
                ]

assert(sizeof(resource_pack_header) == 0x2C)

class string_hash(Structure):
    _fields_ = [("source_hash_code", c_int)]

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
        return "{:#X}".format(self.source_hash_code)

    def __repr__(self):
        hash_code = "0x%08X" % self.source_hash_code
        return f'string_hash(name = {hash_code}'    


string_hash_dictionary = {}
try:
    with io.open("string_hash_dictionary.txt", mode="r") as dictionary_file:
        for i, line in enumerate(dictionary_file):
            if i > 1:
                arr = line.split()
                h = int(arr[0], 16)
                string_hash_dictionary[h] = arr[1]
        
except IOError:
    input("Could not open file!")

assert(len(string_hash_dictionary) != 0)

def tohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))

resource_key_type_ext = ["none",
                        ".XBANIM", ".XBSKEL", ".ALS", ".ENT", ".ENTEXT", ".DDS", ".DDSMP", ".IFL", ".DESC", ".ENS",
                        ".SPL", ".AB", ".QP", ".TRIG", ".XBSX", ".INST", "FDF", ".PANEL", ".TXT", ".ICN",
                        ".XBMESH", ".XBMORPH", ".XBMAT", ".COLL", ".XBPACK", ".XBSANIM", ".MSN", ".MARKER", ".HH", ".WAV",
                        ".WBK", ".XMV", "XMV", ".PFX", ".CSV", ".CLE", ".LIT", ".GRD", ".GLS", ".LOD",
                        ".SIN", ".GV", ".SV", ".TOKENS", ".DSG", ".PATH", ".PTRL", ".LANG", ".SLF", ".VISEME",
                        ".XBMESHDEF", ".XBMORPHDEF", ".XBMATDEF", ".MUT", ".FX_CACHE", ".ASG", ".BAI", ".CUT", ".INTERACT", ".CSV",
                        ".CSV", "._ENTID_", "._ANIMID_", "._REGIONID_", "._AI_GENERIC_ID_", "._RADIOMSG_", "._GOAL_", "._IFC_ATTRIBUTE_", "._SIGNAL_", "._PACKSTATE_"]

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
        return f'resource_key(m_hash = {self.m_hash}, m_type = {self.m_type})'

class resource_location(Structure):
    _fields_ = [("field_0", resource_key),
                ("m_offset", c_int),
                ("m_size", c_int)
                ]
                
    def __repr__(self):
        return f'resource_location(field_0 = {self.field_0}, m_offset = {self.m_offset}, m_size = {self.m_size})'

assert(sizeof(resource_location) == 0x10)

TLRESOURCE_TYPE_NONE = 0
TLRESOURCE_TYPE_TEXTURE = 1
TLRESOURCE_TYPE_MESH_FILE = 2
TLRESOURCE_TYPE_MESH = 3
TLRESOURCE_TYPE_MORPH_FILE = 4
TLRESOURCE_TYPE_MORPH = 5
TLRESOURCE_TYPE_MATERIAL_FILE = 6
TLRESOURCE_TYPE_MATERIAL = 7
TLRESOURCE_TYPE_ANIM_FILE = 8
TLRESOURCE_TYPE_ANIM = 9
TLRESOURCE_TYPE_SCENE_ANIM = 10
TLRESOURCE_TYPE_SKELETON = 11
TLRESOURCE_TYPE_Z = 12

class tlresource_location(Structure):
    _fields_ = [("name", string_hash),
                ("type", c_char),
                ("offset", c_int)
                ]
                
    def get_type(self) -> int:
        return int.from_bytes(self.type, "little")

    def __repr__(self):
        return f'tlresource_location(name = {self.name}, type = {self.get_type()}, offset={hex(self.offset)})'
                
assert(sizeof(tlresource_location) == 0xC)


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

class generic_mash_header(Structure):
    _fields_ = [("safety_key", c_int),
                ("field_4", c_int),
                ("field_8", c_int),
                ("class_id", c_short),
                ("field_E", c_short)
                ]
                
    def __repr__(self):
        return f'generic_mash_header(safety_key = {hex(self.safety_key)}, field_4={self.field_4}, field_8={hex(self.field_8)})'
                
    def generate_safety_key(self):
        return (self.field_8 + 0x7BADBA5D - (self.field_4 & 0xFFFFFFF) + self.class_id + self.field_E) & 0xFFFFFFF | 0x70000000
        
    def is_flagged(self, f: c_int):
        return (f & self.field_4) != 0
        
    def get_mash_data(self) -> c_char_p:
        return cast(this, c_char_p) + self.field_8

assert(sizeof(generic_mash_header) == 0x10)

class generic_mash_data_ptrs(Structure):
    _fields_ = [("field_0", c_int),
                ("field_4", c_int)
                ]
             
    def rebase(self, i: int):
        v8 = i - self.field_0 % i;
        if v8 < i:
            self.field_0 += v8;
                
    def __repr__(self):
        return f'generic_mash_data_ptrs(field_0 = {hex(self.field_0)}, field_4 = {hex(self.field_4)})'
    

class mashable_vector(Structure):
    _fields_ = [("m_data", c_int),
               ("m_size", c_short),
               ("m_shared", c_bool),
               ("field_7", c_bool)
                ]
                
    def __repr__(self):
        return f'mashable_vector(m_size={self.m_size}, m_shared={self.m_shared}, ' \
                f'm_shared={self.from_mash()})'
    
    def from_mash(self) -> bool:
        return self.field_7
        
    def size(self):
        return self.m_size
    
    def empty(self) -> bool:
        return self.size() == 0
        
    def custom_un_mash(self, a4: generic_mash_data_ptrs) -> generic_mash_data_ptrs:
        a4.rebase(4)
        
        a4.rebase(4)
        
        self.m_data = a4.field_0
        a4.field_0 += 4 * self.m_size
        
        a4.rebase(4)
        
        return a4
    
        
    def custom_un_mash__resource_location(self, a4: generic_mash_data_ptrs) -> generic_mash_data_ptrs:
        a4.rebase(8)
        
        a4.rebase(4)
        
        self.m_data = a4.field_0;
        a4.field_0 += sizeof(resource_location) * self.m_size;
        
        a4.rebase(4)
        
        return a4

    def custom_un_mash__tlresource_location(self, a4: generic_mash_data_ptrs) -> generic_mash_data_ptrs:
        a4.rebase(8)
        
        a4.rebase(4)
        
        self.m_data = a4.field_0;
        a4.field_0 += sizeof(tlresource_location) * self.m_size;
        
        a4.rebase(4)
        
        return a4

        
    def un_mash(self, a4: generic_mash_data_ptrs) -> generic_mash_data_ptrs:
        assert(self.from_mash())
        return self.custom_un_mash(a4)
                
print(sizeof(mashable_vector) == 8)


RESOURCE_KEY_TYPE_NONE = 0
RESOURCE_KEY_TYPE_MESH_FILE_STRUCT = 51
RESOURCE_KEY_TYPE_MATERIAL_FILE_STRUCT = 53
RESOURCE_KEY_TYPE_Z = 70

class resource_directory(Structure):
    _fields_ = [("parents", mashable_vector),
                ("resource_locations", mashable_vector),
                ("texture_locations", mashable_vector),
                ("mesh_file_locations", mashable_vector),
                ("mesh_locations", mashable_vector),
                ("morph_file_locations", mashable_vector),
                ("morph_locations", mashable_vector),
                ("material_file_locations", mashable_vector),
                ("material_locations", mashable_vector),
                ("anim_file_locations", mashable_vector),
                ("anim_locations", mashable_vector),
                ("scene_anim_locations", mashable_vector),
                ("skeleton_locations", mashable_vector),
                ("field_68", mashable_vector),
                ("field_70", mashable_vector),
                ("pack_slot", c_int),
                ("base", c_int),
                ("field_80", c_int),
                ("field_84", c_int),
                ("field_88", c_int),
                ("type_start_idxs", c_int * 71),
                ("type_end_idxs", c_int * 71)
                ]
                
    def __repr__(self):
        return f'resource_directory:\n\tparents = {self.parents},\n\tresource_locations = {self.resource_locations},\n\t' \
               f'texture_locations = {self.texture_locations}, \n\t' \
               f'mesh_file_locations = {self.mesh_file_locations},\n\tmesh_locations = {self.mesh_locations},\n\t' \
               f'morph_file_locations = {self.morph_file_locations},\n\tmorph_locations = {self.morph_locations},\n\t' \
               f'material_file_locations = {self.material_file_locations},\n\tmaterial_locations = {self.material_locations},\n\t' \
               f'anim_file_locations = {self.anim_file_locations},\n\tanim_locations = {self.anim_locations},\n\t' \
               f'scene_anim_locations = {self.scene_anim_locations},\n\tskeleton_locations = {self.skeleton_locations}\n )'

    
    def constructor_common(self, a3: int, a5: int, a6: int, a7: int):
        self.base = a3
        self.field_80 = a5
        self.field_84 = a6
        self.field_88 = a7
    
    def get_resource_location(self, i: int, buffer_bytes) -> resource_location:
        assert(i < self.resource_locations.size())
        
        begin_idx = self.resource_locations.m_data + i * sizeof(resource_location)
        end_idx = begin_idx + sizeof(resource_location)
        v16 = resource_location.from_buffer_copy(buffer_bytes[begin_idx:end_idx])
        return v16
    
    def get_mash_data(self, offset: int) -> int:
        assert(self.base != 0)
        return (offset + self.base);

    def get_type_start_idxs(self, p_type: int):
        assert(p_type > RESOURCE_KEY_TYPE_NONE and p_type < RESOURCE_KEY_TYPE_Z)
        
        return self.type_start_idxs[p_type];

    def get_resource(self, loc: resource_location):
        assert(not self.resource_locations.empty())
        
        v5 = self.get_mash_data(loc.m_offset)
        return v5

    def get_resource1(self, resource_id: resource_key):
        assert(resource_id.is_set())

        assert(resource_id.get_type() != RESOURCE_KEY_TYPE_NONE)

        v7 = 0
        mash_data_size: int = 0
        
        is_found, found_dir, found_loc = self.find_resource(resource_id)
        if is_found:
            mash_data_size = found_loc.m_size
            v7 = found_dir.get_resource(found_loc, a4)
        
        return v7, mash_data_size

    def tlresource_type_to_vector(self, a2: int):
        match a2:
            case 1:
                return self.texture_locations;
            case 2:
                return self.mesh_file_locations;
            case 3:
                return self.mesh_locations;
            case 4:
                return self.morph_file_locations;
            case 5:
                return self.morph_locations;
            case 6:
                return self.material_file_locations;
            case 7:
                return self.material_locations;
            case 8:
                return self.anim_file_locations;
            case 9:
                return self.anim_locations;
            case 10:
                return self.scene_anim_locations;
            case 11:
                return self.skeleton_locations;
            case 13:
                return self.texture_locations;
            case 14:
                return self.texture_locations;
            case 15:
                return self.texture_locations;
            case _:
                assert(0 and "invalid tlresource type");

    def get_resource_count(self, p_type: int):
        assert(p_type > RESOURCE_KEY_TYPE_NONE and p_type < RESOURCE_KEY_TYPE_Z)
        return self.type_end_idxs[p_type]

    def get_tlresource_count(self, a1: int) -> int:
        locations = self.tlresource_type_to_vector(a1);
        return locations.size();
                
    def un_mash_start(self, a4: generic_mash_data_ptrs, buffer_bytes) -> generic_mash_data_ptrs:
        a4.rebase(8)
        
        a4 = self.parents.un_mash(a4)
        
        a4 = self.resource_locations.custom_un_mash__resource_location(a4)
        
        a4 = self.texture_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.mesh_file_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.mesh_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.morph_file_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.morph_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.material_file_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.material_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.anim_file_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.anim_locations.custom_un_mash__tlresource_location(a4)
        
        a4 = self.scene_anim_locations.custom_un_mash__tlresource_location(a4)
         
        a4 = self.skeleton_locations.custom_un_mash__tlresource_location(a4)
        
        def validate(vector, tlresource_type):
            for i in range(vector.m_size):
                begin = vector.m_data + i * sizeof(tlresource_location)
                tlres_loc = tlresource_location.from_buffer_copy(buffer_bytes[begin : begin + sizeof(tlresource_location)])
            
                if tlresource_type == TLRESOURCE_TYPE_TEXTURE:
                    print(tlres_loc)
            
                assert(tlres_loc.get_type() == tlresource_type)
        
        validate(self.texture_locations, TLRESOURCE_TYPE_TEXTURE)
        
        validate(self.mesh_file_locations, TLRESOURCE_TYPE_MESH_FILE)
        
        validate(self.mesh_locations, TLRESOURCE_TYPE_MESH)
        
        validate(self.morph_file_locations, TLRESOURCE_TYPE_MORPH_FILE)
        
        validate(self.morph_locations, TLRESOURCE_TYPE_MORPH)
        
        validate(self.material_file_locations, TLRESOURCE_TYPE_MATERIAL_FILE)
        
        validate(self.material_locations, TLRESOURCE_TYPE_MATERIAL)
        
        validate(self.anim_file_locations, TLRESOURCE_TYPE_ANIM_FILE)
        
        validate(self.anim_locations, TLRESOURCE_TYPE_ANIM)
        
        validate(self.scene_anim_locations, TLRESOURCE_TYPE_SCENE_ANIM)
        
        validate(self.skeleton_locations, TLRESOURCE_TYPE_SKELETON)
        
        return a4

assert(sizeof(resource_directory) == 0x2C4)

DEV_MODE = 1

for file in fileList:
    name_pak, ext = splitext(file)
    if ext == ".XBPACK":
    
        print("Resource pack:", file)
        with io.open(file, mode="rb") as rPack:
        
            buffer_bytes = rPack.read()
            print("0x%02X" % buffer_bytes[0])
            print("0x%02X" % buffer_bytes[1])
            print(len(buffer_bytes))
            
            rPack.seek(0, 2)
            numOfBytes = rPack.tell()
            print("Total Size:", numOfBytes, "bytes")
            
            pack_header = resource_pack_header.from_buffer_copy(buffer_bytes[0:sizeof(resource_pack_header)])

            rpVersion = pack_header.field_0.field_0

            if rpVersion == 14:
                print("Game: Ultimate Spider-Man NTSC 1.0")
            elif rpVersion == 10:
                print("Game: Ultimate Spider-Man NTSC 06/20/2005 Prototype")

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
            
            v16 = cur_ptr + sizeof(resource_directory)
            
            mash_data_ptrs = generic_mash_data_ptrs()
            mash_data_ptrs.field_0 = v16
            mash_data_ptrs.field_4 = directory_offset + mash_header.field_8
            print(mash_data_ptrs)

            assert(directory_offset % 4 == 0)
    
            directory.un_mash_start(mash_data_ptrs, buffer_bytes)
            
            directory.constructor_common(pack_header.res_dir_mash_size, 0, pack_header.field_20 - pack_header.res_dir_mash_size, pack_header.field_24)
            
            assert(directory.get_tlresource_count( TLRESOURCE_TYPE_MESH_FILE ) == directory.get_resource_count( RESOURCE_KEY_TYPE_MESH_FILE_STRUCT ))
            
            assert(directory.get_tlresource_count( TLRESOURCE_TYPE_MATERIAL_FILE ) == directory.get_resource_count( RESOURCE_KEY_TYPE_MATERIAL_FILE_STRUCT ))

            if DEV_MODE == 1:
                print("\nDeveloper info:\n")
                
                versions = pack_header.field_0
                print("RESOURCE_PACK_VERSION", versions.field_0)
                print("RESOURCE_ENTITY_MASH_VERSION", versions.field_4)
                print("RESOURCE_NOENTITY_MASH_VERSION", versions.field_8)
                print("RESOURCE_AUTO_MASH_VERSION", versions.field_C)
                print("RESOURCE_RAW_MASH_VERSION", versions.field_10)
                
                print("directory_offset", hex(directory_offset))
                print("base = 0x%04X" % base)
                
                print("mash_header", hex(mash_header.field_8))
            
           
            folder = name_pak
            try:
                os.mkdir(folder)
            except OSError:
                print ("Creation of the directory %s failed" % folder)
            else:
                print ("Successfully created the directory %s " % folder)
                
            for i in range(directory.resource_locations.size()):
                
                res_loc: resource_location = directory.get_resource_location(i, buffer_bytes)
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
                
                #print("{0:d} {1:#x}".format(mash_data_size, resource_idx))
           
           
            print("\n")
            

print("\nDone.")
