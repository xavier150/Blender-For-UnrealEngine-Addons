# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from typing import Dict, Any, Literal

import bpy

from .. import bfu_anim_base
from . import bfu_material_props
from .. bfu_assets_manager.bfu_asset_manager_type import AssetType


def get_gltf_export_materials(obj: bpy.types.Object, is_animation: bool = False) -> 'Literal["EXPORT", "PLACEHOLDER", "VIEWPORT", "NONE"]':
    if is_animation:
        if bfu_anim_base.bfu_anim_base_props.get_object_export_animation_without_mesh(obj):
            return "NONE"
        elif bfu_anim_base.bfu_anim_base_props.get_object_export_animation_without_materials(obj):
            return "NONE"

    if bfu_material_props.get_object_export_materials(obj):
        return "EXPORT"
    else:
        return "PLACEHOLDER"

def get_gltf_export_textures(obj: bpy.types.Object, is_animation: bool = False) -> 'Literal["AUTO", "JPEG", "WEBP", "NONE"]':
    if is_animation:
        if bfu_anim_base.bfu_anim_base_props.get_object_export_animation_without_mesh(obj):
            return "NONE"
        elif bfu_anim_base.bfu_anim_base_props.get_object_export_animation_without_materials(obj):
            return "NONE"  
        elif bfu_anim_base.bfu_anim_base_props.get_object_export_animation_without_textures(obj):
            return "NONE"

    if bfu_material_props.get_object_export_textures(obj) and bfu_material_props.get_object_export_materials(obj):
        return "AUTO"
    else:
        return "NONE"

def get_material_asset_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    return asset_data

def get_material_asset_additional_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    if obj:

        if asset_type in [AssetType.STATIC_MESH, AssetType.SKELETAL_MESH]:
            # Set import material/texture only is export materials/textures is enabled
            asset_data["import_materials"] = bfu_material_props.get_object_export_materials(obj)
            asset_data["import_textures"] = bfu_material_props.get_object_export_textures(obj)

            asset_data["flip_normal_map_green_channel"] = bfu_material_props.get_object_flip_normal_map_green_channel(obj)
            asset_data["reorder_material_to_fbx_order"] = bfu_material_props.get_object_reorder_material_to_fbx_order(obj)
            asset_data["material_search_location"] = bfu_material_props.get_object_material_search_location(obj)
    return asset_data