from . import edit_files

has_valid_parent_function = '''
    def has_valid_parent(self, objects):
        par = self.parent
        if par in objects:
            if self._tag == 'OB':
                par_type = self.bdata.parent_type
                if par_type in {'OBJECT', 'BONE'}:
                    return True
                else:
                    print("Sorry, “{}” parenting type is not supported".format(par_type))
                    return False
            return True
        return False
'''

def update_fbx_utils(file_path, version):
    add_re_import(file_path)
    edit_files.add_quaternion_import(file_path)
    add_support_for_custom_kind(file_path)
    new_func = add_is_leg_bone_func(has_valid_parent_function, file_path)
    new_func = add_is_rightside_bone_func(new_func, file_path)
    new_func = add_is_reverse_direction_bone_func(new_func, file_path)
    new_func = add_is_basic_bone_func(new_func, file_path)
    new_func = add_aling_matrix_funcs(new_func, file_path)
    add_disable_free_scale_animation(file_path)


def add_re_import(file_path):
    # 4.1 and older
    search_lines1 = '''
import math
import time
'''

    content_to_add = '''import re
'''
    edit_files.add_after_lines(file_path, search_lines1, content_to_add)

def add_support_for_custom_kind(file_path):
    # Add custom in kinds
    old_kinds = '''
        'CAMERA_FOCUS_DISTANCE': ("FocusDistance", "FocusDistance", ("FocusDistance",)),'''

    old_kinds_3_2 = '''
        'CAMERA_FOCAL': ("FocalLength", "FocalLength", ("FocalLength",)),'''

    new_kinds = '''
        'CUSTOM': ("Value", "Value", ("Value",)),'''

    if edit_files.lines_exist(file_path, old_kinds):
        edit_files.add_after_lines(file_path, old_kinds, new_kinds)
    elif edit_files.lines_exist(file_path, old_kinds_3_2):
        edit_files.add_after_lines(file_path, old_kinds_3_2, new_kinds)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")

    old_kinds_init = '''
        self.fbx_group = [self.kinds[kind][0]]
        self.fbx_gname = [self.kinds[kind][1]]
        self.fbx_props = [self.kinds[kind][2]]
'''

    new_kinds_init = '''
        if kind == 'CUSTOM':
            self.fbx_group = [default_values[0]]
            self.fbx_gname = [default_values[0]]
            self.fbx_props = [(default_values[0],)]
            default_values = (0.0,)
        else:
            self.fbx_group = [self.kinds[kind][0]]
            self.fbx_gname = [self.kinds[kind][1]]
            self.fbx_props = [self.kinds[kind][2]]
'''

    edit_files.replace_lines(file_path, old_kinds_init, new_kinds_init)

def add_is_leg_bone_func(previous_func, file_path):
    # Add aling matrix functions

    new_function = '''
    LEG_NAME_PATTERN = re.compile(r'[^a-zA-Z]?(thigh|calf)([^a-zA-Z]|$)', re.IGNORECASE)

    def is_leg_bone(self):
        return self.LEG_NAME_PATTERN.match(self.name) != None
'''

    edit_files.add_after_lines(file_path, previous_func, new_function)

    return new_function

def add_is_rightside_bone_func(previous_func, file_path):
    # Add aling matrix functions

    new_function = '''
    SYMMETRY_RIGHTSIDE_NAME_PATTERN = re.compile(r'(.+[_\.])(r|R)(\.\d+)?$')

    def is_rightside_bone(self, objects):
        if self.name.lower() == 'ik_hand_gun':
            return True
        match = self.SYMMETRY_RIGHTSIDE_NAME_PATTERN.match(self.name)
        if match:
            counterpartname = match.group(1) + ('l' if match.group(2) == 'r' else 'L') + (match.group(3) if match.group(3) else '')
            for i in objects:
                if i != self and i._tag == 'BO' and i.name == counterpartname:
                    #print(self.name, counterpartname)
                    return True
        return False
'''

    edit_files.add_after_lines(file_path, previous_func, new_function)

    return new_function

def add_is_reverse_direction_bone_func(previous_func, file_path):
    # Add aling matrix functions

    new_function = '''
    def is_reverse_direction_bone(self, scene_data):
        if scene_data.settings.use_ue_mannequin_bone_alignment and self.is_leg_bone():
            return not self.is_rightside_bone(scene_data.objects)
        return self.is_rightside_bone(scene_data.objects)
'''

    edit_files.add_after_lines(file_path, previous_func, new_function)

    return new_function

