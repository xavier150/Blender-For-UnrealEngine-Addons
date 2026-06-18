# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Dict, Any, TYPE_CHECKING
from .. bfu_assets_manager.bfu_asset_manager_type import AssetType

try:
    from typing import Literal
except ImportError:
    # Can't use Literal in Blender 2.8 that still use Python 3.7
    # Dummy class for Literal typing in Python versions < 3.8
    class Literal:
        def __class_getitem__(cls, item):
            return str

def get_gltf_export_materials(obj: bpy.types.Object, is_animation: bool = False) -> Literal["EXPORT", "PLACEHOLDER", "VIEWPORT", "NONE"]:
    if is_animation:
        if obj.bfu_export_animation_without_mesh:
            return "NONE"
        elif obj.bfu_export_animation_without_materials:
            return "NONE"

    if obj.bfu_export_materials:
        return "EXPORT"
    else:
        return "PLACEHOLDER"

def get_gltf_export_textures(obj: bpy.types.Object, is_animation: bool = False) -> Literal["AUTO", "JPEG", "WEBP", "NONE"]:
    if is_animation:
        if obj.bfu_export_animation_without_mesh:
            return "NONE"
        elif obj.bfu_export_animation_without_materials:
            return "NONE"  
        elif obj.bfu_export_animation_without_textures:
            return "NONE"

    if obj.bfu_export_textures and obj.bfu_export_materials:
        return "AUTO"
    else:
        return "NONE"

def get_material_asset_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    return asset_data

def get_material_asset_additional_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    if obj:

        if TYPE_CHECKING:
            class FakeObject(bpy.types.Object):
                bfu_export_materials: bool = False
                bfu_export_textures: bool = False
                bfu_flip_normal_map_green_channel: bool = False
                bfu_reorder_material_to_fbx_order: bool = False
                bfu_material_search_location: str = ""
            obj = FakeObject()

        if asset_type in [AssetType.STATIC_MESH, AssetType.SKELETAL_MESH]:
            # Set import material/texture only is export materials/textures is enabled
            asset_data["import_materials"] = obj.bfu_import_materials
            asset_data["import_textures"] = obj.bfu_import_textures

            asset_data["flip_normal_map_green_channel"] = obj.bfu_flip_normal_map_green_channel
            asset_data["reorder_material_to_fbx_order"] = obj.bfu_reorder_material_to_fbx_order
            asset_data["material_search_location"] = obj.bfu_material_search_location
    return asset_data