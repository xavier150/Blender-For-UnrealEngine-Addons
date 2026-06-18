# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from pathlib import Path
from typing import List, Any, Optional
import bpy
from . import bfu_export_collection_as_static_mesh_package
from . import bfu_export_procedure
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType, AssetToExport, AssetDataSearchMode, BFU_CollectionAssetClass
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum
from .. import bfu_base_collection
from .. import bfu_export_filter

class BFU_StaticMesh_Collection(BFU_CollectionAssetClass):
    def __init__(self):
        super().__init__()
        self.use_lods = True
        self.use_materials = True


# ###################################################################
# # Asset Root Class
# ###################################################################

    def support_asset_type(self, data: Any, details: Any = None) -> bool:
        if not isinstance(data, bpy.types.Collection):
            return False
        if details is not None:
            return False
        return True

    def get_asset_type(self, data: Any, details: Any = None) -> AssetType:
        return AssetType.COLLECTION_AS_STATIC_MESH
    
    def can_export_asset_type(self) -> bool:
        return bfu_export_filter.bfu_export_filter_utils.get_use_static_collection_export()

    def get_asset_import_directory_path(self, data: Any, details: Any = None, extra_path: Optional[Path] = None) -> Path:
        dirpath: Path = bfu_base_collection.bfu_base_col_utils.get_col_import_location(data)
        return dirpath if extra_path is None else dirpath / extra_path  # Add extra path if provided
    
# ###################################################################
# # Asset Package Management
# ###################################################################

    def get_package_file_prefix(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            return bpy.context.scene.bfu_static_mesh_prefix_export_name  # type: ignore
        return ""
    
    def get_export_file_path(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            scene = bpy.context.scene
            return scene.bfu_export_static_mesh_file_path  # type: ignore[attr-defined]
        return ""

    def get_package_file_type(self, data: bpy.types.Collection, details: Any = None) -> BFU_FileTypeEnum:
        return bfu_export_procedure.get_col_export_type(data)

# ###################################################################
# # UI
# ###################################################################

    def draw_ui_export_procedure(self, layout: bpy.types.UILayout, context: bpy.types.Context, data: bpy.types.Collection) -> bpy.types.UILayout:
        return bfu_export_procedure.draw_col_export_procedure(layout, data)

# ####################################################################
# # Asset Construction
# ####################################################################

    def get_asset_export_data(self, data: bpy.types.Collection, details: Any, search_mode: AssetDataSearchMode) -> List[AssetToExport]:
        
        asset_list: List[AssetToExport] = []

        # One asset per scene collection.
        asset = AssetToExport(self, data.name, AssetType.COLLECTION_AS_STATIC_MESH)
        asset.set_import_name(self.get_package_file_name(data, without_extension=True))
        asset.set_import_dirpath(self.get_asset_import_directory_path(data))

        if search_mode.search_packages():
            pak = asset.add_asset_package(data.name, ["Collection"])
            self.set_package_file(pak, data, details)
                    
            if search_mode.search_package_content():
                pak.set_collection(data)
                pak.export_function = bfu_export_collection_as_static_mesh_package.process_collection_as_static_mesh_export_from_package
        
        # Set the additional data in the asset, add asset to the list and return the list.
        self.set_additional_data_in_asset(asset, data, details, search_mode)
        asset_list.append(asset)
        return asset_list



# --------------------------------------------
# Register and Unregister functions
# --------------------------------------------

def register():
    my_asset_class = BFU_StaticMesh_Collection()
    bfu_assets_manager.bfu_asset_manager_registred_assets.register_asset_class(my_asset_class, "Scene")

def unregister():
    pass