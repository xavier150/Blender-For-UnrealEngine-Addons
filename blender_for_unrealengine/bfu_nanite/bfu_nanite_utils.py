# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Dict, Any
from .. bfu_assets_manager.bfu_asset_manager_type import AssetType
from . import bfu_nanite_props
from .bfu_nanite_props import BFU_BuildNaniteMode

def get_nanite_asset_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    return asset_data

def get_nanite_asset_additional_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}
    if obj:

        if asset_type in [AssetType.STATIC_MESH, AssetType.SKELETAL_MESH]:
            build_nanite_mode: BFU_BuildNaniteMode = bfu_nanite_props.get_object_build_nanite_mode(obj)
            if build_nanite_mode.value == BFU_BuildNaniteMode.BUILD_NANITE_TRUE.value:
                asset_data["build_nanite"] = True
            elif build_nanite_mode.value == BFU_BuildNaniteMode.BUILD_NANITE_FALSE.value:
                asset_data["build_nanite"] = False
            # Keep empty for auto (The engine will decide to build or not nanite depending on the project settings)
    return asset_data