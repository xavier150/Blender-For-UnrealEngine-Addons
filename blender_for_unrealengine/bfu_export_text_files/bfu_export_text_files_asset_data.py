# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import os
import bpy
from typing import List, Dict, Any, Union, Optional
from . import bfu_export_text_files_utils
from .. import bfu_export_logs
from .. import bfu_utils
from .. import bfu_material
from .. import bfu_nanite
from .. import bfu_light_map
from .. import bfu_assets_references
from .. import bfu_vertex_color
from .. import bfu_lod
from ..bfu_assets_manager.bfu_asset_manager_type import AssetType
from .. import bfu_export_nomenclature

def write_main_assets_data(exported_asset_log: List[bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog]) -> Dict[str, Any]:
    # Generate a script for import assets in Unreal Engine.

    data: Dict[str, Any] = {}

    bfu_export_text_files_utils.add_generated_json_header(data, bpy.app.translations.pgettext("It used for import into Unreal Engine all the assets of type StaticMesh, SkeletalMesh, Animation, Pose, Camera, [...]", "interface.write_text_additional_track_all"))
    bfu_export_text_files_utils.add_generated_json_meta_data(data)

    data['unreal_import_location'] = str(bfu_export_nomenclature.bfu_export_nomenclature_utils.get_import_location())

    # Import assets
    assets: List[Dict[str, Any]] = []
    for unreal_exported_asset in exported_asset_log:
        assets.append(write_single_asset_data(unreal_exported_asset))
    data['assets'] = assets

    bfu_export_text_files_utils.add_generated_json_footer(data)
    return data

def write_single_asset_data(unreal_exported_asset: bfu_export_logs.bfu_asset_export_logs_types.ExportedAssetLog) -> Dict[str, Union[str, bool, float, List[Any]]]:
    asset_data: Dict[str, Any] = {}
    asset_data["scene_unit_scale"] = bfu_utils.get_scene_unit_scale()

    asset_data["asset_name"] = unreal_exported_asset.exported_asset.name
    asset_data["asset_type"] = unreal_exported_asset.exported_asset.asset_type.get_type_as_string()
    asset_data["asset_import_name"] = unreal_exported_asset.exported_asset.import_name
    asset_data["asset_import_path"] = str(unreal_exported_asset.exported_asset.import_dirpath) 
    asset_data["files"] = unreal_exported_asset.exported_asset.get_asset_files_as_data()

    asset_type = unreal_exported_asset.exported_asset.asset_type
    if asset_type in [AssetType.SKELETAL_MESH, AssetType.ANIM_ACTION, AssetType.ANIM_POSE, AssetType.ANIM_NLA]:
        main_armature = unreal_exported_asset.exported_asset.asset_packages[0].objects[0]
        # Skeleton
        asset_data["target_skeleton_search_ref"] = bfu_assets_references.bfu_asset_ref_utils.get_skeleton_search_ref(main_armature)
        # Skeletal Mesh
        asset_data["target_skeletal_mesh_search_ref"] = bfu_assets_references.bfu_asset_ref_utils.get_skeletal_mesh_search_ref(main_armature)

        # Better to seperate to let control to uses but my default it use the Skeleton Search Ref.
        asset_data["target_skeleton_import_ref"] = bfu_assets_references.bfu_asset_ref_utils.get_skeleton_search_ref(main_armature)

        

    if asset_type in [AssetType.ANIM_ACTION, AssetType.ANIM_POSE, AssetType.ANIM_NLA]:
        frame_range = unreal_exported_asset.exported_asset.asset_packages[0].frame_range
        if frame_range:
            asset_data["animation_start_frame"] = frame_range[0]
            asset_data["animation_end_frame"] = frame_range[1]

    main_obj_data: Optional[bpy.types.Object] = None
    
    if asset_type in [AssetType.COLLECTION_AS_STATIC_MESH]:
        pass
        #main_collection = unreal_exported_asset.exported_asset.asset_pakages[0].collection
        #main_obj_data = main_collection
    else:
        main_object = unreal_exported_asset.exported_asset.get_primary_asset_package()
        if main_object:
            if asset_type in [AssetType.STATIC_MESH]:
                asset_data["auto_generate_collision"] = main_object.bfu_auto_generate_collision
                asset_data["collision_trace_flag"] = main_object.bfu_collision_trace_flag

            if asset_type in [AssetType.SKELETAL_MESH]:
                asset_data["create_physics_asset"] = main_object.bfu_create_physics_asset
                asset_data["enable_skeletal_mesh_per_poly_collision"] = main_object.bfu_enable_skeletal_mesh_per_poly_collision

            if asset_type in [AssetType.ANIM_ACTION, AssetType.ANIM_POSE, AssetType.ANIM_NLA]:
                asset_data["do_not_import_curve_with_zero"] = main_object.bfu_do_not_import_curve_with_zero
        main_obj_data = main_object

    if main_obj_data is not None:
        asset_data.update(bfu_lod.bfu_lod_utils.get_lod_asset_data(main_obj_data, asset_type))
        asset_data.update(bfu_vertex_color.bfu_vertex_color_utils.get_vertex_color_asset_data(main_obj_data, asset_type))
        asset_data.update(bfu_material.bfu_material_utils.get_material_asset_data(main_obj_data, asset_type))
        asset_data.update(bfu_light_map.bfu_light_map_utils.get_light_map_asset_data(main_obj_data, asset_type))
        asset_data.update(bfu_nanite.bfu_nanite_utils.get_nanite_asset_data(main_obj_data, asset_type))

    return asset_data