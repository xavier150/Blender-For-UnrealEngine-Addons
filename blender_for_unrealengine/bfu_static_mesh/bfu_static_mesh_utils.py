# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from .. import bfu_assets_manager
from . import bfu_export_procedure

def is_static_mesh(obj: bpy.types.Object) -> bool:  
    asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_primary_supported_asset_class(obj)
    if asset_class:
        if asset_class.get_asset_type(obj) == bfu_assets_manager.bfu_asset_manager_type.AssetType.STATIC_MESH:
            return True
    return False

def is_not_static_mesh(obj: bpy.types.Object) -> bool:
    return not is_static_mesh(obj)

def is_fbx_static_mesh(obj: bpy.types.Object) -> bool:
    if is_static_mesh(obj) and bfu_export_procedure.get_object_export_procedure(obj).is_fbx():
            return True
    return False

def is_gltf_static_mesh(obj: bpy.types.Object) -> bool:
    if is_static_mesh(obj) and bfu_export_procedure.get_object_export_procedure(obj).is_gltf():
            return True
    return False