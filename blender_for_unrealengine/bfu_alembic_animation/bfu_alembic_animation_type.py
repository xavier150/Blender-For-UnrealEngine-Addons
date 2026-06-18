# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from pathlib import Path
from typing import List, Any, Dict, Optional
import bpy
from .. import bfu_basics
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType, BFU_ObjectAssetClass, AssetToExport, AssetDataSearchMode
from .. import bfu_base_object
from .. import bfu_socket
from .. import bfu_light_map
from .. import bfu_nanite
from .. import bfu_vertex_color
from .. import bfu_material
from .. import bfu_lod
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum
from .. import bfu_export_filter
from .. import bfu_alembic_animation
from .. import bfu_base_object
from . import bfu_export_procedure
from . import bfu_export_alembic_package
from . import bfu_alembic_animation_utils

class BFU_AlembicAnimation(BFU_ObjectAssetClass):
    def __init__(self):
        super().__init__()
        self.use_materials = True


# ###################################################################
# # Asset Root Class
# ###################################################################

    def support_asset_type(self, data: Any, details: Any = None) -> bool:
        if not isinstance(data, bpy.types.Object):
            return False
        if details is not None:
            return False
        
        if bfu_alembic_animation.bfu_alembic_animation_props.get_object_export_as_alembic_animation(data):
            return True
        return False

    def get_asset_type(self, data: Any, details: Any = None) -> AssetType:
        return AssetType.ANIM_ALEMBIC
    
    def can_export_asset_type(self) -> bool:
        return bfu_export_filter.bfu_export_filter_utils.get_use_alembic_export()

    def get_asset_import_directory_path(self, data: Any, details: Any = None, extra_path: Optional[Path] = None) -> Path:
        dirpath = bfu_base_object.bfu_base_obj_utils.get_obj_import_location(data)
        return dirpath if extra_path is None else dirpath / extra_path  # Add extra path if provided

# ###################################################################
# # Asset Package Management
# ###################################################################

    def get_package_file_prefix(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            return bpy.context.scene.bfu_alembic_animation_prefix_export_name  # type: ignore
        return ""

    def get_export_file_path(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            scene = bpy.context.scene
            return scene.bfu_export_alembic_file_path  # type: ignore[attr-defined]
        return ""
    
    def get_package_file_type(self, data: bpy.types.Object, details: Any = None) -> BFU_FileTypeEnum:
        return bfu_export_procedure.get_obj_export_file_type(data)

    def get_asset_folder_path(self, data: bpy.types.Object, details: Any = None) -> Path:
        # Add alembic sub folder path
        if data.bfu_create_sub_folder_with_alembic_name:  # type: ignore[attr-defined]
            sub_folder = bfu_basics.valid_file_name(data.name)
            return Path(sub_folder) / super().get_asset_folder_path(data, details)

        return super().get_asset_folder_path(data, details)
    
# ###################################################################
# # UI
# ###################################################################

    def draw_ui_export_procedure(self, layout: bpy.types.UILayout, context: bpy.types.Context, data: bpy.types.Object) -> bpy.types.UILayout:
        return bfu_export_procedure.draw_object_export_procedure(layout, data)

# ####################################################################
# # Asset Construction
# ####################################################################

    def get_asset_export_data(self, data: bpy.types.Object, details: Any, search_mode: AssetDataSearchMode) -> List[AssetToExport]:       
        asset_list: List[AssetToExport] = []

        # One asset per alembic animation pack
        asset = AssetToExport(self, data.name, AssetType.ANIM_ALEMBIC)
        asset.set_import_name(self.get_package_file_name(data, without_extension=True))
        asset.set_import_dirpath(self.get_asset_import_directory_path(data))
    
        if search_mode.search_packages():
            pak = asset.add_asset_package(data.name, ["Alembic"])
            self.set_package_file(pak, data, details)

            if search_mode.search_package_content():
                pak.add_objects(bfu_base_object.bfu_base_obj_utils.get_exportable_objects(data))
                frame_range = bfu_alembic_animation_utils.get_desired_alembic_start_end_range(data)
                pak.set_frame_range(frame_range[0], frame_range[1])
                pak.export_function = bfu_export_alembic_package.process_alembic_animation_export_from_package

        # Set the additional data in the asset, add asset to the list and return the list.
        self.set_additional_data_in_asset(asset, data, details, search_mode)
        asset_list.append(asset)
        return asset_list


    def get_asset_additional_data(self, data: bpy.types.Object, details: Any, search_mode: AssetDataSearchMode) -> Dict[str, Any]:
        additional_data: Dict[str, Any] = {}
        # Sockets
        if data:
            additional_data['Sockets'] = bfu_socket.bfu_socket_utils.get_skeletal_mesh_socket_data(data)

        additional_data.update(bfu_lod.bfu_lod_utils.get_lod_additional_data(data, AssetType.STATIC_MESH))
        additional_data.update(bfu_vertex_color.bfu_vertex_color_utils.get_vertex_color_additional_data(data, AssetType.STATIC_MESH))
        additional_data.update(bfu_material.bfu_material_utils.get_material_asset_additional_data(data, AssetType.STATIC_MESH))
        additional_data.update(bfu_light_map.bfu_light_map_utils.get_light_map_additional_data(data, AssetType.STATIC_MESH))
        additional_data.update(bfu_nanite.bfu_nanite_utils.get_nanite_asset_additional_data(data, AssetType.STATIC_MESH))
        return additional_data

# --------------------------------------------
# Register and Unregister functions
# --------------------------------------------

def register():
    my_asset_class = BFU_AlembicAnimation()
    bfu_assets_manager.bfu_asset_manager_registred_assets.register_asset_class(my_asset_class, "Object")

def unregister():
    pass


