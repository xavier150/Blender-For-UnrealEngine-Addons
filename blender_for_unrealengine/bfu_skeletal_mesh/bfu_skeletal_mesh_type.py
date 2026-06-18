# SPDX-FileCopyrightText: 2018-2025 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

from pathlib import Path
from typing import List, Any, Dict, Optional, TypeGuard

import bpy

from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType, AssetToExport, AssetDataSearchMode, BFU_ObjectAssetClass
from .. import bfu_basics
from .. import bbpl
from .. import bfu_modular_skeletal_mesh
from ..bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_type import BFU_UI_ModularSkeletalSpecifiedPartsMeshItem
from .. import bfu_socket
from .. import bfu_light_map
from .. import bfu_nanite
from .. import bfu_vertex_color
from .. import bfu_material
from .. import bfu_lod
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum
from .. import bfu_base_object
from .. import bfu_export_filter
from ..bfu_export_filter.bfu_export_filter_props import BFU_ExportSelectionFilterEnum
from . import bfu_export_skeletal_mesh_package
from . import bfu_export_procedure



class BFU_SkeletalMesh(BFU_ObjectAssetClass):
    def __init__(self):
        super().__init__()
        self.use_materials = True

    @staticmethod
    def _is_specified_parts_mesh_item(details: Any) -> TypeGuard[BFU_UI_ModularSkeletalSpecifiedPartsMeshItem]:
        if isinstance(details, BFU_UI_ModularSkeletalSpecifiedPartsMeshItem):
            return True
        bl_rna = getattr(details, "bl_rna", None)
        return getattr(bl_rna, "identifier", "") == "BFU_UI_ModularSkeletalSpecifiedPartsMeshItem"


# ###################################################################
# # Asset Root Class
# ###################################################################

    def support_asset_type(self, data: Any, details: Any = None) -> bool:
        if not isinstance(data, bpy.types.Object):
            return False
        if details is not None:
            return False
        if data.bfu_export_skeletal_mesh_as_static_mesh:  # type: ignore
            return False
        if data.type == "ARMATURE":  # type: ignore
            return True
        return False

    def get_asset_type(self, data: Any, details: Any = None) -> AssetType:
        return AssetType.SKELETAL_MESH

    def can_export_asset_type(self) -> bool:
        return bfu_export_filter.bfu_export_filter_utils.get_use_skeletal_export()

    def get_asset_import_directory_path(self, data: Any, details: Any = None, extra_path: Optional[Path] = None) -> Path:
        dirpath = bfu_base_object.bfu_base_obj_utils.get_obj_import_location(data)
        return dirpath if extra_path is None else dirpath / extra_path  # Add extra path if provided

