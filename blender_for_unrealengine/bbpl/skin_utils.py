# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBPL -> BleuRaven Blender Python Library
#  https://github.com/xavier150/BBPL
# ----------------------------------------------

import bpy
from typing import List, Dict, Any
from .. import bbpl

def save_deform_bones(armature: bpy.types.Object) -> Dict[str, bool]:
    """
    Save the deform flag for each bone in the armature.
    Returns a dictionary of bone names and their deform flags.
    """
    saved_bones: Dict[str, bool] = {}

    for bone in armature.data.bones:  # type: ignore
        saved_bones[bone.name] = bone.use_deform  # type: ignore
    return saved_bones


def reset_deform_bones(armature: bpy.types.Object, saved_bones: Dict[str, bool]) -> None:
    """
    Reset the deform flags for each bone in the armature using the saved data.
    """
    for bone_name, use_deform in saved_bones.items():
        armature.data.bones[bone_name].use_deform = use_deform  # type: ignore


def set_all_bones_deforms(armature: bpy.types.Object, use_deform: bool) -> None:
    """
    Set the deform flag for all bones in the armature.
    """
    for bone in armature.data.bones:  # type: ignore
        bone.use_deform = use_deform


def set_bones_deforms(armature: bpy.types.Object, bone_name_list: List[str], use_deform: bool) -> None:
    """
    Set the deform flag for the specified bones in the armature.
    """
    bone_list: List[bpy.types.Bone] = []
    for bone_name in bone_name_list:
        if bone_name in armature.data.bones:  # type: ignore
            bone_list.append(armature.data.bones[bone_name])  # type: ignore
    for bone in bone_list:
        bone.use_deform = use_deform


def remove_vertex_groups(obj: bpy.types.Object) -> None:
    """
    Remove all vertex groups from the object.
    """
    for vertex_group in obj.vertex_groups:
        obj.vertex_groups.remove(vertex_group)  # type: ignore


def copy_rig_group(obj: bpy.types.Object, source: bpy.types.Object) -> None:
    """
    Copy the rigging weights from the source object to the target object.
    """
    bbpl.utils.mode_set_on_target(obj, "OBJECT")

    mod_name = "MAR_RigWeightTransfer"

    for old_mod in obj.modifiers:
        if old_mod.name == mod_name:
            obj.modifiers.remove(old_mod)  # type: ignore

    remove_vertex_groups(obj)

    mod = obj.modifiers.new(name=mod_name, type='DATA_TRANSFER')  # type: ignore
    while obj.modifiers[0].name != mod_name:
        bpy.ops.object.modifier_move_up(modifier=mod_name)  # type: ignore


    mod.object = source  # type: ignore
    mod.use_vert_data = True  # type: ignore
    mod.data_types_verts = {'VGROUP_WEIGHTS'}  # type: ignore
    bpy.ops.object.datalayout_transfer(modifier=mod_name, data_type="VGROUP_WEIGHTS")  # type: ignore
    bpy.ops.object.modifier_apply(modifier=mod_name)  # type: ignore


def apply_auto_rig_parent(
    armature: bpy.types.Object, 
    target_objects: List[bpy.types.Object], 
    parent_type: str = 'ARMATURE_AUTO', 
    white_list_bones: List[str] = [], 
    black_list_bones: List[str] = []
) -> None:
    """
    Apply an automatic rig parent to the target object using the armature.
    Optionally, specify a white list or black list of bones to control the deform flag.
    """

    save_deform = save_deform_bones(armature)

    if len(white_list_bones) > 0:
        set_all_bones_deforms(armature, False)

    set_bones_deforms(armature, white_list_bones, True)
    set_bones_deforms(armature, black_list_bones, False)

    for obj in target_objects:
        for modifier in obj.modifiers:
            modifier: bpy.types.Modifier
            if modifier.type == "ARMATURE":  # type: ignore
                obj.modifiers.remove(modifier)  # type: ignore
        remove_vertex_groups(obj)

    all_objs: List[bpy.types.Object] = []
    all_objs.append(armature)
    all_objs.extend(target_objects)
    if bpy.app.version >= (4, 0, 0):
        with bpy.context.temp_override(active_object=armature, object=armature, selected_objects=all_objs, selected_editable_objects=all_objs):  # type: ignore
            bpy.ops.object.parent_set(type=parent_type)  # type: ignore

    else:
        override_context: Dict[str, Any] = bpy.context.copy()  # type: ignore
        override_context['active_object'] = armature
        override_context['object'] = armature
        override_context['selected_objects'] = all_objs
        bpy.ops.object.parent_set(override_context, type=parent_type)  # type: ignore


    reset_deform_bones(armature, save_deform)