def add_aling_matrix_funcs(previous_func, file_path):
    # Add aling matrix functions


    new_function = '''
    def get_bone_align_matrix(self, scene_data):
        bone_aligns = scene_data.settings.bone_align_matrix_dict
        if bone_aligns and self.armature.name in bone_aligns:
            if self.bdata.name in bone_aligns[self.armature.name]:
                return bone_aligns[self.armature.name][self.bdata.name][0]
        return None
    
    def get_parent_bone_align_matrix_inv(self, scene_data):
        if self.bdata.parent:
            bone_aligns = scene_data.settings.bone_align_matrix_dict
            if bone_aligns and self.armature.name in bone_aligns:
                if self.bdata.parent.name in bone_aligns[self.armature.name]:
                    return bone_aligns[self.armature.name][self.bdata.parent.name][1]
        return None
'''

    edit_files.add_after_lines(file_path, previous_func, new_function)


    old_FBXExportSettings = '''
    "bone_correction_matrix", "bone_correction_matrix_inv",'''

    new_FBXExportSettings = '''
    "reverse_direction_bone_correction_matrix", "reverse_direction_bone_correction_matrix_inv",'''

    edit_files.add_after_lines(file_path, old_FBXExportSettings, new_FBXExportSettings)

    old_use = '''
            # Apply the bone correction.
            if scene_data.settings.bone_correction_matrix:
                matrix = matrix @ scene_data.settings.bone_correction_matrix
'''

    new_use = '''
            # Apply the bone correction.
            mat_align = self.get_bone_align_matrix(scene_data)
            if mat_align:
                matrix = matrix @ mat_align
            if scene_data.settings.reverse_direction_bone_correction_matrix and self.is_reverse_direction_bone(scene_data):
                matrix = matrix @ scene_data.settings.reverse_direction_bone_correction_matrix
            elif scene_data.settings.bone_correction_matrix:
                matrix = matrix @ scene_data.settings.bone_correction_matrix
'''

    edit_files.replace_lines(file_path, old_use, new_use)

    old_use2 = '''
            # If we have a bone parent we need to undo the parent correction.
            if not is_global and scene_data.settings.bone_correction_matrix_inv and parent and parent.is_bone:
                matrix = scene_data.settings.bone_correction_matrix_inv @ matrix
'''

    new_use2 = '''
            # If we have a bone parent we need to undo the parent correction.
            if not is_global and scene_data.settings.bone_correction_matrix_inv and parent and parent.is_bone:
                par_mat_align_inv = self.get_parent_bone_align_matrix_inv(scene_data)
                if par_mat_align_inv:
                    matrix = par_mat_align_inv @ matrix
                if scene_data.settings.reverse_direction_bone_correction_matrix_inv and parent.is_reverse_direction_bone(scene_data):
                    matrix = scene_data.settings.reverse_direction_bone_correction_matrix_inv @ matrix
                elif scene_data.settings.bone_correction_matrix_inv:
                    matrix = scene_data.settings.bone_correction_matrix_inv @ matrix
'''

    edit_files.replace_lines(file_path, old_use2, new_use2)
    return new_function

def add_is_basic_bone_func(previous_func, file_path):
    # Add aling matrix functions

    new_function = '''
    BASIC_NAME_PATTERN1 = re.compile(r'^(root|pelvis|spine[_\.]\d+|neck[_\.]\d+|head)$', re.IGNORECASE)
    BASIC_NAME_PATTERN2 = re.compile(r'^(clavicle|upperarm|lowerarm|hand|thigh|calf|foot|ball|thumb)[_\.][lr]$', re.IGNORECASE)
    BASIC_NAME_PATTERN3 = re.compile(r'^(index|middle|ring|pinky)[_\.](\d+|metacarpal)[_\.][lr]$', re.IGNORECASE)
    BASIC_NAME_PATTERN4 = re.compile(r'^(bigtoe|indextoe|middletoe|ringtoe|littletoe)[_\.](\d+|metacarpal)[_\.][lr]$', re.IGNORECASE)

    def is_basic_bone(self):
        if self.BASIC_NAME_PATTERN1.match(self.name):
            return True
        if self.BASIC_NAME_PATTERN2.match(self.name):
            return True
        if self.BASIC_NAME_PATTERN3.match(self.name):
            return True
        if self.BASIC_NAME_PATTERN4.match(self.name):
            return True
        return False
'''

    edit_files.add_after_lines(file_path, previous_func, new_function)
    return new_function

def add_disable_free_scale_animation(file_path):

    old_FBXExportSettings = '''
    "reverse_direction_bone_correction_matrix", "reverse_direction_bone_correction_matrix_inv",
'''

    new_FBXExportSettings = '''    "use_ue_mannequin_bone_alignment", "bone_align_matrix_dict", "disable_free_scale_animation",
'''

    edit_files.add_after_lines(file_path, old_FBXExportSettings, new_FBXExportSettings)

    matrix_decompose = '''
        matrix = self.fbx_object_matrix(scene_data, rest=rest)
        loc, rot, scale = matrix.decompose()
'''

    disable_free_scale_animation = '''        if scene_data.settings.disable_free_scale_animation and self.is_basic_bone():
            scale_value = (scale.x + scale.y + scale.z) / 3.0
            if math.isclose(scale_value, 1.0, rel_tol=0.00001):
                scale_value = 1.0
            scale = Vector((scale_value, scale_value, scale_value))
'''

    edit_files.add_after_lines(file_path, matrix_decompose, disable_free_scale_animation)