# ###################################################################
# # Asset Package Management
# ###################################################################

    def get_package_file_prefix(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            return bpy.context.scene.bfu_skeletal_mesh_prefix_export_name  # type: ignore[attr-defined]
        return ""
    
    def get_export_file_path(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            scene = bpy.context.scene
            return scene.bfu_export_skeletal_mesh_file_path  # type: ignore[attr-defined]
        return ""

    def get_package_file_type(self, data: bpy.types.Object, details: Any = None) -> BFU_FileTypeEnum:
        return bfu_export_procedure.get_obj_export_file_type(data)

    def get_package_file_name(self, data: bpy.types.Object, details: Optional[bpy.types.Object] = None, desired_name: str = "", without_extension: bool = False) -> str:

        if isinstance(details, bpy.types.Object):

            if bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.modular_mode_is_every_meshs(data):
                asset_name = data.name + str(data.bfu_modular_skeletal_mesh_every_meshs_separate) + details.name # type: ignore[attr-defined]
                return super().get_package_file_name(
                    data,
                    details,
                    desired_name=asset_name,
                    without_extension=without_extension,
                )
            
        if self._is_specified_parts_mesh_item(details):
            if bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.modular_mode_is_specified_parts(data):
                asset_name = details.name
                return super().get_package_file_name(
                    data,
                    details,
                    desired_name=asset_name,
                    without_extension=without_extension,
                )

        return super().get_package_file_name(
            data,
            details,
            desired_name=desired_name,
            without_extension=without_extension,
        )


    def get_asset_folder_path(self, data: bpy.types.Object, details: Optional[BFU_UI_ModularSkeletalSpecifiedPartsMeshItem] = None) -> Path:
        # Add skeletal sub folder path
        if data.bfu_create_sub_folder_with_skeletal_mesh_name:  # type: ignore[attr-defined]
            sub_folder = bfu_basics.valid_file_name(data.name)
            path = Path(sub_folder) / super().get_asset_folder_path(data, details)
        else:
            path = super().get_asset_folder_path(data, details)

        if self._is_specified_parts_mesh_item(details):
            if bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.modular_mode_is_specified_parts(data):
                path /= Path(details.sub_folder)

        return path


# ###################################################################
# # UI
# ###################################################################

    def draw_ui_export_procedure(self, layout: bpy.types.UILayout, context: bpy.types.Context, data: bpy.types.Object) -> bpy.types.UILayout:
        return bfu_export_procedure.draw_object_export_procedure(layout, data)

# ####################################################################
# # Asset Construction
# ####################################################################

    @staticmethod
    def get_valid_childs_meshes(data: bpy.types.Object) -> List[bpy.types.Object]:
        meshes: List[bpy.types.Object] = []
        for obj in bbpl.basics.get_obj_childs(data):
            if bfu_base_object.bfu_base_obj_utils.in_hidden_collection(obj):
                continue  # Skip objects in hidden collections
            if obj.type != "MESH":
                continue
            meshes.append(obj)
        return meshes

    def get_asset_export_data(self, data: bpy.types.Object, details: Any, search_mode: AssetDataSearchMode) -> List[AssetToExport]:

        scene = bpy.context.scene
        if scene is None:
            return []

        asset_list: List[AssetToExport] = []
        
        # Export the armature and all mesh as a single skeletal mesh
        if bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.modular_mode_is_all_in_one(data):
            asset = AssetToExport(self, data.name, AssetType.SKELETAL_MESH)

            asset.set_import_name(self.get_package_file_name(data, without_extension=True))
            asset.set_import_dirpath(self.get_asset_import_directory_path(data))

            if search_mode.search_packages():
                pak = asset.add_asset_package(data.name, ["Lod0"])
                self.set_package_file(pak, data, details)

                if search_mode.search_package_content():
                    pak.add_objects(bfu_base_object.bfu_base_obj_utils.get_exportable_objects(data))
                    pak.export_function = bfu_export_skeletal_mesh_package.process_skeletal_mesh_export_from_package
            
            self.set_additional_data_in_asset(asset, data, details, search_mode)
            asset_list.append(asset)

        # Export each mesh as a separate skeletal mesh
        elif bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.modular_mode_is_every_meshs(data):
            for mesh in self.get_valid_childs_meshes(data):

                asset_name = data.name + str(data.bfu_modular_skeletal_mesh_every_meshs_separate) + mesh.name # type: ignore[attr-defined]
                asset = AssetToExport(self, asset_name, AssetType.SKELETAL_MESH)
                
                import_dirpath = self.get_asset_import_directory_path(data)
                asset.set_import_name(self.get_package_file_name(mesh, without_extension=True))
                asset.set_import_dirpath(import_dirpath)

                if search_mode.search_packages():
                    pak = asset.add_asset_package(mesh.name, ["Lod0"])
                    self.set_package_file(pak, data, mesh) # Send mesh as details.

                    if search_mode.search_package_content():
                        pak.add_object(data) # Add the armature object
                        pak.add_object(mesh)
                        pak.export_function = bfu_export_skeletal_mesh_package.process_skeletal_mesh_export_from_package

                self.set_additional_data_in_asset(asset, data, mesh, search_mode) # Send mesh as details.
                asset_list.append(asset)

        # Export specified parts of the modular skeletal mesh
        elif bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.modular_mode_is_specified_parts(data):
            export_filter: BFU_ExportSelectionFilterEnum = bfu_export_filter.bfu_export_filter_props.scene_export_selection_filter(scene)
            active_part: int = -1
            if export_filter.value == BFU_ExportSelectionFilterEnum.ONLY_OBJECT_AND_ACTIVE.value:
                active_part = data.bfu_modular_skeletal_specified_parts_meshs_template.active_template_property  # type: ignore[attr-defined]

            template = bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.get_modular_skeletal_specified_parts_meshs_template(data)
            for x, part in enumerate(template.get_template_collection()):

                
                should_export = True
                if part.enabled == False:
                    should_export = False
                # Check export filter
                if export_filter.value == BFU_ExportSelectionFilterEnum.ONLY_OBJECT_AND_ACTIVE.value:
                    if x != active_part:
                        should_export = False
                
                if should_export:
                    asset = AssetToExport(self, part.name, AssetType.SKELETAL_MESH)

                    import_dirpath = self.get_asset_import_directory_path(data, extra_path=Path(part.sub_folder))
                    asset.set_import_name(self.get_package_file_name(data, desired_name=part.name, without_extension=True))
                    asset.set_import_dirpath(import_dirpath)

                    if search_mode.search_packages():
                        pak = asset.add_asset_package(data.name, ["Lod0"])
                        self.set_package_file(pak, data, part) # Send part as details.

                        if search_mode.search_package_content():
                            pak.add_object(data) # Add the armature object
                            pak.add_objects(bfu_modular_skeletal_mesh.bfu_modular_skeletal_mesh_utils.get_modular_objects_from_part(part))                    
                            pak.export_function = bfu_export_skeletal_mesh_package.process_skeletal_mesh_export_from_package

                    self.set_additional_data_in_asset(asset, data, part, search_mode) # Send part as details.
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
    my_asset_class = BFU_SkeletalMesh()
    bfu_assets_manager.bfu_asset_manager_registred_assets.register_asset_class(my_asset_class, "Object")

def unregister():
    pass