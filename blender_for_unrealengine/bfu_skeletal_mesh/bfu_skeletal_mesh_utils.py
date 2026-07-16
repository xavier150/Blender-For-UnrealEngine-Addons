# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import fnmatch
from typing import List

import bpy

from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType
from .. import bfu_addon_prefs
from . import bfu_skeletal_mesh_props

def get_socket_in_desired_childs(obj: bpy.types.Object) -> List[bpy.types.Object]:
    socket_objs: List[bpy.types.Object] = []
    for obj in bfu_utils.get_export_desired_childs(obj):
        if fnmatch.fnmatchcase(obj.name, "SOCKET*"):
            socket_objs.append(obj)
    return socket_objs

def deselect_socket(obj: bpy.types.Object):
    # With skeletal mesh the Socket musts be not exported,
    # Because Unreal Engine will import it as bones.
    socket_objs = get_socket_in_desired_childs(obj)
    for obj in socket_objs:
        obj.select_set(False)


def is_skeletal_mesh(obj: bpy.types.Object):
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_primary_supported_asset_class(obj)
    if asset_class:
        if asset_class.get_asset_type(obj) == AssetType.SKELETAL_MESH:
            return True
    return False

def is_not_skeletal_mesh(obj: bpy.types.Object):
    return not is_skeletal_mesh(obj)

def get_armature_root_bones(armature: bpy.types.Object) -> List[bpy.types.Bone]:
    root_bones: List[bpy.types.Bone] = []
    if isinstance(armature.data, bpy.types.Armature):

        if bfu_skeletal_mesh_props.get_object_export_deform_only(armature):
            for bone in armature.data.bones:
                if bone.use_deform:
                    rootBone = bfu_basics.get_root_bone_parent(bone)
                    if rootBone not in root_bones:
                        root_bones.append(rootBone)

        else:
            for bone in armature.data.bones:
                if bone.parent is None:
                    root_bones.append(bone)
    return root_bones

def get_desired_export_armature_name(obj: bpy.types.Object) -> str:
    addon_prefs = bfu_addon_prefs.get_addon_preferences()
    single_root = len(get_armature_root_bones(obj)) == 1
    if addon_prefs.add_skeleton_root_bone or single_root != 1:
        return addon_prefs.skeleton_root_bone_name
    return "Armature"