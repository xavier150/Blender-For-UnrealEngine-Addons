# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from pathlib import Path
from typing import Any, Optional, List
import bpy
from . import bfu_export_procedure
from . import bfu_export_groom_package
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType, BFU_ObjectAssetClass, AssetDataSearchMode, AssetToExport
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum
from .. import bfu_base_object
from .. import bfu_export_filter


class BFU_Groom(BFU_ObjectAssetClass):
    def __init__(self):
        super().__init__()


# ###################################################################
# # Asset Root Class
# ###################################################################

    def support_asset_type(self, data: Any, details: Any = None) -> bool:
        if not isinstance(data, bpy.types.Object):
            return False
        if details is not None:
            return False
        if data.bfu_export_as_groom_simulation:  # type: ignore[attr-defined]
            return True
        return False

    def get_asset_type(self, data: Any, details: Any = None) -> AssetType:
        return AssetType.GROOM_SIMULATION

    def can_export_asset_type(self) -> bool:
        return bfu_export_filter.bfu_export_filter_utils.get_use_groom_simulation_export()

    def get_asset_import_directory_path(self, data: Any, details: Any = None, extra_path: Optional[Path] = None) -> Path:
        dirpath = bfu_base_object.bfu_base_obj_utils.get_obj_import_location(data)
        return dirpath if extra_path is None else dirpath / extra_path  # Add extra path if provided
    
####################################################################
# Asset Package Management
####################################################################

    def get_package_file_prefix(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            return bpy.context.scene.bfu_groom_simulation_prefix_export_name  # type: ignore[attr-defined]
        return ""

    def get_export_file_path(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            scene = bpy.context.scene
            return scene.bfu_export_groom_file_path  # type: ignore[attr-defined]
        return ""

    def get_package_file_type(self, data: bpy.types.Object, details: Any = None) -> BFU_FileTypeEnum:
        return bfu_export_procedure.get_obj_export_file_type(data)
    
####################################################################
# UI
####################################################################

    def draw_ui_export_procedure(self, layout: bpy.types.UILayout, context: bpy.types.Context, data: bpy.types.Object) -> bpy.types.UILayout:
        return bfu_export_procedure.draw_object_export_procedure(layout, data)
    
# ####################################################################
# # Asset Construction
# ####################################################################

    def get_asset_export_data(self, data: bpy.types.Object, details: Any, search_mode: AssetDataSearchMode) -> List[AssetToExport]:
                
        asset_list: List[AssetToExport] = []

        # One asset per groom object.
        asset = AssetToExport(self, data.name, AssetType.GROOM_SIMULATION)
        asset.set_import_name(self.get_package_file_name(data, without_extension=True))
        asset.set_import_dirpath(self.get_asset_import_directory_path(data))

        if search_mode.search_packages():
            pak = asset.add_asset_package(data.name, ["Lod0"])
            self.set_package_file(pak, data, details)

            if search_mode.search_package_content():
                pak.add_objects(bfu_base_object.bfu_base_obj_utils.get_exportable_objects(data))
                pak.export_function = bfu_export_groom_package.process_groom_simulation_export_from_package

        # Set the additional data in the asset, add asset to the list and return the list.
        self.set_additional_data_in_asset(asset, data, details, search_mode)
        asset_list.append(asset)
        return asset_list

# --------------------------------------------
# Register and Unregister functions
# --------------------------------------------

def register():
    my_asset_class = BFU_Groom()
    bfu_assets_manager.bfu_asset_manager_registred_assets.register_asset_class(my_asset_class, "Object")

def unregister():
    pass