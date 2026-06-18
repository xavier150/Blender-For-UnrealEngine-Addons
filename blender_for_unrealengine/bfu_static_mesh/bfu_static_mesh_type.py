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
from . import bfu_export_static_mesh_package
from . import bfu_export_procedure
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType, AssetToExport, AssetDataSearchMode, BFU_ObjectAssetClass
from .. import bfu_socket
from .. import bfu_light_map
from .. import bfu_nanite
from .. import bfu_vertex_color
from .. import bfu_material
from .. import bfu_lod
from .. import bfu_base_object
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum
from .. import bfu_export_filter
from .. import bfu_alembic_animation
from .. import bfu_groom

class BFU_StaticMesh(BFU_ObjectAssetClass):
    def __init__(self):
        super().__init__()
        self.use_lods = True
        self.use_materials = True

# ###################################################################
# # Asset Root Class
# ###################################################################

    def support_asset_type(self, data: Any, details: Any = None) -> bool:
        if not isinstance(data, bpy.types.Object):
            return False
        if details is not None:
            return False
        
        if data.type == "ARMATURE":
            if data.bfu_export_skeletal_mesh_as_static_mesh:  # type: ignore
                return True
            return False
        
        if data.type == "CURVE":
            if data.bfu_export_spline_as_static_mesh:  # type: ignore
                return True
            return False
        
        if data.type == "CAMERA":
            # Can't export camera as static mesh
            return False

        elif bfu_groom.bfu_groom_props.get_object_export_as_groom_simulation(data):  # type: ignore
            return False
        
        elif bfu_alembic_animation.bfu_alembic_animation_props.get_object_export_as_alembic_animation(data):
            return False
        return True

    def get_asset_type(self, data: Any, details: Any = None) -> AssetType:
        return AssetType.STATIC_MESH

    def can_export_asset_type(self) -> bool:
        return bfu_export_filter.bfu_export_filter_utils.get_use_static_export()

    def get_asset_import_directory_path(self, data: bpy.types.Object, details: Any = None, extra_path: Optional[Path] = None) -> Path:
        dirpath = bfu_base_object.bfu_base_obj_utils.get_obj_import_location(data)
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

    def get_package_file_type(self, data: bpy.types.Object, details: Any = None) -> BFU_FileTypeEnum:
        return bfu_export_procedure.get_obj_export_file_type(data)

# ###################################################################
# # UI
# ###################################################################

    def draw_ui_export_procedure(self, layout: bpy.types.UILayout, context: bpy.types.Context, data: bpy.types.Object) -> bpy.types.UILayout:
        return bfu_export_procedure.draw_object_export_procedure(layout, data)

# ####################################################################
# # Asset Construction
# ####################################################################


    def get_asset_export_data(self, data: bpy.types.Object, details: Any, search_mode: AssetDataSearchMode)-> List[AssetToExport]:
        
        if data.bfu_export_as_lod_mesh: # type: ignore[attr-defined]
            # Asset exported as Lod will be included as package content in the Lod0 Asset.
            return []
        
        asset_list: List[AssetToExport] = []

        # One asset per static mesh and on package per LOD
        asset = AssetToExport(self, data.name, AssetType.STATIC_MESH)
        asset.set_import_name(self.get_package_file_name(data, without_extension=True))
        asset.set_import_dirpath(self.get_asset_import_directory_path(data))

        if search_mode.search_packages():
            pak = asset.add_asset_package(data.name, ["Lod0"])
            self.set_package_file(pak, data, details)

            if search_mode.search_package_content():
                pak.add_objects(bfu_base_object.bfu_base_obj_utils.get_exportable_objects(data))
                pak.export_function = bfu_export_static_mesh_package.process_static_mesh_export_from_package


        for i in range(1, bfu_lod.bfu_lod_utils.get_last_lod_index() + 1):
            target = getattr(data, f"bfu_lod_target{i}", None)
            if target and target.name in bpy.data.objects:

                if search_mode.search_packages():
                    target_pak = asset.add_asset_package(target.name, [f"Lod{i}"])
                    self.set_package_file(target_pak, target, details)

                    if search_mode.search_package_content():
                        target_pak.add_objects(bfu_base_object.bfu_base_obj_utils.get_exportable_objects(target))
                        target_pak.export_function = bfu_export_static_mesh_package.process_static_mesh_export_from_package

        
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
    my_asset_class = BFU_StaticMesh()
    bfu_assets_manager.bfu_asset_manager_registred_assets.register_asset_class(my_asset_class, "Object")

def unregister():
    pass
