# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import TYPE_CHECKING
from . import bfu_basics
from . import bfu_anim_action
from . import bfu_anim_nla
from . import bfu_export_nomenclature
from . bfu_anim_action.bfu_anim_action_props import BFU_AnimNamingTypeEnum

def get_collection_file_name(collection: bpy.types.Collection, desired_name: str = "", fileType: str = ".fbx") -> str:
    # Generate assset file name for skeletal mesh
    
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("Scene is None")

    if TYPE_CHECKING:
        class FakeScene(bpy.types.Scene):
            bfu_static_mesh_prefix_export_name: str = ""
            bfu_static_mesh_prefix_export_name: str = ""
        scene = FakeScene()

    if desired_name:
        return bfu_basics.valid_file_name(scene.bfu_static_mesh_prefix_export_name + desired_name + fileType)
    return bfu_basics.valid_file_name(scene.bfu_static_mesh_prefix_export_name + collection.name + fileType)


def get_nonlinear_animation_file_name(obj: bpy.types.Object, fileType: str = ".fbx") -> str:
    # Generate action file name

    scene = bpy.context.scene


    if bfu_anim_action.bfu_anim_action_props.get_object_anim_naming_type_enum(obj) == BFU_AnimNamingTypeEnum.INCLUDE_ARMATURE_NAME:
        armature_name: str = obj.name+"_"
    elif bfu_anim_action.bfu_anim_action_props.get_object_anim_naming_type_enum(obj) == BFU_AnimNamingTypeEnum.ACTION_NAME:
        armature_name: str = ""
    elif bfu_anim_action.bfu_anim_action_props.get_object_anim_naming_type_enum(obj) == BFU_AnimNamingTypeEnum.INCLUDE_CUSTOM_NAME:
        armature_name: str = bfu_anim_action.bfu_anim_action_props.get_object_anim_naming_custom(obj) + "_"
    else:
        armature_name: str = ""

    return bfu_basics.valid_file_name(
        bfu_export_nomenclature.bfu_export_nomenclature_props.get_anim_prefix_export_name(scene)
        + armature_name
        + bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_export_name(obj)
        + fileType
    )
