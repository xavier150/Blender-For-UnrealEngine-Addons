# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Any, Dict, Optional, TYPE_CHECKING
from pathlib import Path
from .. import bfu_assets_manager
from .. bfu_assets_manager.bfu_asset_manager_type import AssetType

def get_last_lod_index() -> int:
    # Support 5 LODs, this can be increased if needed.
    # LOD 0 is the main mesh, so we start from 1
    return 5

def get_lod_asset_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}

    if TYPE_CHECKING:
        class FakeObject(bpy.types.Object):
            bfu_export_as_lod_mesh: bool = False
        obj = FakeObject()

    if asset_type in [AssetType.STATIC_MESH, AssetType.SKELETAL_MESH]:
        if obj.bfu_export_as_lod_mesh:
            asset_data["import_as_lod_mesh"] = True
        else:
            asset_data["import_as_lod_mesh"] = False

    return asset_data

def get_lod_additional_data(obj: bpy.types.Object, asset_type: AssetType) -> Dict[str, Any]:
    asset_data: Dict[str, Any] = {}

    if TYPE_CHECKING:
        class FakeObject(bpy.types.Object):
            bfu_use_static_mesh_lod_group: bool = False
            bfu_static_mesh_lod_group: str = ""
            bfu_lod_target1: Optional[bpy.types.Object]
            bfu_lod_target2: Optional[bpy.types.Object]
            bfu_lod_target3: Optional[bpy.types.Object]
            bfu_lod_target4: Optional[bpy.types.Object]
            bfu_lod_target5: Optional[bpy.types.Object]
        obj = FakeObject()

    # Add lod group name
    if obj:
        if asset_type in [AssetType.STATIC_MESH]:
            if (obj.bfu_use_static_mesh_lod_group):
                asset_data["static_mesh_lod_group"] = obj.bfu_static_mesh_lod_group
            else:
                asset_data["static_mesh_lod_group"] = None

    # Add lod slots
    if obj:
        asset_class = bfu_assets_manager.bfu_asset_manager_utils.get_primary_supported_asset_class(obj)
        if asset_class:

            asset_data['level_of_details'] = {}

            def GetLodPath(lod_obj: bpy.types.Object) -> str:
                directory_path: Path = asset_class.get_package_export_directory_path(lod_obj, absolute = True)
                file_name = asset_class.get_package_file_name(lod_obj)
                return str(directory_path / file_name)

            if obj.bfu_lod_target1 is not None:
                asset_data['level_of_details']['lod_1'] = GetLodPath(obj.bfu_lod_target1)
            if obj.bfu_lod_target2 is not None:
                asset_data['level_of_details']['lod_2'] = GetLodPath(obj.bfu_lod_target2)
            if obj.bfu_lod_target3 is not None:
                asset_data['level_of_details']['lod_3'] = GetLodPath(obj.bfu_lod_target3)
            if obj.bfu_lod_target4 is not None:
                asset_data['level_of_details']['lod_4'] = GetLodPath(obj.bfu_lod_target4)
            if obj.bfu_lod_target5 is not None:
                asset_data['level_of_details']['lod_5'] = GetLodPath(obj.bfu_lod_target5)

    return asset_data