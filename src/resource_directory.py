from ctypes import *
from mashable_vector import *

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


RESOURCE_KEY_TYPE_NONE = 0
RESOURCE_KEY_TYPE_MESH_FILE_STRUCT = 51
RESOURCE_KEY_TYPE_MATERIAL_FILE_STRUCT = 53
RESOURCE_KEY_TYPE_Z = 70

class resource_directory(Structure):
    _fields_ = [("parents", mashable_vector),
                ("resource_locations", mashable_vector__resource_location),
                ("texture_locations", mashable_vector__tlresource_location),
                ("mesh_file_locations", mashable_vector__tlresource_location),
                ("mesh_locations", mashable_vector__tlresource_location),
                ("morph_file_locations", mashable_vector__tlresource_location),
                ("morph_locations", mashable_vector__tlresource_location),
                ("material_file_locations", mashable_vector__tlresource_location),
                ("material_locations", mashable_vector__tlresource_location),
                ("anim_file_locations", mashable_vector__tlresource_location),
                ("anim_locations", mashable_vector__tlresource_location),
                ("scene_anim_locations", mashable_vector__tlresource_location),
                ("skeleton_locations", mashable_vector__tlresource_location),
                ("field_68", mashable_vector),
                ("field_70", mashable_vector),
                ("pack_slot", c_int),
                ("base", c_int),
                ("field_80", c_int),
                ("field_84", c_int),
                ("field_88", c_int),
                ("type_start_idxs", c_int * 70),
                ("type_end_idxs", c_int * 70)
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

    def get_resource_location(self, i: int) -> resource_location:
        #print("get_resource_location", i)

        assert(i < self.resource_locations.size())

        res = self.resource_locations.m_data[i]
        return res

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

        a4 = self.parents.un_mash(a4, buffer_bytes)

        a4 = self.resource_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.texture_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.mesh_file_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.mesh_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.morph_file_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.morph_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.material_file_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.material_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.anim_file_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.anim_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.scene_anim_locations.custom_un_mash(a4, buffer_bytes)

        a4 = self.skeleton_locations.custom_un_mash(a4, buffer_bytes)

        def validate(vector, tlresource_type):
            for i in range(vector.m_size):
                tlres_loc = vector.m_data[i]

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

assert(sizeof(resource_directory) == 0x2BC)

