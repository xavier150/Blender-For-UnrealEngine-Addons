# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List, Any, Optional, Dict
from pathlib import Path

from .. import bfu_anim_nla
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType, AssetToExport, AssetDataSearchMode, BFU_ObjectAssetClass
from .. import bfu_basics
from ..bfu_simple_file_type_enum import BFU_FileTypeEnum
from .. import bfu_base_object
from .. import bfu_export_filter
from . import bfu_export_nla_package
from . import bfu_export_procedure
from . import bfu_skeletal_nla_utils




class BFU_SkeletalNonLinearAnimation(BFU_ObjectAssetClass):
    def __init__(self):
        super().__init__()
        self.use_materials = True


# ###################################################################
# # Asset Root Class
# ###################################################################

    def support_asset_type(self, data: Any, details: Any = None) -> bool:
        if not isinstance(data, bpy.types.Object):
            return False
        if data.bfu_export_as_lod_mesh:  # type: ignore[attr-defined]
            return False
        if details is not None:
            return False
        if data.type == "ARMATURE" and bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_use(data):
            return True
        return False

    def get_asset_type(self, data: Any, details: Any = None) -> AssetType:
        return AssetType.ANIM_NLA
            

    def can_export_asset_type(self) -> bool:
        return bfu_export_filter.bfu_export_filter_utils.get_use_animation_export()

    def get_asset_import_directory_path(self, data: Any, details: Any = None, extra_path: Optional[Path] = None) -> Path:
        dirpath = bfu_base_object.bfu_base_obj_utils.get_obj_import_location(data)
        return dirpath if extra_path is None else dirpath / extra_path  # Add extra path if provided

####################################################################
# Asset Package Management
####################################################################

    def get_package_file_prefix(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            return bpy.context.scene.bfu_anim_prefix_export_name  # type: ignore[attr-defined]
        return ""
        
    def get_export_file_path(self, data: Any, details: Any = None) -> str:
        if bpy.context:
            scene = bpy.context.scene
            return scene.bfu_export_skeletal_animation_file_path  # type: ignore[attr-defined]
        return ""

    def get_package_file_type(self, data: bpy.types.Object, details: Any = None) -> BFU_FileTypeEnum:
        return bfu_export_procedure.get_obj_export_file_type(data)

    def get_package_file_name(self, data: bpy.types.Object, details: Any = None, desired_name: str = "", without_extension: bool = False) -> str:
        return super().get_package_file_name(
            data,
            details,
            desired_name=bfu_anim_nla.bfu_anim_nla_props.get_object_anim_nla_export_name(data),
            without_extension=without_extension,
        )

    def get_asset_folder_path(self, data: bpy.types.Object, details: Any = None) -> Path:
        # Add skeletal sub folder path
        if bpy.context:
            scene = bpy.context.scene
            if data.bfu_create_sub_folder_with_skeletal_mesh_name:  # type: ignore[attr-defined]
                sub_folder = bfu_basics.valid_file_name(data.name)
                return Path(sub_folder) / scene.bfu_anim_subfolder_name  # type: ignore[attr-defined]
        return Path()
   
# ###################################################################
# # UI
# ###################################################################

    def draw_ui_export_procedure(self, layout: bpy.types.UILayout, context: bpy.types.Context, data: bpy.types.Object) -> bpy.types.UILayout:
        # Skeletal use the skeletal mesh export procedure.
        return layout

# ####################################################################
# # Asset Construction
# ####################################################################

    def get_asset_export_data(self, data: bpy.types.Object, details: bpy.types.Action, search_mode: AssetDataSearchMode) -> List[AssetToExport]:
                
        asset_list: List[AssetToExport] = []

        # One asset per skeletal mesh.
        asset_name = f"{data.name}_{data.bfu_anim_nla_export_name}"  # type: ignore[attr-defined]
        asset = AssetToExport(self, asset_name, AssetType.ANIM_NLA)
        asset.set_import_name(self.get_package_file_name(data, without_extension=True))
        asset.set_import_dirpath(self.get_asset_import_directory_path(data))

        if search_mode.search_packages():
            pak = asset.add_asset_package(data.bfu_anim_nla_export_name, ["NLA"])  # type: ignore[attr-defined]
            self.set_package_file(pak, data, details)

            if search_mode.search_package_content():
                if data.bfu_export_animation_without_mesh: # type: ignore[attr-defined]
                    pak.add_object(data)
                else:
                    pak.add_objects(bfu_base_object.bfu_base_obj_utils.get_exportable_objects(data))

                frame_range = bfu_skeletal_nla_utils.get_desired_nla_start_end_range(data)
                pak.set_frame_range(frame_range[0], frame_range[1])
                pak.export_function = bfu_export_nla_package.process_nla_animation_export_from_package
                            
        # Set the additional data in the asset, add asset to the list and return the list.
        self.set_additional_data_in_asset(asset, data, details, search_mode)
        asset_list.append(asset)
        return asset_list

    def get_asset_additional_data(self, data: bpy.types.Object, details: Any, search_mode: AssetDataSearchMode) -> Dict[str, Any]:
        additional_data: Dict[str, Any] = {}

        scene = bpy.context.scene
        if scene:
            # Used for set animation sample rate with glTF imports
            additional_data['animation_frame_rate_denominator'] = scene.render.fps_base
            additional_data['animation_frame_rate_numerator'] = scene.render.fps
        return additional_data

# --------------------------------------------
# Register and Unregister functions
# --------------------------------------------

def register():
    my_asset_class = BFU_SkeletalNonLinearAnimation()
    bfu_assets_manager.bfu_asset_manager_registred_assets.register_asset_class(my_asset_class, "ArmatureAnimation")

def unregister():
    pass